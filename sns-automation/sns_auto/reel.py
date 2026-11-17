"""① 写真セットから 9:16 のリール動画を自動生成する（ffmpeg 使用）。

1枚ごとにゆっくり寄る（Ken Burns 風）クリップを作り、クロスフェードでつなぎ、
BGM（無ければ無音トラック）とテロップを付けて Instagram / X の推奨形式で書き出す。
"""
from __future__ import annotations

import random
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

from .config import resolve

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
AUDIO_EXTS = {".mp3", ".m4a", ".aac", ".wav"}
# config の font_path が無いときに探す日本語フォント（Linux / Mac / Windows）
FALLBACK_FONTS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "C:/Windows/Fonts/meiryob.ttc",
    "C:/Windows/Fonts/YuGothB.ttc",
]


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg 失敗:\n{' '.join(cmd)}\n{proc.stderr[-2000:]}")


def list_images(folder: Path, limit: int) -> list[Path]:
    images = sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    return images[:limit]


def _prepare_frame(src: Path, dst: Path, w: int, h: int, bg: str) -> None:
    """EXIF回転を補正し、白背景キャンバス（2倍解像度）の中央に収める。"""
    canvas_w, canvas_h = w * 2, h * 2
    margin = 0.06
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        box_w, box_h = int(canvas_w * (1 - margin * 2)), int(canvas_h * (1 - margin * 2))
        scale = min(box_w / im.width, box_h / im.height)
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        canvas = Image.new("RGB", (canvas_w, canvas_h), ImageColor.getrgb(bg))
        canvas.paste(im, ((canvas_w - im.width) // 2, (canvas_h - im.height) // 2))
        canvas.save(dst, quality=95)


def _make_clip(frame: Path, out: Path, w: int, h: int, fps: int, seconds: float, zoom: float) -> None:
    frames = max(1, round(seconds * fps))
    z = f"1+({zoom - 1:.4f})*on/{frames}"
    vf = (
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={frames}:s={w}x{h}:fps={fps},format=yuv420p"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(frame), "-vf", vf,
          "-frames:v", str(frames), "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", str(out)])


def _make_overlay(text: str, out: Path, w: int, h: int, font_path: Path, size: int) -> None:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = None
    for cand in [font_path, *FALLBACK_FONTS]:
        try:
            font = ImageFont.truetype(str(cand), size)
            break
        except OSError:
            continue
    if font is None:
        print(f"[warn] 日本語フォントが見つかりません: {font_path}")
        font = ImageFont.load_default(size=size)
    lines = text.splitlines() or [text]
    line_h = int(size * 1.35)
    block_h = line_h * len(lines) + size
    top = int(h * 0.72) - block_h // 2
    draw.rectangle([0, top, w, top + block_h], fill=(0, 0, 0, 110))
    y = top + size // 2
    for line in lines:
        tw = draw.textlength(line, font=font)
        draw.text(((w - tw) / 2, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_h
    img.save(out)


def _pick_bgm(bgm_dir: Path) -> Path | None:
    if not bgm_dir.exists():
        return None
    tracks = [p for p in bgm_dir.iterdir() if p.suffix.lower() in AUDIO_EXTS]
    return random.choice(tracks) if tracks else None


def build_reel(image_dir: Path, out_path: Path, cfg: dict, overlay_text: str | None = None,
               bgm: Path | None = None) -> Path:
    rc = cfg["reel"]
    w, h, fps = rc["width"], rc["height"], rc["fps"]
    d, t = float(rc["seconds_per_image"]), float(rc["transition_seconds"])
    images = list_images(image_dir, rc["max_images"])
    if not images:
        raise ValueError(f"画像がありません: {image_dir}")
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg がインストールされていません")

    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        clips = []
        for i, img in enumerate(images):
            frame = tmp / f"frame{i:03d}.jpg"
            clip = tmp / f"clip{i:03d}.mp4"
            _prepare_frame(img, frame, w, h, rc["background"])
            _make_clip(frame, clip, w, h, fps, d, float(rc["zoom"]))
            clips.append(clip)

        n = len(clips)
        total = n * d - (n - 1) * t if n > 1 else d
        inputs: list[str] = []
        for c in clips:
            inputs += ["-i", str(c)]

        # クロスフェードの連結
        filters = []
        last = "[0:v]"
        for k in range(1, n):
            label = f"[v{k}]"
            filters.append(f"{last}[{k}:v]xfade=transition=fade:duration={t}:offset={k * (d - t):.3f}{label}")
            last = label

        idx = n
        # テロップ
        if overlay_text:
            ov = tmp / "overlay.png"
            _make_overlay(overlay_text, ov, w, h, resolve(rc["font_path"]), rc["overlay_font_size"])
            inputs += ["-loop", "1", "-t", f"{total:.3f}", "-i", str(ov)]
            s = float(rc["overlay_seconds"])
            filters.append(f"[{idx}:v]format=rgba,fade=t=out:st={max(0, s - 0.4):.2f}:d=0.4:alpha=1[ovl]")
            filters.append(f"{last}[ovl]overlay=0:0[vo]")
            last = "[vo]"
            idx += 1
        filters.append(f"{last}format=yuv420p[vout]")

        # 音声（BGM か無音。Instagram は音声トラックがある方が安定）
        bgm = bgm or _pick_bgm(resolve(rc["bgm_dir"]))
        if bgm:
            inputs += ["-i", str(bgm)]
            fade_st = max(0.0, total - 1.5)
            filters.append(f"[{idx}:a]atrim=0:{total:.3f},volume={rc['bgm_volume']},"
                           f"afade=t=out:st={fade_st:.2f}:d=1.5,aresample=48000[aout]")
        else:
            inputs += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
            filters.append(f"[{idx}:a]anull[aout]")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        _run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
              "-filter_complex", ";".join(filters),
              "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
              "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "20",
              "-maxrate", "8M", "-bufsize", "16M", "-r", str(fps), "-pix_fmt", "yuv420p",
              "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
              "-movflags", "+faststart", str(out_path)])
    return out_path
