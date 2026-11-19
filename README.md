---
title: ClipCut AI Studio
emoji: ⚡
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
---

# ⚡ ClipCut — AI Video Clipping & Shorts Studio

> **Transform long videos and live streams into viral, captioned vertical shorts in seconds.**  
> Powered by AI & Whisper Speech Recognition. Developed by **CM Studio**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-cyan.svg)](Dockerfile)
[![GitHub Repository](https://img.shields.io/badge/GitHub-CM--Studio77%2FClipcut-purple.svg)](https://github.com/CM-Studio77/Clipcut)

---

## 🌟 Key Features

- 🎯 **AI Viral Moment Detection**: Automatically analyzes video transcripts and audio energy to pick the highest-retention hooks and scenes.
- 📱 **Smart 9:16 Vertical Reframing**: Converts landscape 16:9 videos into modern vertical Shorts, Reels, and TikToks with blurred, fill, or smart-crop layouts.
- 💬 **Dynamic Word-by-Word Captions**: Subtitles rendered in viral styles (Bounce, Clean, Hype) with customizable fonts, highlighting, and animations.
- 🔴 **Real-time Live Stream Clipper**: Paste YouTube, Twitch, or Kick live streams — ClipCut monitors the stream and clips highlights while it is still ongoing!
- 🚀 **Direct Social Publishing**: One-click connect for YouTube Shorts, Instagram Reels, and TikTok with scheduled posting and daily rate limits.
- 🧠 **Bring Your Own AI**: Full support for Google Gemini, OpenAI, Claude, Groq, Ollama, OpenRouter, or running 100% offline via loudness scoring.
- 🔒 **Self-Hosted & Private**: No monthly subscriptions, no watermarks, full control over your media and API keys.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **FFmpeg** installed and accessible in your PATH:
  - Windows: `winget install Gyan.FFmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt update && sudo apt install ffmpeg`

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CM-Studio77/Clipcut.git
   cd Clipcut
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   Add your Gemini / OpenAI API key to `.env`.

5. **Start ClipCut Studio:**
   ```bash
   python -m studio.server
   ```
   Open your browser at `http://127.0.0.1:8765`.

---

## 🐳 Docker Deployment

Run the complete ClipCut stack (App + PostgreSQL + Caddy HTTPS) with Docker Compose:

```bash
docker compose up -d --build
```

Access the studio at `https://your-domain` or `http://localhost:8765`.

---

## 🎨 Supported Caption Styles

- **Bounce**: Colorful pop-up words with high-energy bouncing animations (MrBeast style).
- **Hype**: Bold, impactful typography with dynamic keyword color highlights.
- **Clean**: Elegant, minimalistic subtitles for podcasts, interviews, and educational shorts.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) by **CM Studio**.
Portions copyright by PeakCut contributors.
