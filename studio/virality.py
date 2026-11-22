# --------------------------------------------------------------------------
# ClipCut AI Studio
# Author: CM Studio (https://github.com/CM-Studio77)
# Repository: https://github.com/CM-Studio77/Clipcut
# Copyright (c) 2026 CM Studio. All rights reserved.
# Licensed under Apache License 2.0. See LICENSE for details.
# --------------------------------------------------------------------------
"""Retention scoring and active speaker detection heuristics.
Ported from openshorts and enhanced for ClipCut.

Features:
1. Active Speaker Detection:
   - Mouth-motion analysis across audio windows to detect who is speaking in two-shots / split layouts
   - Audio envelope gating (speech vs. room silence)
   - Margin-based speaker attribution and smoothing (hold filter)
2. Retention & Virality Scoring:
   - Transcript window segmentation with Whisper segment alignment
   - Word-boundary snapping for clean cuts (preventing cut-off words)
   - Overlap deduplication
   - Algorithmic virality & retention prediction (hook strength, pacing, length sweet-spot, engagement)
"""
from __future__ import annotations

import math
import os
import re
import subprocess
from pathlib import Path

import numpy as np

# =====================================================================
# Active Speaker Detection Heuristics
# =====================================================================

WINDOW_SECONDS = 0.4
AUDIO_FLOOR = 0.18
MIN_MARGIN = 0.15
MIN_SHARE = float(os.environ.get("SPLIT_MIN_SHARE", "0.2"))
ANALYSIS_WIDTH = 480


def mouth_region(box: list[float] | tuple[float, ...], frame_w: int, frame_h: int, scale: float = 1.0) -> tuple[int, int, int, int]:
    """Pixel rect (x0, y0, x1, y1) around the mouth of a face box [x, y, w, h]."""
    x, y, w, h = [v / scale for v in box]
    cx = x + w / 2.0
    mouth_y = y + h * 0.72
    half_w = w * 0.36
    half_h = h * 0.22

    x0 = int(max(0, min(cx - half_w, frame_w - 1)))
    x1 = int(max(x0 + 1, min(cx + half_w, frame_w)))
    y0 = int(max(0, min(mouth_y - half_h, frame_h - 1)))
    y1 = int(max(y0 + 1, min(mouth_y + half_h, frame_h)))
    return x0, y0, x1, y1


def audio_envelope(video_path: str | Path, start_s: float, duration_s: float, window_s: float = WINDOW_SECONDS) -> list[float]:
    """Per-window RMS of the clip's audio, normalised to peak [0.0 - 1.0]."""
    try:
        raw = subprocess.run(
            [
                "ffmpeg", "-v", "error", "-ss", f"{start_s:.4f}",
                "-t", f"{duration_s:.4f}", "-i", str(video_path),
                "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-",
            ],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=120,
        ).stdout
    except Exception:
        return []
    if not raw:
        return []

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    per_window = max(1, int(8000 * window_s))
    n = len(samples) // per_window
    if n < 1:
        return []

    windows = samples[:n * per_window].reshape(n, per_window)
    rms = np.sqrt(np.mean(windows ** 2, axis=1))
    peak = rms.max()
    return (rms / peak).tolist() if peak > 0 else [0.0] * n


def normalise_activity(activity: list[list[float]]) -> list[list[float]]:
    """Rescale each speaker's mouth activity onto its own quiet-to-loud range."""
    if not activity:
        return []
    columns = np.asarray(activity, dtype=float)
    if columns.ndim != 2 or columns.shape[1] < 2:
        return activity

    low = np.percentile(columns, 20, axis=0)
    high = np.percentile(columns, 80, axis=0)
    spread = np.where(high - low > 1e-6, high - low, 1.0)
    return np.clip((columns - low) / spread, 0.0, None).tolist()


def attribute_windows(activity: list[list[float]], loudness: list[float], min_margin: float = MIN_MARGIN) -> list[int | None]:
    """Determine which speaker owns each window: 0, 1, or None if ambiguous/silent."""
    verdicts: list[int | None] = []
    for i, pair in enumerate(activity):
        if loudness and i < len(loudness) and loudness[i] < AUDIO_FLOOR:
            verdicts.append(None)
            continue
        if len(pair) < 2:
            verdicts.append(0 if pair else None)
            continue
        a, b = pair[0], pair[1]
        total = a + b
        if total <= 0:
            verdicts.append(None)
            continue
        margin = abs(a - b) / total
        verdicts.append(None if margin < min_margin else (0 if a > b else 1))
    return verdicts


def shares(verdicts: list[int | None]) -> tuple[float, float]:
    """Fraction of attributed windows held by each speaker (share0, share1)."""
    counted = [v for v in verdicts if v is not None]
    if not counted:
        return 0.0, 0.0
    n = float(len(counted))
    return counted.count(0) / n, counted.count(1) / n


def is_conversation(verdicts: list[int | None], min_share: float | None = None) -> bool:
    """True when both speakers hold at least min_share of speaking turns."""
    ms = MIN_SHARE if min_share is None else min_share
    a, b = shares(verdicts)
    return min(a, b) >= ms


def hold(verdicts: list[int | None], min_windows: int = 3) -> list[int | None]:
    """Smooth window verdicts so speaker switching doesn't flap rapidly."""
    out: list[int | None] = []
    current = None
    pending = None
    run = 0
    for v in verdicts:
        if v is None or v == current:
            if v == current:
                pending, run = None, 0
            out.append(current)
            continue
        if v == pending:
            run += 1
        else:
            pending, run = v, 1
        if current is None or run >= min_windows:
            current, pending, run = v, None, 0
        out.append(current)

    if all(v is None for v in out):
        return out
    first = next(v for v in out if v is not None)
    return [first if v is None else v for v in out]


def speaker_xs(held: list[int | None], centres: list[list[float]], crop_w: int, orig_w: int, n_frames: int, fps: float, window_s: float = WINDOW_SECONDS) -> list[int]:
    """Per-frame horizontal crop coordinates that track the active speaker."""
    xs: list[int] = []
    for f in range(n_frames):
        idx = min(int((f / fps) / window_s), len(held) - 1) if held else 0
        who = held[idx] if held else 0
        who_idx = who if who is not None and who < len(centres) else 0
        cx = centres[who_idx][0]
        x = int(round(cx - crop_w / 2.0))
        xs.append(max(0, min(x, orig_w - crop_w)))
    return xs


def decode_activity(video_path: str | Path, start_s: float, duration_s: float, boxes: list, fps: float, window_s: float = WINDOW_SECONDS) -> list[list[float]]:
    """Decode scene at low resolution and measure mean absolute frame differences in mouth boxes."""
    try:
        import cv2
        probe = cv2.VideoCapture(str(video_path))
        orig_w = int(probe.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_h = int(probe.get(cv2.CAP_PROP_FRAME_HEIGHT))
        probe.release()
    except Exception:
        orig_w, orig_h = 1920, 1080

    if not orig_w or not orig_h:
        return []

    small_w = min(ANALYSIS_WIDTH, orig_w)
    small_w -= small_w % 2
    small_h = max(int(orig_h * small_w / orig_w), 2)
    small_h += small_h % 2
    scale = orig_w / float(small_w)

    regions = [mouth_region(b, small_w, small_h, scale) for b in boxes]
    try:
        proc = subprocess.Popen(
            [
                "ffmpeg", "-v", "error", "-ss", f"{start_s:.4f}",
                "-t", f"{duration_s:.4f}", "-i", str(video_path),
                "-vf", f"scale={small_w}:{small_h}", "-f", "rawvideo",
                "-pix_fmt", "gray", "-",
            ],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            bufsize=small_w * small_h * 4,
        )
    except Exception:
        return []

    per_window = max(1, int(round(fps * window_s)))
    activity: list[list[float]] = []
    bucket: list[list[float]] = []
    prev: np.ndarray | None = None

    try:
        while True:
            buf = proc.stdout.read(small_w * small_h)
            if len(buf) < small_w * small_h:
                break
            frame = np.frombuffer(buf, dtype=np.uint8).reshape(small_h, small_w)
            if prev is not None:
                diffs = [
                    float(np.mean(np.abs(frame[y0:y1, x0:x1].astype(np.int16) - prev[y0:y1, x0:x1].astype(np.int16))))
                    for x0, y0, x1, y1 in regions
                ]
                bucket.append(diffs)
            prev = frame
            if len(bucket) >= per_window:
                activity.append(np.mean(bucket, axis=0).tolist())
                bucket = []
    finally:
        if proc.stdout:
            proc.stdout.close()
        proc.wait()

    if bucket:
        activity.append(np.mean(bucket, axis=0).tolist())
    return activity


# =====================================================================
# Retention & Virality Scoring Heuristics
# =====================================================================

def clip_count_targets(n_windows: int) -> tuple[int, int]:
    """Target min and max number of clips to select given candidate window count."""
    n = max(1, int(n_windows or 1))
    low = max(2, min(6, n // 2 + 2))
    high = min(12, max(4, n * 2))
    low = min(low, high)
    return low, high


def shortlist_target(video_duration: float) -> int:
    """Number of candidate windows to detail-score based on source video duration."""
    try:
        seconds = float(video_duration or 0)
    except (TypeError, ValueError):
        seconds = 0.0
    return max(3, min(10, int(seconds // 90) + 2))


def score_batches(windows: list, batch_size: int = 8) -> list[list]:
    """Split windows into balanced, near-equal batches."""
    n = len(windows)
    if not n:
        return []
    size = max(1, int(batch_size or 1))
    n_batches = max(1, -(-n // size))
    base, extra = divmod(n, n_batches)

    out = []
    start = 0
    for idx in range(n_batches):
        take = base + (1 if idx < extra else 0)
        batch = windows[start:start + take]
        start += take
        if batch:
            out.append(batch)
    return out


def trim_to_best(shorts: list[dict], max_clips: int) -> list[dict]:
    """Trim candidate clips down to max_clips by predicted_score, preserving order."""
    max_clips = max(1, int(max_clips or 1))
    if len(shorts) <= max_clips:
        return list(shorts)

    def score(item):
        try:
            return float(item.get("predicted_score") or item.get("score") or 0)
        except Exception:
            return 0.0

    indexed = list(enumerate(shorts))
    best = sorted(indexed, key=lambda p: score(p[1]), reverse=True)[:max_clips]
    return [item for _, item in sorted(best, key=lambda pair: pair[0])]


def build_transcript_windows(transcript_result: dict, video_duration: float, window_seconds: float = 90.0, overlap_seconds: float = 30.0) -> list[dict]:
    """Build scoring windows aligned to Whisper speech segment boundaries."""
    segments = []
    for segment in transcript_result.get("segments", []):
        text = str(segment.get("text") or "").strip()
        if not text:
            continue
        segments.append((float(segment.get("start", 0)), float(segment.get("end", 0)), text))

    windows = []
    window_index = 1
    i = 0
    n = len(segments)
    while i < n:
        w_start = segments[i][0]
        j = i
        while j + 1 < n and segments[j + 1][1] - w_start <= window_seconds * 1.25:
            j += 1
            if segments[j][1] - w_start >= window_seconds:
                break
        w_end = segments[j][1]
        windows.append({
            "id": f"window_{window_index:03d}",
            "start": round(w_start, 3),
            "end": round(w_end, 3),
            "text": " ".join(seg[2] for seg in segments[i:j + 1]),
        })
        window_index += 1
        if j >= n - 1:
            break
        target = w_end - overlap_seconds
        k = i + 1
        while k <= j and segments[k][0] < target:
            k += 1
        i = max(k, i + 1)

    if not windows:
        windows.append({
            "id": "window_001",
            "start": 0.0,
            "end": round(float(video_duration), 3),
            "text": str(transcript_result.get("text", "") or ""),
        })
    return windows


def dedupe_overlapping(shorts: list[dict], ratio: float = 0.25) -> list[dict]:
    """Drop clips that overlap an earlier kept clip by >= ratio of the shorter clip."""
    def _score(c):
        try:
            return float(c.get("predicted_score") or c.get("score") or 0)
        except Exception:
            return 0.0

    def _span(c):
        try:
            return float(c.get("start", 0)), float(c.get("end", 0))
        except Exception:
            return 0.0, 0.0

    indexed = list(enumerate(shorts))
    kept: list[tuple[int, dict]] = []
    for idx, clip in sorted(indexed, key=lambda p: (-_score(p[1]), p[0])):
        s, e = _span(clip)
        clash = False
        for _, other in kept:
            os_, oe = _span(other)
            overlap = min(e, oe) - max(s, os_)
            shorter = max(1e-6, min(e - s, oe - os_))
            if overlap > 0 and overlap / shorter >= ratio:
                clash = True
                break
        if not clash:
            kept.append((idx, clip))
    return [c for _, c in sorted(kept, key=lambda p: p[0])]


def snap_clip_to_words(
    start: float,
    end: float,
    words: list[dict],
    video_duration: float,
    min_duration: float = 15.0,
    max_duration: float = 60.0,
    search_window: float = 1.5,
    max_lead: float = 0.35,
    max_tail: float = 0.45,
) -> tuple[float, float]:
    """Snap proposed clip boundaries onto real word timestamps and surrounding silence."""
    original = (round(float(start), 3), round(float(end), 3))
    if not words:
        return original

    starts = [float(w.get("s", 0)) for w in words]
    ends = [float(w.get("e", 0)) for w in words]

    new_start = float(start)
    candidates_s = [s for s in starts if abs(s - new_start) <= search_window]
    if candidates_s:
        word_start = min(candidates_s, key=lambda s: abs(s - new_start))
        prev_ends = [e for e in ends if e <= word_start]
        lead = min(max_lead, max(0.0, word_start - max(prev_ends)) / 2) if prev_ends else max_lead
        new_start = max(0.0, word_start - lead)

    new_end = float(end)
    candidates_e = [e for e in ends if abs(e - new_end) <= search_window]
    if candidates_e:
        word_end = min(candidates_e, key=lambda e: abs(e - new_end))
        next_starts = [s for s in starts if s >= word_end]
        tail = min(max_tail, max(0.0, min(next_starts) - word_end) / 2) if next_starts else max_tail
        new_end = min(float(video_duration), word_end + tail)

    if new_end - new_start < min_duration:
        target = new_start + min_duration
        later = sorted(e for e in ends if e >= target)
        if later and later[0] - new_start <= max_duration:
            new_end = min(float(video_duration), later[0] + 0.2)
        else:
            return original

    if new_end - new_start > max_duration:
        target = new_start + max_duration
        earlier = [e for e in ends if new_start < e <= target]
        new_end = (max(earlier) + 0.2) if earlier else target
        new_end = min(new_end, new_start + max_duration, float(video_duration))

    if new_end <= new_start or new_end - new_start < min_duration:
        return original
    return (round(new_start, 3), round(new_end, 3))


# High-retention hook and curiosity triggers
_HOOK_PATTERNS = [
    re.compile(r"\b(why|how|what if|here is why|the truth about|never|secret|nobody talks about|insane|crazy)\b", re.I),
    re.compile(r"\b(wait until|watch this|you won't believe|this changed everything|stop doing|mistake)\b", re.I),
    re.compile(r"\b(don't make this|the biggest mistake|3 ways|top 5|one thing)\b", re.I),
    re.compile(r"\b(kyun|kaise|ye dekho|sach|kabhi mat|galti|raaz|kamaal)\b", re.I),  # Hinglish triggers
]


def predict_retention_score(
    text: str,
    duration_seconds: float = 30.0,
    hook_text: str = "",
    words: list[dict] | None = None,
) -> dict:
    """Compute algorithmic virality and audience retention prediction (0-100).

    Factors evaluated:
    1. Hook Strength (first 3-5s curiosity, shock value, emotional tension)
    2. Length & Duration sweet spot for mobile feeds (25-45s is optimal)
    3. Speaking Pace (Words per minute: optimal 145-185 WPM)
    4. Punchiness & Engagement cues (numbers, contrast, questions)
    """
    txt = (text or "").strip()
    full_text = f"{hook_text} {txt}".strip()
    word_tokens = full_text.split()
    n_words = len(word_tokens)
    dur = max(5.0, float(duration_seconds or 30.0))

    # 1. Hook Score (0 - 100)
    hook_score = 50.0
    opening = " ".join(word_tokens[:15])
    matches = sum(1 for pat in _HOOK_PATTERNS if pat.search(opening))
    if matches >= 2:
        hook_score += 35.0
    elif matches == 1:
        hook_score += 20.0
    if "?" in opening:
        hook_score += 10.0
    if any(char.isdigit() for char in opening):
        hook_score += 5.0
    hook_score = min(100.0, max(20.0, hook_score))

    # 2. Duration Score (0 - 100)
    if 25.0 <= dur <= 45.0:
        duration_score = 100.0
    elif 15.0 <= dur < 25.0:
        duration_score = 80.0 + (dur - 15.0) * 2.0
    elif 45.0 < dur <= 60.0:
        duration_score = 100.0 - (dur - 45.0) * 1.5
    elif dur > 60.0:
        duration_score = max(40.0, 77.5 - (dur - 60.0) * 0.8)
    else:
        duration_score = max(30.0, dur * 5.0)

    # 3. Pacing (Words Per Minute)
    wpm = (n_words / dur) * 60.0 if dur > 0 else 0
    if 140.0 <= wpm <= 185.0:
        pacing_score = 100.0
    elif 110.0 <= wpm < 140.0:
        pacing_score = 70.0 + (wpm - 110.0)
    elif 185.0 < wpm <= 220.0:
        pacing_score = 100.0 - (wpm - 185.0) * 0.8
    else:
        pacing_score = max(30.0, 60.0 - abs(wpm - 160.0) * 0.5)

    # 4. Engagement signals
    engagement = 60.0
    if "?" in full_text:
        engagement += 10.0
    if "!" in full_text:
        engagement += 10.0
    if any(w.isupper() and len(w) > 2 for w in word_tokens):
        engagement += 10.0
    engagement_score = min(100.0, engagement)

    # Composite predicted virality / retention score
    predicted = (
        hook_score * 0.35
        + duration_score * 0.25
        + pacing_score * 0.25
        + engagement_score * 0.15
    )
    predicted_score = round(predicted, 1)

    feedback = []
    if hook_score >= 80:
        feedback.append("Strong curiosity hook in first seconds")
    else:
        feedback.append("Consider leading with a provocative question or shocking reveal")
    if duration_score >= 90:
        feedback.append("Ideal length for high completion rate (25-45s)")
    elif dur > 60:
        feedback.append("Clip exceeds 60s; tighter editing can boost completion rate")
    if pacing_score >= 90:
        feedback.append(f"Optimal speech tempo ({int(wpm)} WPM)")
    elif wpm < 130:
        feedback.append(f"Slow speech tempo ({int(wpm)} WPM); cut pauses between sentences")

    return {
        "predicted_score": predicted_score,
        "hook_score": round(hook_score, 1),
        "duration_score": round(duration_score, 1),
        "pacing_score": round(pacing_score, 1),
        "engagement_score": round(engagement_score, 1),
        "wpm": round(wpm, 1),
        "duration_seconds": round(dur, 2),
        "feedback": feedback,
    }
