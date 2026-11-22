# --------------------------------------------------------------------------
# ClipCut AI Studio
# Author: CM Studio (https://github.com/CM-Studio77)
# Repository: https://github.com/CM-Studio77/Clipcut
# Copyright (c) 2026 CM Studio. All rights reserved.
# Licensed under Apache License 2.0. See LICENSE for details.
# --------------------------------------------------------------------------
"""Emoji pictures for captions and clips: Google's Noto emoji (3D style, OFL / Apache 2.0).

Only the emojis a clip uses are downloaded, once, and cached in data/cache/emoji/.
Captions can't draw colour emojis directly (standard subtitle fonts lack colour emoji support),
so the edit places the 3D emoji image above the caption line or inline when its word is spoken.
"""
from __future__ import annotations

import base64
import re
import urllib.request
from pathlib import Path

from . import config

CACHE = config.DATA_DIR / "cache" / "emoji"
SOURCES = [
    "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/3D/png/512/emoji_u{code}.png",
    "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/2D/png/512/emoji_u{code}.png",
]

# Regex covering standard Unicode emoji characters
_EMOJI_PATTERN = re.compile(
    r"["
    r"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    r"\U0001F300-\U0001F5FF"  # symbols & pictographs
    r"\U0001F600-\U0001F64F"  # emoticons
    r"\U0001F680-\U0001F6FF"  # transport & map symbols
    r"\U0001F700-\U0001F77F"  # alchemical symbols
    r"\U0001F780-\U0001F7FF"  # geometric shapes extended
    r"\U0001F800-\U0001F8FF"  # supplemental arrows-C
    r"\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
    r"\U0001FA00-\U0001FA6F"  # chess symbols, symbols and pictographs extended-A
    r"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-B
    r"\u2600-\u26FF"          # misc symbols
    r"\u2700-\u27BF"          # dingbats
    r"\u2300-\u23FF"          # misc technical
    r"\u2B50\u2B55"          # stars / circle
    r"]",
    flags=re.UNICODE,
)


def code(ch: str) -> str:
    """'💰' -> '1f4b0' (variation selectors left out, matching Noto Emoji filenames)."""
    if not ch:
        return ""
    return "_".join(f"{ord(c):x}" for c in ch.strip() if ord(c) not in (0xFE0E, 0xFE0F))


def code_to_char(c: str) -> str:
    """'1f4b0' -> '💰'."""
    try:
        parts = c.strip().split("_")
        return "".join(chr(int(p, 16)) for p in parts if p)
    except Exception:
        return ""


def png(ch: str, timeout: float = 10.0) -> Path | None:
    """The picture file of an emoji, downloaded the first time; None when unavailable (offline)."""
    c = code(ch)
    if not c:
        return None
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"emoji_u{c}.png"
    if path.exists() and path.stat().st_size > 500:
        return path

    for url_tmpl in SOURCES:
        url = url_tmpl.format(code=c)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ClipCut/1.0 (NotoEmoji)"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
            if data[:8] == b"\x89PNG\r\n\x1a\n":
                path.write_bytes(data)
                return path
        except Exception:
            continue
    return None


def has_emoji(text: str) -> bool:
    """Check if text contains any emoji character."""
    return bool(_EMOJI_PATTERN.search(text or ""))


def extract_emojis(text: str) -> list[str]:
    """Return all unique emoji characters found in text, in order of appearance."""
    matches = _EMOJI_PATTERN.findall(text or "")
    seen = set()
    out = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def find_emojis(text: str) -> list[dict]:
    """Find emojis with their positions and cached status."""
    res = []
    for m in _EMOJI_PATTERN.finditer(text or ""):
        char = m.group(0)
        c = code(char)
        cached_file = CACHE / f"emoji_u{c}.png" if c else None
        res.append({
            "char": char,
            "code": c,
            "start": m.start(),
            "end": m.end(),
            "cached": bool(cached_file and cached_file.exists()),
        })
    return res


def emoji_data_uri(ch: str) -> str | None:
    """Return data:image/png;base64,... URI for the emoji, or None."""
    p = png(ch)
    if not p or not p.exists():
        return None
    try:
        raw = p.read_bytes()
        return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")
    except Exception:
        return None


def clean_emojis(text: str) -> str:
    """Remove emoji characters from text."""
    return _EMOJI_PATTERN.sub("", text or "").strip()
