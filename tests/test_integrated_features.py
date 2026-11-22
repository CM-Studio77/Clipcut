# --------------------------------------------------------------------------
# ClipCut AI Studio
# Author: CM Studio (https://github.com/CM-Studio77)
# Repository: https://github.com/CM-Studio77/Clipcut
# Copyright (c) 2026 CM Studio. All rights reserved.
# Licensed under Apache License 2.0. See LICENSE for details.
# --------------------------------------------------------------------------
"""Integration test suite for ported features:
- studio/emoji.py (3D Google Noto emoji engine & /api/emoji)
- studio/sfx.py (whoosh & mood sfx engine & /api/sfx)
- studio/romanize.py (Hinglish Romanization engine & /api/romanize)
- studio/virality.py (active speaker detection & retention scoring)
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

tmp_data = tempfile.mkdtemp(prefix="clipcut-test-features-")
os.environ["PEAKCUT_DATA"] = tmp_data
os.environ["DATABASE_URL"] = ""
os.environ["PEAKCUT_ACCOUNTS"] = "0"
os.environ["PEAKCUT_PUBLIC_URL"] = "http://127.0.0.1:8765"

from fastapi.testclient import TestClient  # noqa: E402
from studio import db, emoji, romanize, server, sfx, virality  # noqa: E402

db.init()
c = TestClient(server.app, base_url="http://127.0.0.1:8765")
fails = []


def check(name: str, got, want=True):
    ok = (got == want) if not callable(want) else want(got)
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"   got {got!r}"))
    if not ok:
        fails.append(name)


def main():
    print("\n=== Testing Emoji Engine & API ===")
    check("code('💰') produces '1f4b0'", emoji.code("💰"), "1f4b0")
    check("code_to_char('1f4b0') returns '💰'", emoji.code_to_char("1f4b0"), "💰")
    check("has_emoji detects emoji in string", emoji.has_emoji("Check out this 🚀 launch!"), True)
    check("has_emoji false for plain string", emoji.has_emoji("Plain text with no emoji."), False)
    check("extract_emojis extracts all emojis", emoji.extract_emojis("🔥 Fire and 💯 cool"), ["🔥", "💯"])
    check("clean_emojis removes emojis", emoji.clean_emojis("Clean this 🔥 up"), "Clean this  up")

    r = c.get("/api/emoji?code=1f4b0")
    check("GET /api/emoji returns status 200", r.status_code, 200)
    data = r.json()
    check("GET /api/emoji data contains code", data.get("code"), "1f4b0")

    r_text = c.post("/api/emoji", json={"text": "Trending right now 🚀🔥"})
    check("POST /api/emoji text extraction status 200", r_text.status_code, 200)
    extracted = r_text.json().get("emojis", [])
    check("POST /api/emoji extracted 2 emojis", len(extracted), 2)

    print("\n=== Testing SFX Engine & API ===")
    check("role_of identifies 'whoosh'", sfx.role_of("whoosh-cinematic.mp3"), "whoosh")
    check("role_of identifies 'shock'", sfx.role_of("shock-boom.mp3"), "shock")
    check("role_of identifies 'funny'", sfx.role_of("boing.mp3"), "funny")
    check("role_of with folder parameter", sfx.role_of("random_name.wav", folder="hype"), "hype")

    cat = sfx.scan()
    check("sfx.scan() returns dict with items", isinstance(cat.get("items"), list), True)
    picked = sfx.pick("whoosh")
    check("sfx.pick('whoosh') chooses a sound", picked is not None, True)
    if picked:
        check("sfx.path_of returns existing or valid path", sfx.path_of(picked).name, picked["file"])

    r_sfx = c.get("/api/sfx")
    check("GET /api/sfx returns status 200", r_sfx.status_code, 200)
    check("GET /api/sfx returns moods dict", isinstance(r_sfx.json().get("moods"), dict), True)

    r_pick = c.get("/api/sfx?role=whoosh&pick=true")
    check("GET /api/sfx?pick=true returns picked item", "picked" in r_pick.json(), True)

    print("\n=== Testing Romanization Engine & API ===")
    check("ROMAN_RESPELL maps 'nahin' to 'nahi'", sfx_val := romanize.respelled("nahin"), "nahi")
    check("ROMAN_RESPELL maps 'vahaan' to 'wahan'", romanize.respelled("vahaan"), "wahan")
    check("ROMAN_RESPELL preserves uppercase 'Nahin' -> 'Nahi'", romanize.respelled("Nahin"), "Nahi")
    check("split_word splits punctuation", romanize.split_word('"करेंगे।"'), ('"', 'करेंगे', '।"'))

    words_in = [{"w": "आज", "s": 0.0, "e": 0.4}, {"w": "hum", "s": 0.5, "e": 0.8}, {"w": "vahaan", "s": 0.9, "e": 1.2}]
    words_out, missing = romanize.apply(words_in)
    check("romanize.apply transforms Hindi & Hinglish words", [w["w"] for w in words_out], ["aaj", "hum", "wahan"])

    text_rom = romanize.romanize_text("आज vah vahaan jaega!")
    check("romanize_text converts full sentence", text_rom, "aaj wo wahan jayega!")

    r_rom = c.get("/api/romanize?text=आज+हम+बात+करेंगे")
    check("GET /api/romanize status 200", r_rom.status_code, 200)
    check("GET /api/romanize romanized correctly", r_rom.json().get("romanized"), "aaj hum baat karenge")

    r_post_rom = c.post("/api/romanize", json={"words": words_in})
    check("POST /api/romanize words status 200", r_post_rom.status_code, 200)
    check("POST /api/romanize converted words", [w["w"] for w in r_post_rom.json().get("words", [])], ["aaj", "hum", "wahan"])

    print("\n=== Testing Virality & Retention Heuristics ===")
    low, high = virality.clip_count_targets(5)
    check("clip_count_targets returns realistic range", (low >= 2 and high <= 12), True)

    sl = virality.shortlist_target(300.0)
    check("shortlist_target scales with duration", sl >= 3, True)

    batches = virality.score_batches(list(range(10)), batch_size=4)
    check("score_batches splits into balanced chunks", len(batches), 3)

    pred = virality.predict_retention_score(
        text="This is why you should never make this common mistake in Python. Let me show you what happened.",
        duration_seconds=32.0,
        hook_text="Stop doing this right now!",
    )
    check("predict_retention_score returns predicted_score >= 0", pred["predicted_score"] > 0, True)
    check("predict_retention_score includes hook_score and pacing_score", "hook_score" in pred and "pacing_score" in pred, True)
    check("predict_retention_score gives feedback tips", len(pred.get("feedback", [])) > 0, True)

    r_vir = c.post("/api/virality/score", json={"text": "Here is why this secret changed everything.", "duration": 30.0})
    check("POST /api/virality/score returns 200", r_vir.status_code, 200)
    check("POST /api/virality/score contains predicted_score", "predicted_score" in r_vir.json(), True)

    # Active speaker helpers
    mouth = virality.mouth_region([100, 100, 80, 100], 480, 270)
    check("mouth_region calculates valid bounding box", len(mouth), 4)

    verdicts = [0, 0, None, 1, 1, 1, 0, 0]
    held = virality.hold(verdicts, min_windows=2)
    check("hold filter smooths verdicts without flaps", len(held), len(verdicts))

    is_conv = virality.is_conversation(verdicts, min_share=0.2)
    check("is_conversation checks dual speaker turns", is_conv, True)

    print(f"\nResult: {'ALL PASSED' if not fails else f'{len(fails)} FAILED'}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
