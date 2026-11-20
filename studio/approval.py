"""Approval queue: clips must be approved by a human before they are published."""
import json
import os
import threading
import time
from pathlib import Path

from . import config, ctx, jobs

_lock = threading.RLock()


def _queue_path(uid: str) -> Path:
    d = config.DATA_DIR / "users" / uid / "approval"
    d.mkdir(parents=True, exist_ok=True)
    return d


def add(uid: str, job_id: str, clip_id: str, platforms: list = None, meta: dict = None) -> dict:
    """Add a clip to the approval queue."""
    if platforms is None:
        platforms = ["youtube", "instagram", "tiktok", "facebook"]
    if meta is None:
        meta = {}
    
    # Retrieve clip metadata if available
    job = jobs._jobs.get(job_id) if hasattr(jobs, "_jobs") else None
    if not job:
        try:
            job = jobs.get(job_id)
        except Exception:
            job = None
    clip = None
    if job:
        clip = next((c for c in job.get("clips", []) if str(c.get("id")) == str(clip_id)), None)
        if clip:
            meta.setdefault("title", clip.get("title", ""))
            meta.setdefault("hook", clip.get("hook", ""))
            meta.setdefault("description", clip.get("description", ""))
            meta.setdefault("hashtags", clip.get("hashtags", []))
            meta.setdefault("tags", clip.get("tags", []))
            meta.setdefault("score", clip.get("score", 0))
            meta.setdefault("duration", clip.get("end", 0) - clip.get("start", 0))
            meta.setdefault("cover", clip.get("cover", ""))
            meta.setdefault("file", clip.get("file", ""))

    item = {
        "id": os.urandom(8).hex(),
        "uid": uid,
        "job_id": job_id,
        "clip_id": clip_id,
        "platforms": platforms,
        "meta": meta,
        "status": "pending",
        "created_at": time.time(),
    }
    p = _queue_path(uid) / f"{item['id']}.json"
    with _lock:
        p.write_text(json.dumps(item, indent=2), encoding="utf-8")
    return item


def _raw_items(uid: str) -> list:
    out = []
    for f in _queue_path(uid).glob("*.json"):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return out


def sync_all_ready_clips(uid: str = "u_local") -> int:
    """Sync all existing finished clips from jobs into the approval queue if not already present."""
    existing = set()
    for it in _raw_items(uid):
        existing.add((it.get("job_id"), str(it.get("clip_id"))))

    added = 0
    all_j = list(jobs._jobs.values()) if hasattr(jobs, "_jobs") else []
    for j in all_j:
        for c in j.get("clips", []):
            if c.get("status") == "done":
                pair = (j["id"], str(c.get("id")))
                if pair not in existing:
                    add(uid, j["id"], c["id"])
                    existing.add(pair)
                    added += 1
    return added


def queue(uid: str) -> list:
    """All pending approval items for this user."""
    items = [it for it in _raw_items(uid) if it.get("status") == "pending"]
    if not items:
        sync_all_ready_clips(uid)
        items = [it for it in _raw_items(uid) if it.get("status") == "pending"]
    return sorted(items, key=lambda x: x.get("created_at", 0), reverse=True)


def get(uid: str, item_id: str) -> dict | None:
    p = _queue_path(uid) / f"{item_id}.json"
    try:
        item = json.loads(p.read_text(encoding="utf-8"))
        return item if item.get("uid") == uid else None
    except (OSError, ValueError):
        return None


def approve(uid: str, item_id: str, platforms: list = None, meta: dict = None) -> dict:
    """Approve a clip: update metadata and mark as approved, then trigger publishing."""
    from . import posting, accounts
    with _lock:
        item = get(uid, item_id)
        if not item:
            raise ValueError("Item not found in approval queue.")
        if item.get("status") != "pending":
            raise ValueError(f"Clip is already {item.get('status')}.")
        
        item["status"] = "approved"
        item["approved_at"] = time.time()
        if platforms is not None:
            item["platforms"] = platforms
        if meta:
            item["meta"] = {**item.get("meta", {}), **meta}
            
        p = _queue_path(uid) / f"{item_id}.json"
        p.write_text(json.dumps(item, indent=2), encoding="utf-8")
        
    # Trigger publishing to approved platforms
    job = jobs._jobs.get(item["job_id"]) if hasattr(jobs, "_jobs") else None
    if not job:
        try:
            job = jobs.get(item["job_id"])
        except Exception:
            job = None
    if job:
        clip = next((c for c in job.get("clips", []) if str(c.get("id")) == str(item["clip_id"])), None)
        if clip:
            # Update clip with any edited metadata
            if meta:
                for k in ("title", "hook", "description", "hashtags", "tags"):
                    if k in meta:
                        clip[k] = meta[k]
                jobs.save(job)
            
            # Find accounts matching chosen platforms
            user_accounts = accounts.for_user(uid) if hasattr(accounts, "for_user") else []
            chosen_aids = []
            target_plats = set(item.get("platforms", []))
            for acc in user_accounts:
                if acc.get("platform") in target_plats:
                    chosen_aids.append(acc["id"])
                    
            if chosen_aids:
                schedule_mode = (meta or {}).get("schedule_mode", "now")
                schedule_at = (meta or {}).get("schedule_at")
                now = schedule_mode == "now"
                posting.enqueue(job, clip, chosen_aids, now=now, schedule_at=schedule_at)

    return item


def reject(uid: str, item_id: str, reason: str = "") -> dict:
    """Reject a clip."""
    with _lock:
        item = get(uid, item_id)
        if not item:
            raise ValueError("Item not found in approval queue.")
        item["status"] = "rejected"
        item["rejected_at"] = time.time()
        item["reason"] = reason
        item["rejection_reason"] = reason
        p = _queue_path(uid) / f"{item_id}.json"
        p.write_text(json.dumps(item, indent=2), encoding="utf-8")
    return item


def history(uid: str, limit: int = 50) -> list:
    """All processed items (approved/rejected) for this user."""
    out = []
    for f in _queue_path(uid).glob("*.json"):
        try:
            item = json.loads(f.read_text(encoding="utf-8"))
            if item.get("status") in ("approved", "rejected"):
                out.append(item)
        except (OSError, ValueError):
            pass
    return sorted(out, key=lambda x: x.get("created_at", 0), reverse=True)[:limit]
