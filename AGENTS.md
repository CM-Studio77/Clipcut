# Working on ClipCut

A developer guide for contributors and AI coding assistants.

## About ClipCut
ClipCut is an AI-powered automated video clipper and short-form content generator developed by CM Studio. It transforms long-form streams (YouTube, Twitch, Kick) and uploaded video files into optimized, captioned vertical clips (9:16) for YouTube Shorts, Instagram Reels, and TikTok.

## Run and test
- Run locally: `python -m studio.server` (settings from `.env`). Requires Python 3.10+ and `ffmpeg`.
- The speech model downloads automatically on first start; `python -m studio.fetch_model` can pre-download it.
- To test with clean data: `PEAKCUT_DATA=<temp folder> PEAKCUT_PORT=8766 python -m studio.server`.

## Codebase Architecture

| File | Description |
|---|---|
| `studio/server.py` | FastAPI/Starlette web routes, static files, middleware |
| `studio/config.py` | Configuration and environment variable loader |
| `studio/ai.py` | AI provider integration (Gemini, OpenAI, Groq, Ollama) |
| `studio/brain.py` | AI prompt engineering (highlight picking, viral hooks, captions) |
| `studio/jobs.py` | Video processing job lifecycle and queue management |
| `studio/live.py` | Real-time live stream recording and auto-segmentation |
| `studio/transcribe.py` | Speech-to-text engine using Sherpa-ONNX / Whisper |
| `studio/render.py` | Video reframing, layout generation, and ASS caption burn-in |
| `studio/posting.py` | YouTube, Instagram, and TikTok scheduled uploader |
| `web/index.html` | ClipCut Studio single-page application |
| `web/landing.html` | ClipCut marketing and landing page |
