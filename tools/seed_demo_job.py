import os
import shutil
import json
from pathlib import Path
from studio import config, auth, ctx, db, jobs

db.init()
u = auth.local_user()
uid = u.id

user_jobs_dir = config.user_dir(uid) / "jobs"
job_id = "20261122-120000-technogta6"
job_dir = user_jobs_dir / job_id
clips_dir = job_dir / "clips"
clips_dir.mkdir(parents=True, exist_ok=True)

brand_dir = config.ROOT / "web" / "brand"

# Copy media files into clips_dir
shutil.copy2(brand_dir / "techno-thumb.jpg", job_dir / "thumb.jpg")
shutil.copy2(brand_dir / "techno-clip1.mp4", clips_dir / "clip01.mp4")
shutil.copy2(brand_dir / "techno-thumb1.jpg", clips_dir / "clip01.jpg")
shutil.copy2(brand_dir / "techno-clip2.mp4", clips_dir / "clip02.mp4")
shutil.copy2(brand_dir / "techno-thumb2.jpg", clips_dir / "clip02.jpg")
shutil.copy2(brand_dir / "techno-clip3.mp4", clips_dir / "clip03.mp4")
shutil.copy2(brand_dir / "techno-thumb3.jpg", clips_dir / "clip03.jpg")

job_data = {
    "id": job_id,
    "user": uid,
    "title": "MY GIRLFRIEND IS BACK | GTA 6 GAMEPLAY #3",
    "uploader": "Techno Gamerz",
    "channel": "Techno Gamerz",
    "kind": "video",
    "creator": "caseoh",
    "status": "done",
    "stage": "Finished",
    "progress": 1.0,
    "duration": 60,
    "took": 4,
    "thumb": "thumb.jpg",
    "source": {
        "type": "link",
        "url": "https://youtu.be/1O_GCgCu-j4",
        "name": "MY GIRLFRIEND IS BACK | GTA 6 GAMEPLAY #3"
    },
    "options": {
        "max_clips": 3,
        "min_len": 15,
        "max_len": 60,
        "style": "mrbeast",
        "layout": "split_bottom",
        "captions": True,
        "lang": "hi"
    },
    "clips": [
        {
            "id": "clip01",
            "title": "MY GIRLFRIEND IS BACK | GTA 6 GAMEPLAY #3 — Viral Reaction & Intense Hook",
            "hook": "INSANE REACTION MOMENT",
            "score": 99,
            "virality_score": 99,
            "tag": "VIRAL HOOK",
            "duration": 22,
            "start": 0.0,
            "end": 22.0,
            "file": "clip01.mp4",
            "cover": "clip01.jpg",
            "version": 1,
            "status": "done",
            "style": "mrbeast",
            "captions": "MrBeast Bold",
            "layout": "split_bottom",
            "ratio": "9:16 Vertical HD",
            "hashtags": ["Shorts", "ViralShorts", "GTA6", "TechnoGamerz", "Gaming"],
            "tags": ["gta 6", "techno gamerz", "gaming shorts", "viral shorts"]
        },
        {
            "id": "clip02",
            "title": "MY GIRLFRIEND IS BACK | GTA 6 GAMEPLAY #3 — Police Escape & High-Speed Chase",
            "hook": "HIGH-SPEED CHASE & ESCAPE",
            "score": 96,
            "virality_score": 96,
            "tag": "ACTION CLIMAX",
            "duration": 20,
            "start": 15.0,
            "end": 35.0,
            "file": "clip02.mp4",
            "cover": "clip02.jpg",
            "version": 1,
            "status": "done",
            "style": "hormozi",
            "captions": "Hormozi Pop",
            "layout": "split_bottom",
            "ratio": "9:16 Vertical HD",
            "hashtags": ["Shorts", "PoliceChase", "GTA6Gameplay", "Viral"],
            "tags": ["gta 6 police chase", "techno gamerz gta", "action clips"]
        },
        {
            "id": "clip03",
            "title": "MY GIRLFRIEND IS BACK | GTA 6 GAMEPLAY #3 — Hilarious Dialogue & Ending Moment",
            "hook": "WAIT FOR THE ENDING",
            "score": 94,
            "virality_score": 94,
            "tag": "FUNNY MOMENT",
            "duration": 18,
            "start": 30.0,
            "end": 48.0,
            "file": "clip03.mp4",
            "cover": "clip03.jpg",
            "version": 1,
            "status": "done",
            "style": "clean",
            "captions": "Clean Minimal",
            "layout": "split_bottom",
            "ratio": "9:16 Vertical HD",
            "hashtags": ["Shorts", "FunnyMoments", "GTA6Ending", "ComedyShorts"],
            "tags": ["funny gta moments", "techno comedy", "shorts feed"]
        }
    ],
    "ai": {
        "model": "gemini-2.5-flash",
        "tokens": 450,
        "log": ["Detected high-energy reaction spike at 0s", "Gameplay split layout applied (70% game, 30% facecam)", "Animated captions rendered with MrBeast style"]
    }
}

job_file = job_dir / "job.json"
job_file.write_text(json.dumps(job_data, indent=2), encoding="utf-8")
print(f"Successfully seeded job {job_id} at {job_file}!")
