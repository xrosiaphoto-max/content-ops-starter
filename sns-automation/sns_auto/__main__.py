"""コマンドライン入口。

  python -m sns_auto build            # inbox/ の写真セット → リール生成 → アップロード → キュー追加
  python -m sns_auto post             # キューから本日分を Instagram / X に投稿
  python -m sns_auto post --dry-run   # 投稿せず内容だけ確認
  python -m sns_auto status           # キューの状況を表示
  python -m sns_auto refresh-ig-token # Instagram 長期トークンの延長
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

import requests
import yaml

from . import caption, queue, storage
from .config import load_config, resolve
from .reel import build_reel, list_images


def cmd_build(args, cfg) -> int:
    inbox, done = resolve("inbox"), resolve("inbox/_done")
    sets = sorted(p for p in inbox.iterdir() if p.is_dir() and not p.name.startswith("_"))
    if args.set:
        sets = [s for s in sets if s.name == args.set]
    if not sets:
        print("inbox/ に写真セットのフォルダがありません")
        return 0

    items = queue.load(cfg)
    last = max((date.fromisoformat(str(i["not_before"])) for i in items), default=None)
    next_day = max(queue.now(cfg).date(), (last + timedelta(days=1)) if last else date.min)

    for s in sets:
        if not list_images(s, 1):
            print(f"[skip] 画像なし: {s.name}")
            continue
        meta_path = s / "meta.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        meta = meta or {}
        meta.setdefault("title", s.name)
        item_id = f"{next_day.isoformat()}_{s.name}"
        out = resolve("output") / f"{item_id}.mp4"
        print(f"[build] {s.name} → {out.name}")
        build_reel(s, out, cfg, overlay_text=meta.get("overlay_text"))

        video_url = None if args.no_upload else storage.upload(out, cfg)
        if video_url:
            print(f"  uploaded: {video_url}")

        items.append({
            "id": item_id,
            "title": meta["title"],
            "not_before": next_day.isoformat(),
            "video_url": video_url,
            "local_file": str(out.relative_to(resolve("."))),
            "captions": caption.build_captions(meta, cfg),
            "status": {p: "pending" for p in queue.enabled_platforms(cfg)},
            "post_ids": {},
            "errors": {},
        })
        next_day += timedelta(days=1)
        if not args.keep:
            done.mkdir(exist_ok=True)
            shutil.move(str(s), str(done / s.name))

    queue.save(items, cfg)
    print(f"キューに追加しました（合計 {len(items)} 件）")
    return 0


def _local_video(item: dict, tmp: Path) -> Path:
    local = resolve(item["local_file"]) if item.get("local_file") else None
    if local and local.exists():
        return local
    if not item.get("video_url"):
        raise RuntimeError("動画ファイルも公開URLもありません")
    dst = tmp / f"{item['id']}.mp4"
    with requests.get(item["video_url"], stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dst, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    return dst


def cmd_post(args, cfg) -> int:
    from . import instagram, x_client

    items = queue.load(cfg)
    targets = queue.pending(items, cfg)[: cfg["posting"]["posts_per_run"]]
    if not targets:
        print("本日投稿するものはありません（キューを補充してください）")
        return 0

    failed = False
    with tempfile.TemporaryDirectory() as tmp_s:
        for it in targets:
            print(f"[post] {it['id']}")
            for p in queue.enabled_platforms(cfg):
                if it["status"].get(p) == "posted":
                    continue
                if args.dry_run:
                    print(f"  ({p}) DRY-RUN\n---\n{it['captions'][p]}\n---")
                    continue
                try:
                    if p == "instagram":
                        if not it.get("video_url"):
                            raise RuntimeError("Instagram には公開URLが必要です（build 時にアップロードしてください）")
                        pid = instagram.post_reel(it["video_url"], it["captions"]["instagram"], cfg)
                    else:
                        pid = x_client.post_video(_local_video(it, Path(tmp_s)), it["captions"]["x"], cfg)
                    it["status"][p], it["post_ids"][p] = "posted", pid
                    it["errors"].pop(p, None)
                    it.setdefault("posted_at", {})[p] = queue.now(cfg).isoformat(timespec="seconds")
                    print(f"  ({p}) 投稿成功 id={pid}")
                except Exception as e:  # noqa: BLE001 片方の失敗で全体を止めない
                    failed = True
                    it["status"][p] = "error"
                    it["errors"][p] = str(e)[:500]
                    print(f"  ({p}) 失敗: {e}", file=sys.stderr)

    if not args.dry_run:
        queue.save(items, cfg)
    remaining = len(queue.pending(items, cfg)) if not args.dry_run else None
    if remaining is not None and remaining < 3:
        print(f"[warn] 残りストックが {remaining} 件です。撮影素材を補充してください")
    return 1 if failed else 0


def cmd_status(args, cfg) -> int:
    for it in queue.load(cfg):
        st = " ".join(f"{p}:{s}" for p, s in it["status"].items())
        print(f"{it['not_before']}  {it['id']:<40} {st}")
    return 0


def cmd_refresh(args, cfg) -> int:
    from . import instagram
    data = instagram.refresh_token(cfg)
    print(f"新しいトークン（GitHub Secrets の IG_ACCESS_TOKEN を更新）:\n{data['access_token']}")
    print(f"有効期限: {int(data.get('expires_in', 0)) // 86400} 日")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="sns_auto")
    ap.add_argument("--config", help="config.yaml のパス")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--set", help="特定のフォルダだけ処理")
    b.add_argument("--no-upload", action="store_true", help="ストレージへアップロードしない（確認用）")
    b.add_argument("--keep", action="store_true", help="処理後に inbox/_done へ移動しない")
    p = sub.add_parser("post")
    p.add_argument("--dry-run", action="store_true")
    sub.add_parser("status")
    sub.add_parser("refresh-ig-token")
    args = ap.parse_args()
    cfg = load_config(args.config)
    return {"build": cmd_build, "post": cmd_post, "status": cmd_status,
            "refresh-ig-token": cmd_refresh}[args.cmd](args, cfg)


if __name__ == "__main__":
    sys.exit(main())
