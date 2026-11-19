# Deploying ClipCut to a Server

ClipCut runs seamlessly as three containers on any Linux server: the ClipCut web application, PostgreSQL database, and Caddy (automatic HTTPS reverse proxy).

## Hardware & System Requirements
- **OS**: Ubuntu 22.04 / 24.04 LTS (recommended) with Docker & Docker Compose.
- **CPU**: 4+ Cores (8+ recommended for multi-user clipping).
- **RAM**: 8 GB to 16 GB RAM.
- **Storage**: 100 GB+ SSD for temporary video processing and caching.
- **Domain**: A domain or subdomain pointing an `A` record to your server's public IP.

## Quick Deployment Steps

1. Clone the repository on your server:
   ```bash
   git clone https://github.com/CM-Studio77/Clipcut.git
   cd Clipcut
   ```

2. Create and customize your `.env` configuration:
   ```bash
   cp .env.example .env
   ```
   Set `PEAKCUT_DOMAIN=yourdomain.com`, `POSTGRES_PASSWORD`, and your AI API Key (Gemini or OpenAI).

3. Launch with Docker Compose:
   ```bash
   docker compose up -d --build
   ```

4. Create your administrator account:
   ```bash
   docker compose exec app python -m studio.admin grant your-email@example.com
   ```

5. Access the studio:
   Open `https://yourdomain.com` and log in to configure social connections and settings.
