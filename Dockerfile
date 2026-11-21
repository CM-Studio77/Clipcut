# PeakCut: AI Video Clipping & Shorts Studio
FROM python:3.11-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg ca-certificates bzip2 fonts-noto-core fonts-noto-cjk \
 && rm -rf /var/lib/apt/lists/*
# yt-dlp needs a JavaScript runtime for YouTube
COPY --from=denoland/deno:bin /deno /usr/local/bin/deno

WORKDIR /app

# Create a non-root user (UID 1000) for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 user && \
    mkdir -p /data /app && \
    chown -R user:user /data /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY studio studio
COPY web web

RUN chown -R user:user /app

USER user

ENV PEAKCUT_DATA=/data \
    PEAKCUT_HOST=0.0.0.0 \
    PEAKCUT_PORT=7860 \
    PEAKCUT_TRUST_PROXY=1 \
    PYTHONUNBUFFERED=1

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=120s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/healthz', timeout=4)"

CMD ["python", "-m", "studio.server"]
