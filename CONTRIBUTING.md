# Contributing to ClipCut 🎬⚡

Thank you for your interest in contributing to **ClipCut**! ClipCut is an open-source, autonomous AI video studio built for streamers, podcasters, and content creators. We welcome contributions from developers, designers, video engineers, and documentation writers worldwide.

---

## 📜 Code of Conduct

ClipCut is dedicated to providing a welcoming, inclusive, and harassment-free environment for everyone. By participating in this project, you agree to abide by standard open-source community standards:
- Treat all community members with respect and kindness.
- Welcome diverse viewpoints and constructive criticism.
- Focus on what is best for the community and users.
- Show empathy towards other participants.

---

## 🛠️ Getting Started with Local Development

### 1. Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **Git**
- **FFmpeg 6.0+** installed with system `PATH` access:
  - *Ubuntu/Debian*: `sudo apt update && sudo apt install -y ffmpeg libsndfile1`
  - *macOS*: `brew install ffmpeg`
  - *Windows*: `winget install Gyan.FFmpeg`
- **Docker & Docker Compose** (optional, for containerized workflows)

### 2. Fork and Clone the Repository

```bash
git clone https://github.com/CM-Studio77/Clipcut.git
cd Clipcut
```

### 3. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate on Linux / macOS:
source .venv/bin/activate

# Activate on Windows PowerShell:
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-asyncio flake8
```

### 5. Configure Local Environment

Copy the example configuration:
```bash
cp .env.example .env
```
ClipCut is designed to run locally even without external AI keys! For full AI features, add your Gemini, OpenAI, Claude, or Groq API keys to `.env`.

### 6. Start the Local Server

```bash
python -m studio.server
```
Visit `http://127.0.0.1:8765` in your browser.

---

## 📐 Project Architecture & Structure

```
ClipCut/
├── studio/               # Core Python Backend & Processing Engines
│   ├── server.py         # FastAPI Web Application & API router
│   ├── context.py        # Multimodal fusion (Vision + Audio + Chat)
│   ├── virality.py       # Hook scoring & engagement retention heuristics
│   ├── facecam.py        # Facecam detection & dual-layer 9:16 layout split
│   ├── render.py         # FFmpeg video rendering & subtitle compositing
│   ├── roman.py          # Hinglish Romanization engine (Hindi/Urdu transliteration)
│   ├── emoji.py          # 3D Google Noto emoji placement in captions
│   ├── sfx.py            # Audio whoosh sound effects & sonic transitions
│   ├── approval.py       # Human-in-the-loop approval center queue
│   ├── accounts.py       # Social platform OAuth & token manager
│   ├── posting.py        # YouTube Shorts, IG Reels, TikTok, FB Reels adapters
│   └── asr_worker.py     # Faster-Whisper int8 local speech transcription
├── web/                  # Web Interface & Assets
│   ├── index.html        # Live Studio & Creator Dashboard
│   ├── landing.html      # Obsidian Cyber Dark Landing Page
│   └── brand/            # SVGs, Logos, and Visual Media Assets
├── tests/                # Automated Test Suite & Validation
│   ├── run.py            # Comprehensive test runner
│   ├── test_local.py     # Local pipeline integration tests
│   └── test_roman.py     # Hinglish transliteration test suite
└── .github/              # GitHub Actions Workflows & Automation
```

---

## 🔄 Development & PR Workflow

We follow standard GitHub Flow:

1. **Create an Issue**: Before submitting a major feature or refactor, open an issue to discuss your proposal.
2. **Branch Naming**:
   - `feat/feature-name` (e.g., `feat/twitch-chat-sentiment`)
   - `fix/bug-description` (e.g., `fix/ffmpeg-subtitle-wrap`)
   - `docs/documentation-update` (e.g., `docs/readme-docker-guide`)
3. **Commit Messages**: Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add animated 3D emoji injection for highlights`
   - `fix: resolve subtitle font fallback on Linux`
   - `docs: update quickstart guide with Docker Compose instructions`
4. **Run Local Tests**:
   Ensure all tests pass before opening your Pull Request:
   ```bash
   python tests/test_local.py
   python tests/test_roman.py
   python tests/test_captions.py
   ```
5. **Code Style & Linting**:
   ```bash
   flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv,__pycache__
   ```
6. **Submit Pull Request**:
   - Target the `main` branch.
   - Describe the changes and reference any related issues (e.g., `Closes #42`).
   - Include before/after screenshots or terminal outputs where appropriate.

---

## 🧪 Testing Guidelines

- Write clean, deterministic unit tests for every new feature or bug fix.
- Test edge cases (e.g. videos with no speech, extremely long live streams, special characters in subtitles).
- Do not make external API calls in automated test suites; mock network requests.

---

## 💡 Feature Ideas & Contribution Areas

We actively seek contributions in:
- **New Social Adapters**: Bluesky video, LinkedIn video, Threads video.
- **Enhanced ASR & Dialects**: Additional regional transliteration engines (Tamil, Telugu, Bengali, Arabic).
- **GPU Acceleration**: CUDA / TensorRT / Apple Metal optimizations for faster-whisper and FFmpeg pipelines.
- **Visual Filters & Effects**: Custom caption animations, border glow effects, dynamic face tracking.

---

## 📄 License & Attribution

By contributing to ClipCut, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
