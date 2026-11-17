"""Instagram リール投稿（Instagram API with Instagram Login / Content Publishing）。

必要な環境変数:
  IG_USER_ID       … Instagram のプロアカウントのユーザーID
  IG_ACCESS_TOKEN  … 長期アクセストークン（60日有効。refresh_token() で延長）
必要な権限: instagram_business_basic, instagram_business_content_publish
"""
from __future__ import annotations

import time

import requests

from .config import env


class InstagramError(RuntimeError):
    pass


def _base(cfg: dict) -> str:
    ic = cfg["posting"]["instagram"]
    return f"{ic['api_base']}/{ic['api_version']}"


def _check(resp: requests.Response) -> dict:
    data = resp.json() if resp.content else {}
    if resp.status_code >= 400 or "error" in data:
        raise InstagramError(f"{resp.status_code}: {data.get('error', data)}")
    return data


def post_reel(video_url: str, caption: str, cfg: dict, timeout_sec: int = 600) -> str:
    """動画の公開URLからリールを投稿し、メディアIDを返す。"""
    user_id, token = env("IG_USER_ID"), env("IG_ACCESS_TOKEN")
    base = _base(cfg)

    # 1) コンテナ作成
    container = _check(requests.post(f"{base}/{user_id}/media", data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": str(cfg["posting"]["instagram"]["share_to_feed"]).lower(),
        "access_token": token,
    }, timeout=60))["id"]

    # 2) Instagram 側の動画処理完了を待つ
    deadline = time.time() + timeout_sec
    while True:
        st = _check(requests.get(f"{base}/{container}", params={
            "fields": "status_code,status", "access_token": token}, timeout=30))
        code = st.get("status_code")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise InstagramError(f"動画処理エラー: {st}")
        if time.time() > deadline:
            raise InstagramError(f"動画処理がタイムアウトしました: {st}")
        time.sleep(10)

    # 3) 公開
    return _check(requests.post(f"{base}/{user_id}/media_publish", data={
        "creation_id": container, "access_token": token}, timeout=60))["id"]


def refresh_token(cfg: dict) -> dict:
    """長期トークンを延長（発行から24時間以上経過・期限切れ前のみ有効）。"""
    resp = requests.get(f"{cfg['posting']['instagram']['api_base']}/refresh_access_token", params={
        "grant_type": "ig_refresh_token", "access_token": env("IG_ACCESS_TOKEN")}, timeout=30)
    return _check(resp)
