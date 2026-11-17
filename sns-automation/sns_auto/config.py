"""設定ファイルと環境変数の読み込み。"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str | os.PathLike | None = None) -> dict:
    cfg_path = Path(path) if path else ROOT / "config.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve(rel: str) -> Path:
    """config 内の相対パスを sns-automation/ 基準で解決する。"""
    p = Path(rel)
    return p if p.is_absolute() else ROOT / p


def env(name: str, required: bool = True) -> str | None:
    value = os.environ.get(name)
    if required and not value:
        raise RuntimeError(f"環境変数 {name} が設定されていません")
    return value
