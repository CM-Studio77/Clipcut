"""Sound effects engine: built-in whooshes & clicks, plus user sounds sorted by mood.

Mood categories:
- shock: deep boom, bass drop, "dun dun"
- attention: riser, ding, notification, alert bell
- fear: suspense sting, horror hit, creepy drone
- funny: boing, cartoon honk, record scratch, "bruh"
- sad: soft piano / violin sting
- hype: air horn, crowd cheer, wow
- reveal: ta-da, magic sparkle, success chime
- fail: wrong buzzer, sad trombone, error sound
- money: cash register, coin drop

Built-in roles: whoosh (zooms/cuts), hit (impacts), click (subtle pops).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np

from . import config

SFX_DIR = config.ROOT / "assets" / "sfx"
MINE = config.DATA_DIR / "sounds"
CATALOG = MINE / ".catalog.json"
SR = 48000
EXTS = (".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac")

ROLES = {
    "whoosh": ("whoosh", "swoosh", "swish", "swipe"),
    "hit": ("hit", "impact", "punch", "thud"),
    "click": ("click", "pop", "tick"),
}

MOODS = {
    "attention": (("attention", "riser", "ding", "notif", "alert", "bell"),
                  "grab attention: a riser, a ding, a notification"),
    "shock": (("shock", "boom", "vine", "bass", "drop", "dun"),
              "a shocking line or reveal: a deep boom, bass drop, 'dun dun'"),
    "fear": (("fear", "horror", "scary", "creepy", "suspense", "tension", "drone"),
             "something scary or tense: suspense sting, horror hit"),
    "funny": (("funny", "boing", "cartoon", "honk", "bruh", "scratch", "laugh"),
              "a punchline or awkward moment: boing, record scratch, 'bruh'"),
    "sad": (("sad", "violin", "emotional", "sorrow"),
            "a sad or emotional moment: soft piano or violin sting"),
    "hype": (("hype", "airhorn", "cheer", "crowd", "wow"),
             "a big win or hype: air horn, crowd cheer"),
    "reveal": (("reveal", "tada", "magic", "sparkle", "success"),
               "an answer or result: ta-da, sparkle"),
    "fail": (("fail", "wrong", "buzzer", "trombone", "error"),
             "a mistake or fail: wrong buzzer, sad trombone"),
    "money": (("money", "cash", "coin", "ching", "register"),
              "money talk: cash register, coins"),
}

GAIN = {
    "shock": -11,
    "funny": -12,
    "fail": -12,
    "money": -12,
    "hype": -13,
    "attention": -14,
    "reveal": -14,
    "fear": -15,
    "sad": -16,
}
MAX_LEN = 2.5


def _load_json(p: Path, default=None):
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def role_of(name: str, folder: str | None = None) -> str | None:
    """The role or mood of a sound: its folder name, else matching keyword in file name."""
    if folder:
        return folder.lower()
    n = name.lower()
    for role, (keys, _) in MOODS.items():
        if any(k in n for k in keys):
            return role
    for role, keys in ROLES.items():
        if any(k in n for k in keys):
            return role
    return None


def decode(path: Path | str) -> np.ndarray:
    """Decode audio file to 48kHz mono float32 array using ffmpeg."""
    try:
        r = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
            capture_output=True, timeout=60,
        )
        if r.returncode != 0 or not r.stdout:
            return np.zeros(0, dtype=np.float32)
        return np.frombuffer(r.stdout, dtype=np.float32)
    except Exception:
        return np.zeros(0, dtype=np.float32)


def segments(x: np.ndarray, floor_db: float = -42, min_gap: float = 0.25, min_len: float = 0.15):
    """Split a sound pack into separate sound events at silences: [(start, end, peak)] in seconds."""
    hop = SR // 100
    n = len(x) // hop
    if n == 0:
        return []
    rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms / (rms.max() + 1e-12))
    on = db > floor_db
    segs, i = [], 0
    while i < n:
        if not on[i]:
            i += 1
            continue
        j = i
        quiet = 0
        while j < n and quiet < min_gap * 100:
            quiet = quiet + 1 if not on[j] else 0
            j += 1
        end = j - quiet
        if (end - i) / 100 >= min_len:
            pk = i + int(np.argmax(rms[i:end]))
            segs.append((i / 100, end / 100, pk / 100))
        i = j
    return segs


def files() -> list[tuple[Path, str | None]]:
    """[(path, folder or None)] of every sound: built-in first, then user's custom sounds."""
    out: list[tuple[Path, str | None]] = []
    if SFX_DIR.exists():
        out += [(p, None) for p in sorted(SFX_DIR.glob("*")) if p.suffix.lower() in EXTS]
    if MINE.exists():
        out += [(p, None) for p in sorted(MINE.glob("*")) if p.suffix.lower() in EXTS]
        for d in sorted(x for x in MINE.iterdir() if x.is_dir() and not x.name.startswith(".")):
            out += [(p, d.name) for p in sorted(d.rglob("*")) if p.suffix.lower() in EXTS]
    return out


def scan() -> dict:
    """Catalog all sounds, detecting cues, peak amplitudes, and gain normalizations."""
    found = files()
    sig = [[str(p), p.stat().st_size] for p, _ in found if p.exists()]
    cat = _load_json(CATALOG)
    if cat and cat.get("sig") == sig:
        return cat

    items = []
    for p, folder in found:
        if not p.exists():
            continue
        role = role_of(p.stem, folder)
        if not role:
            continue
        x = decode(p)
        if len(x) == 0:
            continue
        segs = segments(x) if folder is None and role in ROLES else [(0.0, len(x) / SR, None)]
        for k, (a, b, pk) in enumerate(segs[:12]):
            part = x[int(a * SR):int(b * SR)]
            if not len(part):
                continue
            amp = float(np.abs(part).max() or 1e-6)
            if pk is None:
                pk = a + int(np.argmax(np.abs(part))) / SR
            try:
                rel = str(p.relative_to(config.ROOT))
            except ValueError:
                rel = str(p)
            items.append({
                "file": p.name,
                "path": rel,
                "role": role,
                "variant": k,
                "start": round(a, 2),
                "length": round(b - a, 2),
                "peak": round(pk - a, 2),
                "norm_db": round(-20 * np.log10(amp), 2),
            })
    cat = {"sig": sig, "items": items}
    MINE.mkdir(parents=True, exist_ok=True)
    _save_json(CATALOG, cat)
    return cat


def pick(role: str, prefer_len: float | None = None, exclude: tuple = (), salt: str = "") -> dict | None:
    """Choose a sound matching role/mood. `salt` (e.g. clip id/title) distributes choices."""
    items = [i for i in scan()["items"] if i["role"] == role and (i["file"], i["variant"]) not in exclude]
    if not items:
        return None
    if prefer_len:
        items.sort(key=lambda i: abs(i["length"] - prefer_len))
        return items[0]
    idx = int(hashlib.md5(salt.encode()).hexdigest(), 16) % len(items)
    return items[idx]


def path_of(cue: dict) -> Path:
    """Get absolute Path for a sound cue dict."""
    p_str = cue.get("path")
    if p_str:
        p = Path(p_str)
        if p.is_absolute():
            return p
        return config.ROOT / p
    return SFX_DIR / cue.get("file", "")


def moods_available() -> dict[str, int]:
    """{mood: count} for all available sounds, including built-in and user mood folders."""
    out = {}
    for it in scan()["items"]:
        r = it["role"]
        out[r] = out.get(r, 0) + 1
    return out


def make_folders():
    """Create initial mood folders in user's sounds directory."""
    MINE.mkdir(parents=True, exist_ok=True)
    for m in MOODS:
        (MINE / m).mkdir(exist_ok=True)


def add_sound(src_path: str | Path, mood: str) -> dict:
    """Add a sound file or directory of sounds to a mood folder."""
    src = Path(src_path).expanduser().resolve()
    mood = mood.strip().lower()
    if not mood:
        raise ValueError("Mood name cannot be empty")
    dest_dir = MINE / mood
    dest_dir.mkdir(parents=True, exist_ok=True)
    added = []

    to_copy = []
    if src.is_dir():
        to_copy = [p for p in src.rglob("*") if p.suffix.lower() in EXTS]
    elif src.is_file() and src.suffix.lower() in EXTS:
        to_copy = [src]
    else:
        raise ValueError(f"File not found or unsupported audio format: {src}")

    for p in to_copy:
        target = dest_dir / p.name
        shutil.copy2(p, target)
        added.append(p.name)

    # Invalidate catalog
    if CATALOG.exists():
        try:
            CATALOG.unlink()
        except OSError:
            pass

    return {"mood": mood, "added": added, "count": len(added)}


def remove_sound(filename: str) -> bool:
    """Remove a sound from user's sounds directory by filename."""
    found = False
    for p, folder in files():
        if folder and p.name == filename:
            try:
                p.unlink()
                found = True
            except OSError:
                pass
    if found and CATALOG.exists():
        try:
            CATALOG.unlink()
        except OSError:
            pass
    return found
