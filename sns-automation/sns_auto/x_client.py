"""X（旧Twitter）への動画付きポスト（API v2 / OAuth 1.0a ユーザーコンテキスト）。

必要な環境変数（X Developer Portal のアプリ画面で取得。アプリ権限は Read and Write）:
  X_API_KEY, X_API_SECRET           … アプリのキー（Consumer Keys）
  X_ACCESS_TOKEN, X_ACCESS_SECRET   … 投稿するアカウントのトークン
"""
from __future__ import annotations

import time
from pathlib import Path

import requests
from requests_oauthlib import OAuth1

from .config import env

CHUNK = 4 * 1024 * 1024  # 4MB


class XError(RuntimeError):
    pass


def _auth() -> OAuth1:
    return OAuth1(env("X_API_KEY"), env("X_API_SECRET"), env("X_ACCESS_TOKEN"), env("X_ACCESS_SECRET"))


def _check(resp: requests.Response) -> dict:
    data = resp.json() if resp.content else {}
    if resp.status_code >= 400 or data.get("errors"):
        raise XError(f"{resp.status_code}: {data}")
    return data


def upload_video(path: Path, cfg: dict, timeout_sec: int = 600) -> str:
    base = cfg["posting"]["x"]["api_base"]
    auth = _auth()
    size = path.stat().st_size

    media_id = _check(requests.post(f"{base}/2/media/upload/initialize", auth=auth, json={
        "media_type": "video/mp4", "total_bytes": size, "media_category": "tweet_video",
    }, timeout=60))["data"]["id"]

    with open(path, "rb") as f:
        idx = 0
        while chunk := f.read(CHUNK):
            _check(requests.post(f"{base}/2/media/upload/{media_id}/append", auth=auth,
                                 data={"segment_index": idx},
                                 files={"media": ("chunk", chunk, "application/octet-stream")},
                                 timeout=120))
            idx += 1

    info = _check(requests.post(f"{base}/2/media/upload/{media_id}/finalize", auth=auth,
                                timeout=60))["data"].get("processing_info")
    deadline = time.time() + timeout_sec
    while info and info.get("state") in ("pending", "in_progress"):
        if time.time() > deadline:
            raise XError("動画処理がタイムアウトしました")
        time.sleep(info.get("check_after_secs", 5))
        info = _check(requests.get(f"{base}/2/media/upload", auth=auth, params={
            "command": "STATUS", "media_id": media_id}, timeout=30))["data"].get("processing_info")
    if info and info.get("state") == "failed":
        raise XError(f"動画処理エラー: {info}")
    return media_id


def post_video(path: Path, text: str, cfg: dict) -> str:
    media_id = upload_video(path, cfg)
    data = _check(requests.post(f"{cfg['posting']['x']['api_base']}/2/tweets", auth=_auth(), json={
        "text": text, "media": {"media_ids": [media_id]}}, timeout=60))
    return data["data"]["id"]
