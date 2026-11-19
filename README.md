<div align="center">

# ⚡ ClipCut — AI Video & Shorts Studio

### *Turn Long Videos & Live Streams into Viral, Scroll-Stopping 9:16 Shorts*

[![License: MIT](https://img.shields.io/badge/License-MIT-6366F1.svg?style=for-the-badge)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3B82F6.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Whisper ASR](https://img.shields.io/badge/Whisper-Multilingual_ASR-06B6D4.svg?style=for-the-badge)](https://github.com/SYSTRAN/faster-whisper)
[![Docker Ready](https://img.shields.io/badge/Docker-Containerized-22D3EE.svg?style=for-the-badge&logo=docker&logoColor=white)](Dockerfile)
[![Creator](https://img.shields.io/badge/Maintained_by-CM_Studio-10B981.svg?style=for-the-badge)](https://github.com/CM-Studio77/Clipcut)

<br/>

```
  ██████╗██╗     ██╗██████╗  ██████╗██╗   ██╗████████╗
 ██╔════╝██║     ██║██╔══██╗██╔════╝██║   ██║╚══██╔══╝
 ██║     ██║     ██║██████╔╝██║     ██║   ██║   ██║   
 ██║     ██║     ██║██╔═══╝ ██║     ██║   ██║   ██║   
 ╚██████╗███████╗██║██║     ╚██████╗╚██████╔╝   ██║   
  ╚═════╝╚══════╝╚═╝╚═╝      ╚═════╝ ╚═════╝    ╚═╝   
    A I   V I D E O   &   S H O R T S   S T U D I O   
```

**[⚡ Live Studio Demo](http://127.0.0.1:8765)** • **[🚀 Quick Start](#-quick-start)** • **[🎮 Facecam Layouts](#-dual-layer-facecam-layouts)** • **[🇮🇳 Hindi & Hinglish Guide](#-multilingual-hindi--hinglish-whisper-engine)** • **[📡 API Docs](#-api-endpoints)**

</div>

---

## 🌟 What is ClipCut?

**ClipCut** is a production-grade, self-hosted AI studio that transforms long videos (YouTube, Twitch, Kick, local files) and continuous live streams into high-retention, viral vertical shorts (9:16) for **TikTok, Instagram Reels, and YouTube Shorts**.

Featuring built-in **Faster-Whisper ASR**, automated **Facecam & Gameplay split layouts**, natural **Hindi / Hinglish transliteration**, dynamic animated captions, and intelligent hook discovery powered by Gemini, OpenAI, Claude, or local Ollama.

---

## 🚀 Key Highlights & Features

| Capability | Description |
| :--- | :--- |
| 🎮 **Dual-Layer Facecam Split** | Automatically crops webcam & gameplay into stacked 9:16 vertical layouts (`split_top`, `split_bottom`, `gameplay`). |
| 🇮🇳 **Multilingual & Hinglish Captions** | Transcribes English, Hindi, Urdu, or Auto-detects speech, converting Devanagari Hindi into natural Hinglish Roman subtitles for maximum viral retention. |
| ⚡ **Faster-Whisper int8 Engine** | High-performance CPU & GPU word-level timestamping running locally with zero cloud API audio costs. |
| 🔍 **AI Viral Moment Scout** | Evaluates transcripts, energetic audio peaks, and reactions to find the funniest and most engaging clips. |
| 🎨 **Dynamic Animated Captions** | Styled animated captions including **Bounce** (MrBeast style), **Hype** (bold neon word highlight), and **Clean** (podcast minimal). |
| 🔴 **Live Stream Clipping** | Monitors live YouTube, Twitch, or Kick streams in real-time and clips highlights while the broadcast is ongoing. |
| 📱 **High-End Cyber Studio UI** | Dark glassmorphism interface with 3D perspective demo previews, source quick-selectors, and interactive clip editing. |
| 🔒 **100% Private & Open Source** | Run locally on your own machine. No watermarks, no subscriptions, no data collection. |

---

## 🎮 Dual-Layer Facecam Layouts

ClipCut provides 6 intelligent layout modes built specifically for gamers, podcasters, and streamers:

### 1. `split_top` — Facecam on Top, Gameplay on Bottom
```
┌──────────────────┐
│  [ FACECAM ]     │  <-- Streamer webcam zoomed & centered (38% height)
├──────────────────┤
│                  │
│  [ GAMEPLAY ]    │  <-- High-octane action / gameplay (62% height)
│                  │
│  "BHAI KYA THA!" │  <-- Animated karaoke caption
└──────────────────┘
```

### 2. `split_bottom` — Gameplay on Top, Facecam on Bottom
```
┌──────────────────┐
│                  │
│  [ GAMEPLAY ]    │  <-- Game action on top (60% height)
│                  │
├──────────────────┤
│  [ FACECAM ]     │  <-- Face reaction on bottom (40% height)
│  "NO WAYYY! 💥"  │  <-- Animated neon captions
└──────────────────┘
```

### 3. `gameplay` — Picture-in-Picture Facecam
```
┌──────────────────┐
│                  │
│   Full 9:16      │
│   Action Video   │
│                  │
│          ┌─────┐ │
│          │ CAM │ │  <-- PiP Facecam corner overlay
└──────────┴─────┴─┘
```

### 4. Other Layouts:
- **`blur`**: Cinematic blurred background with the original 16:9 video centered.
- **`zoom`**: Dynamically scaled 9:16 crop filling the full canvas.
- **`crop`**: Direct center-cut with face/action tracking.

---

## 🇮🇳 Multilingual Hindi & Hinglish Whisper Engine

ClipCut features an integrated **Faster-Whisper** engine with a dedicated **Hindi-to-Hinglish transliterator** designed for Indian gaming creators and vloggers:

1. **Auto-Detect or Select Language**:
   - `auto`: Automatic language detection.
   - `hi`: Hindi transcription with automatic Roman Hinglish transliteration.
   - `en`: English subtitles.
   - `ur`: Roman Urdu transcription.
2. **Instant Hinglish Conversion**:
   - Spoken: *"नमस्ते दोस्तों आज हम खेलने वाले हैं GTA 5"*
   - Transcribed: `namaste doston aaj hum khelne wale hain GTA 5`
   - Rendered as bold neon karaoke captions word-by-word with 100% Devanagari font compatibility!

---

## 💻 Tech Stack & Architecture

- **Backend**: Python 3.10+, FastAPI, Starlette, Uvicorn
- **Speech Recognition**: Faster-Whisper (CTranslate2, int8 quantized)
- **Video Engine**: FFmpeg 6.0+, Libass, Pillow, OpenCV
- **AI Intelligence**: Google Gemini (Flash / Pro), OpenAI GPT-4o, Anthropic Claude 3.5, Groq, Ollama
- **Frontend**: Cyber Studio Glassmorphism, CSS Custom Properties, Vanilla JS, HTML5 Video, SVG Icons
- **Database**: SQLite (local) / PostgreSQL (production docker)

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10 or newer**
- **FFmpeg** installed and in your system `PATH`:
  - **Windows**: `winget install Gyan.FFmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Linux**: `sudo apt update && sudo apt install ffmpeg`

### 2. Clone & Setup

```bash
git clone https://github.com/CM-Studio77/Clipcut.git
cd Clipcut

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure `.env`

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your AI key (e.g. `GEMINI_API_KEY=...` or `OPENAI_API_KEY=...`).  
*Note: ClipCut works even without AI keys using built-in audio loudness peak detection!*

### 4. Run the Studio

```bash
python -m studio.server
```

Open your browser at **`http://127.0.0.1:8765`**.

---

## 🐳 Docker Deployment

Run the complete multi-container production stack with Docker Compose:

```bash
docker compose up -d --build
```

Access the studio at `http://localhost:8765`.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Cyber Landing page with interactive 3D demo & pricing |
| `GET` | `/app` | Studio web application dashboard |
| `GET` | `/api/status` | System health, supported languages, layouts, AI status |
| `POST` | `/api/jobs` | Submit a video URL (YouTube, Twitch, Kick) or local file for clipping |
| `GET` | `/api/jobs` | List all clipping jobs and progress |
| `GET` | `/api/jobs/{id}` | Inspect a specific job and rendered clips |
| `POST` | `/api/clips/{id}/render` | Re-render clip with new caption style, layout, or timings |
| `GET` | `/media/{job_id}/{file}` | Stream or download generated MP4 clips and thumbnails |

---

## 🎨 UI/UX Moodboard & Design Tour

The ClipCut design system is inspired by cutting-edge cyber creator tools:
- **01. Landing Hero**: 3D perspective phone mockup with live caption switcher.
- **02. Features Bento**: 6-card feature matrix highlighting AI Detection & Facecam Split.
- **03. Transparent Pricing**: Free ($0), Creator ($9.99/mo), and Studio ($24.99/mo).
- **04. Auth & Onboarding**: Cyber glass card with trust badges.
- **05. Source Quick-Select**: 1-click paste for YouTube, Twitch, Kick, and direct video upload.
- **06. Configure Your Clip**: Visual layout cards, duration sliders, language picker.
- **07. Overview Dashboard**: Real-time stats, greeting, processing activity.
- **08. Clip Editor**: Video stage, live caption selector (`Aa`), and 1-click export.

---

## 👥 Authors & Maintainers

- **CM Studio** — [nk9504858@gmail.com](mailto:nk9504858@gmail.com)
- **Repository**: [https://github.com/CM-Studio77/Clipcut](https://github.com/CM-Studio77/Clipcut)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.  
Portions copyright by PeakCut contributors.
