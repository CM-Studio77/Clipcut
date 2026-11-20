"""Multimodal video intelligence: extracts frames from streams/clips and analyzes visual action & reaction."""
import json
import re
import subprocess
import tempfile
from pathlib import Path

from . import ai, config, media


def extract_frame(video_path: Path, timestamp: float = 0.0) -> bytes | None:
    """Extract a single JPEG frame at a given timestamp using FFmpeg."""
    cmd = [
        "ffmpeg", "-v", "error",
        "-ss", f"{timestamp:.2f}",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "3",
        "-f", "image2",
        "pipe:1"
    ]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=getattr(media, "NO_WINDOW", 0),
            timeout=10,
            check=False
        )
        if proc.returncode == 0 and len(proc.stdout) > 500:
            return proc.stdout
    except Exception:
        pass
    return None


VISION_PROMPT = """Analyze this video frame from a live stream session.
Evaluate the visual virality and action:
- Visual excitement level (0-100)
- Streamer reaction (laughing, shock, anger, celebrating, neutral, no facecam)
- Gameplay or visual action (clutch play, elimination, fail, discovery, intense action, calm)
- Standalone clip visual appeal

Return JSON only:
{
  "visual_score": <integer 0-100>,
  "reaction": "<one of: laughing, shock, excited, rage, celebrating, neutral, none>",
  "action": "<brief description of visual event>",
  "is_viral_moment": <true/false>
}
"""


def judge_frame(image_bytes: bytes, timeout: float = 15.0) -> dict:
    """Send a frame to Multimodal AI and parse visual intelligence."""
    if not image_bytes or not ai.ready():
        return {"visual_score": 50, "reaction": "neutral", "action": "", "is_viral_moment": False}
    try:
        text, _, _ = ai.see(VISION_PROMPT, image_bytes, timeout=timeout)
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            data = json.loads(m.group(0))
            return {
                "visual_score": int(data.get("visual_score", 50)),
                "reaction": str(data.get("reaction", "neutral")),
                "action": str(data.get("action", "")),
                "is_viral_moment": bool(data.get("is_viral_moment", False)),
            }
    except Exception:
        pass
    return {"visual_score": 50, "reaction": "neutral", "action": "", "is_viral_moment": False}


def analyze_video_moment(video_path: Path, timestamp: float) -> dict:
    """Extract and analyze visual frame at a specific moment."""
    frame = extract_frame(video_path, timestamp)
    if not frame:
        return {"visual_score": 50, "reaction": "neutral", "action": "", "is_viral_moment": False}
    return judge_frame(frame)
