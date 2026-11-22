# --------------------------------------------------------------------------
# ClipCut AI Studio
# Author: CM Studio (https://github.com/CM-Studio77)
# Repository: https://github.com/CM-Studio77/Clipcut
# Copyright (c) 2026 CM Studio. All rights reserved.
# Licensed under Apache License 2.0. See LICENSE for details.
# --------------------------------------------------------------------------
"""Context Fusion Engine: Synchronizes Video, Audio, Speech Transcript, and Live Chat signals.
Computes multimodal virality composite scores and generates highlight candidates."""
import time
from dataclasses import dataclass, field
from pathlib import Path

from . import vision


@dataclass
class MultimodalEvidence:
    speech_text: str = ""
    speech_score: int = 0
    audio_loudness_db: float = 0.0
    audio_jump_pct: float = 0.0
    chat_velocity_spike: float = 0.0
    chat_top_reactions: list = field(default_factory=list)
    visual_score: int = 50
    visual_reaction: str = "neutral"
    visual_action: str = ""
    composite_score: int = 0
    multimodal_boost: bool = False


def calculate_composite_score(
    speech_score: int,
    audio_jump_pct: float,
    chat_spike_ratio: float,
    visual_score: int = 50
) -> tuple[int, bool]:
    """Combines all multimodal indicators into a unified 0-100 virality score."""
    # Normalize inputs
    w_score = max(0, min(100, speech_score))
    
    # Audio jump: 0% jump -> 50 score, +100% jump -> 100 score
    a_score = max(0, min(100, int(50 + (audio_jump_pct * 50))))
    
    # Chat spike: 1x -> 50, 3x+ -> 100
    c_score = max(0, min(100, int(min(chat_spike_ratio, 4.0) / 4.0 * 100))) if chat_spike_ratio > 0 else 50
    
    # Visual score
    v_score = max(0, min(100, visual_score))
    
    # Weighting: Speech 35%, Audio 25%, Chat 20%, Visual 20%
    base_score = int(
        (0.35 * w_score) +
        (0.25 * a_score) +
        (0.20 * c_score) +
        (0.20 * v_score)
    )
    
    # Synergistic boost: if at least 3 indicators are high
    high_count = sum([
        w_score >= 70,
        a_score >= 75,
        c_score >= 75,
        v_score >= 75
    ])
    
    boost = high_count >= 3
    final_score = min(100, base_score + (12 if boost else 0))
    return final_score, boost


def fuse_signals(
    start_sec: float,
    end_sec: float,
    words: list,
    db_history: list,
    chat_history: dict,
    video_path: Path | None = None
) -> MultimodalEvidence:
    """Fuses all available data streams for a time window."""
    s_idx, e_idx = int(start_sec), int(end_sec)
    
    # 1. Transcript slice
    spoken_words = [w["text"] for w in words if s_idx <= w.get("s", 0) <= e_idx]
    transcript_text = " ".join(spoken_words)
    
    # 2. Audio loudness
    window_db = db_history[s_idx:e_idx] if len(db_history) > e_idx else db_history[-30:] if db_history else []
    mean_db = float(sum(window_db) / len(window_db)) if window_db else -50.0
    prior_db = db_history[max(0, s_idx - 60):s_idx] if s_idx > 10 else []
    prior_mean = float(sum(prior_db) / len(prior_db)) if prior_db else mean_db
    audio_jump = (mean_db - prior_mean) / abs(prior_mean) if prior_mean != 0 else 0.0
    
    # 3. Chat velocity
    chat_counts = [chat_history.get(t, 0) for t in range(s_idx, e_idx + 1)] if chat_history else []
    chat_rate = sum(chat_counts) / max(1, len(chat_counts)) if chat_counts else 0.0
    prior_chat = [chat_history.get(t, 0) for t in range(max(0, s_idx - 60), s_idx)] if chat_history else []
    prior_rate = sum(prior_chat) / max(1, len(prior_chat)) if prior_chat else 1.0
    chat_ratio = (chat_rate / prior_rate) if prior_rate > 0 else 1.0
    
    # 4. Visual intelligence
    v_data = {"visual_score": 55, "reaction": "neutral", "action": ""}
    if video_path and video_path.exists():
        midpoint = (start_sec + end_sec) / 2.0
        v_data = vision.analyze_video_moment(video_path, midpoint)
        
    final_score, boosted = calculate_composite_score(
        speech_score=70 if spoken_words else 45,
        audio_jump_pct=audio_jump,
        chat_spike_ratio=chat_ratio,
        visual_score=v_data["visual_score"]
    )
    
    return MultimodalEvidence(
        speech_text=transcript_text,
        speech_score=70 if spoken_words else 45,
        audio_loudness_db=round(mean_db, 1),
        audio_jump_pct=round(audio_jump * 100, 1),
        chat_velocity_spike=round(chat_ratio, 2),
        visual_score=v_data["visual_score"],
        visual_reaction=v_data["reaction"],
        visual_action=v_data["action"],
        composite_score=final_score,
        multimodal_boost=boosted
    )
