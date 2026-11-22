# --------------------------------------------------------------------------
# ClipCut AI Studio
# Author: CM Studio (https://github.com/CM-Studio77)
# Repository: https://github.com/CM-Studio77/Clipcut
# Copyright (c) 2026 CM Studio. All rights reserved.
# Licensed under Apache License 2.0. See LICENSE for details.
# --------------------------------------------------------------------------
import os
import sys
import urllib.parse
from bs4 import BeautifulSoup
import httpx

BASE_URL = "https://clipcut.ai"
SCRAPE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "scraped_site")
os.makedirs(SCRAPE_DIR, exist_ok=True)

candidate_paths = [
    "/",
    "/landing.html",
    "/web/index.html",
    "/index.html",
    "/auth.html",
    "/auth",
    "/admin.html",
    "/admin",
    "/legal.html",
    "/legal",
    "/reset.html",
    "/reset",
    "/brand/logo.svg",
    "/brand/logo-light.svg",
    "/brand/favicon.svg",
    "/brand/logo-email.png",
    "/brand/demo-bounce.jpg",
    "/brand/demo-bounce.mp4",
    "/brand/demo-clean.jpg",
    "/brand/demo-clean.mp4",
    "/brand/demo-hype.jpg",
    "/brand/demo-hype.mp4",
    "/ascii.js",
    "/gradient-ascii.js",
    "/healthz",
    "/api/info",
    "/version",
    "/robots.txt",
    "/sitemap.xml",
    "/manifest.json",
    "/favicon.ico"
]

visited = set()
queue = list(candidate_paths)

client = httpx.Client(base_url=BASE_URL, follow_redirects=True, timeout=15.0)

print(f"Starting scrape from {BASE_URL} into {SCRAPE_DIR}...")

while queue:
    path = queue.pop(0)
    if path in visited:
        continue
    visited.add(path)

    url = urllib.parse.urljoin(BASE_URL, path)
    try:
        res = client.get(path)
    except Exception as e:
        print(f"FAILED {path}: {e}")
        continue

    print(f"[{res.status_code}] {path} -> {res.url} ({len(res.content)} bytes, {res.headers.get('content-type', '')})")
    
    if res.status_code != 200:
        continue

    # Determine local save path
    rel_path = path.lstrip("/")
    if not rel_path or rel_path.endswith("/"):
        rel_path = rel_path + "index.html"
    
    save_path = os.path.join(SCRAPE_DIR, rel_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, "wb") as f:
        f.write(res.content)

    # If HTML, parse links and assets
    ct = res.headers.get("content-type", "")
    if "text/html" in ct:
        soup = BeautifulSoup(res.text, "html.parser")
        
        # tags to look for URLs: <link href>, <script src>, <img src>, <video src>, <source src>, <a href>
        for tag in soup.find_all(["link", "script", "img", "video", "source", "a"]):
            attr = None
            if tag.name == "link" and tag.has_attr("href"):
                attr = "href"
            elif tag.has_attr("src"):
                attr = "src"
            elif tag.name == "a" and tag.has_attr("href"):
                attr = "href"
            
            if attr:
                val = tag[attr]
                parsed = urllib.parse.urlparse(val)
                if parsed.scheme in ("", "http", "https"):
                    if parsed.netloc in ("", "clipcut.ai"):
                        asset_path = parsed.path
                        if asset_path and asset_path not in visited and not asset_path.startswith("mailto:") and not asset_path.startswith("javascript:"):
                            queue.append(asset_path)

print(f"\nScrape complete. Total visited: {len(visited)} URLs.")
