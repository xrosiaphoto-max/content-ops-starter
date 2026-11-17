"""投稿キュー（queue.yaml）の読み書き。

各アイテムはプラットフォームごとに status を持つので、
片方だけ失敗しても次回はその片方だけ再投稿される（二重投稿しない）。
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import yaml

from .config import resolve

PLATFORMS = ("instagram", "x")


def load(cfg: dict) -> list[dict]:
    path = resolve(cfg["posting"]["queue_file"])
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def save(items: list[dict], cfg: dict) -> None:
    path = resolve(cfg["posting"]["queue_file"])
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(items, f, allow_unicode=True, sort_keys=False, width=1000)


def now(cfg: dict) -> datetime:
    return datetime.now(ZoneInfo(cfg["account"]["timezone"]))


def enabled_platforms(cfg: dict) -> list[str]:
    return [p for p in PLATFORMS if cfg["posting"][p]["enabled"]]


def pending(items: list[dict], cfg: dict) -> list[dict]:
    """投稿待ち（未投稿プラットフォームがあり、予定日を過ぎている）を古い順で返す。"""
    today = now(cfg).date().isoformat()
    out = []
    for it in items:
        if str(it.get("not_before", "")) > today:
            continue
        if any(it["status"].get(p) != "posted" for p in enabled_platforms(cfg)):
            out.append(it)
    return out
