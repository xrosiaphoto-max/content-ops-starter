"""キャプション生成（テンプレート + ハッシュタグ）。"""
from __future__ import annotations


def _x_length(text: str) -> int:
    """X の文字数カウント（全角=2, 半角=1 の簡易版。URLは考慮しない）。"""
    return sum(1 if ord(ch) < 0x1100 else 2 for ch in text)


def _truncate_for_x(text: str, limit: int = 280) -> str:
    out = ""
    for ch in text:
        if _x_length(out + ch) > limit - 1:
            return out.rstrip() + "…"
        out += ch
    return out


def build_captions(meta: dict, cfg: dict) -> dict[str, str]:
    cc = cfg["caption"]
    tags = list(dict.fromkeys(meta.get("hashtags", []) + cc["default_hashtags"]))
    tags = [t if t.startswith("#") else f"#{t}" for t in tags][:30]  # Instagram 上限30
    body = meta.get("body", "").strip()
    values = {
        "title": meta.get("title", "").strip(),
        "body": body,
        "body_short": body.split("\n")[0][:80],
        "brand_name": cfg["account"]["brand_name"],
        "hashtags": " ".join(tags),
        "hashtags_short": " ".join(tags[: cc["x_max_hashtags"]]),
    }
    ig = meta.get("caption_instagram") or cc["instagram_template"].format(**values)
    x = meta.get("caption_x") or cc["x_template"].format(**values)
    return {"instagram": ig.strip()[:2200], "x": _truncate_for_x(x.strip())}
