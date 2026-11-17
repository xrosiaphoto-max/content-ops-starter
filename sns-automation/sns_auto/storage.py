"""動画を S3 互換ストレージ（Cloudflare R2 / AWS S3）へアップロードし公開URLを返す。

Instagram の API は動画ファイルを直接受け取らず「公開URL」から取りに来るため必須。
認証は boto3 標準の環境変数 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY を使う。
"""
from __future__ import annotations

from pathlib import Path

from .config import env


def upload(path: Path, cfg: dict) -> str:
    import boto3

    sc = cfg["storage"]
    bucket = env(sc["bucket_env"])
    endpoint = env(sc["endpoint_env"], required=False)
    base_url = env(sc["public_base_url_env"]).rstrip("/")
    key = f"{sc['prefix']}{path.name}"

    s3 = boto3.client("s3", endpoint_url=endpoint or None)
    s3.upload_file(str(path), bucket, key, ExtraArgs={"ContentType": "video/mp4"})
    return f"{base_url}/{key}"
