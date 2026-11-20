"""Post queue: decides when each finished clip goes to which account, posts it, and tracks views."""
import secrets
import threading
import time
from pathlib import Path

import json

from . import accounts, alerts, config, creators, ctx, jobs, live

_lock = threading.RLock()
_FILE = config.DATA_DIR / "posts.json"
try:
    _posts: list = json.loads(_FILE.read_text(encoding="utf-8")) if _FILE.exists() else []
except ValueError:
    _posts = []


def _mine() -> list:
    u = ctx.uid()
    return [p for p in _posts if p.get("user") == u]
OPEN = ("scheduled", "posting")


def _save():
    with _lock:
        tmp = _FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(_posts, indent=1), encoding="utf-8")
        tmp.replace(_FILE)


def forget(uid: str):
    """Drop everything queued or recorded for a deleted account, so nothing is posted or retried for it any more."""
    with _lock:
        for p in _posts:
            if p.get("user") == uid:
                p["status"] = "deleted"          # the posting loop may be holding this one already: it then skips it
        _posts[:] = [p for p in _posts if p.get("user") != uid]
        _save()


def _day(t):
    return time.strftime("%Y-%m-%d", time.localtime(t))


def _mirror(p):
    """Copy the post's state onto its clip so the clip card can show it."""
    job = jobs.get(p["job"])
    clip = next((c for c in job["clips"] if c["id"] == p["clip"]), None) if job else None
    if clip is not None:
        clip.setdefault("posts", {})[p["id"]] = {k: p.get(k) for k in ("account_name", "platform", "status", "url", "due_at", "error")}
        jobs.save(job)


VIRAL_PEAK_HOURS = [(9, 0), (13, 30), (18, 30), (21, 0)]


def _align_to_viral_slot(target_time: float) -> float:
    """Aligns post time to the nearest optimal viral engagement window."""
    lt = time.localtime(target_time)
    today = (lt.tm_year, lt.tm_mon, lt.tm_mday)
    for h, m in VIRAL_PEAK_HOURS:
        slot = time.mktime((*today, h, m, 0, 0, 0, -1))
        if slot >= target_time - 300:
            return slot
    next_day_lt = time.localtime(target_time + 86400)
    return time.mktime((next_day_lt.tm_year, next_day_lt.tm_mon, next_day_lt.tm_mday, VIRAL_PEAK_HOURS[0][0], VIRAL_PEAK_HOURS[0][1], 0, 0, 0, -1))


def _next_slot(account_id, gap_min, cap):
    """Earliest time that respects the gap between posts, viral engagement slots, and the daily cap for this account."""
    mine = [p for p in _mine() if p["account"] == account_id and p["status"] in OPEN + ("posted",)]
    t = max(time.time(), max((p.get("posted_at") or p["due_at"] for p in mine), default=0) + gap_min * 60)
    t = _align_to_viral_slot(t)
    for _ in range(30):
        if sum(1 for p in mine if _day(p.get("posted_at") or p["due_at"]) == _day(t)) < cap:
            break
        lt = time.localtime(t + 86400)
        t = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, VIRAL_PEAK_HOURS[0][0], VIRAL_PEAK_HOURS[0][1], 0, 0, 0, -1))
    return t


def enqueue(job, clip, account_ids, now=False, schedule_at: float = None) -> list:
    c = creators.get(job["creator"]) or creators.DEFAULTS
    made = []
    with _lock:
        for aid in account_ids:
            acc = accounts.get(aid)
            if not acc:
                continue
            if any(p["job"] == job["id"] and p["clip"] == clip["id"] and p["account"] == aid
                   and p["status"] in OPEN + ("posted",) for p in _mine()):
                continue  # never post the same clip to the same account twice
            if schedule_at and float(schedule_at) > time.time():
                due = float(schedule_at)
            elif now:
                due = time.time()
            else:
                due = _next_slot(aid, c["post_gap_min"], c["daily_cap"])
            p = {"id": secrets.token_hex(8), "user": ctx.uid(), "job": job["id"], "clip": clip["id"], "creator": job["creator"],
                 "account": aid, "account_name": acc["name"], "platform": acc["platform"], "status": "scheduled",
                 "due_at": due, "created": time.time(), "title": clip.get("title") or clip.get("hook") or "Clip",
                 "score": clip.get("score", 0), "tries": 0, "url": "", "remote_id": "", "error": None, "views": None}
            _posts.append(p)
            made.append(p)
        _save()
    for p in made:
        _mirror(p)
    return made


def on_clip_ready(job, clip):
    """Called once when a clip first finishes rendering."""
    # Fixed Configuration: Human Approval Required. Add every finished clip to approval queue.
    from . import approval
    uid = job.get("user") or ctx.uid()
    if uid:
        try:
            approval.add(uid, job["id"], clip["id"])
        except Exception:
            pass

    c = creators.get(job["creator"])
    if not c or not c.get("autopost") or not c.get("accounts"):
        return
    # If autopost is explicitly enabled and auto_approve is set, proceed
    if not c.get("auto_approve_no_review", False):
        return
    if clip.get("score", 0) < c["post_min_score"]:
        return  # includes hand-made clips (score 0): those wait for you to press Post
    made = enqueue(job, clip, c["accounts"])
    if made:
        creators.log(c["id"], f"Queued for {len(made)} account(s): {clip.get('title') or clip.get('hook')}")


def _format_youtube_caption(clip, creator):
    desc = clip.get("description") or ""
    hook = clip.get("hook") or ""
    tags = clip.get("hashtags") or []
    parts = []
    if hook:
        parts.append(f"🔥 {hook}")
    if desc:
        parts.append(desc)
    parts.append("━━━━━━━━━━━━━━━━━━━━━")
    parts.append("🎬 Full live stream highlight extracted with ClipCut AI.")
    parts.append("🔔 Subscribe & turn on notifications for daily viral clips!")
    parts.append("━━━━━━━━━━━━━━━━━━━━━")
    ht_line = " ".join("#" + h.lstrip("#") for h in tags)
    if "#Shorts" not in ht_line and "#shorts" not in ht_line:
        ht_line += " #Shorts #YouTubeShorts #Viral #Trending"
    parts.append(ht_line)
    if creator.get("post_footer"):
        parts.append(creator["post_footer"])
    return "\n\n".join(parts)


def _format_instagram_caption(clip, creator):
    title = clip.get("title") or clip.get("hook") or "Viral Reel"
    desc = clip.get("description") or ""
    tags = clip.get("hashtags") or []
    parts = [f"{title} 😱👇"]
    if desc:
        parts.append(desc)
    parts.append(".\n.\n💬 Konsa part sabse best laga? Comment mein batao! 👇\n👉 Follow for daily viral clips & reels!\n.\n.")
    base_tags = [h.lstrip("#") for h in tags]
    ig_viral = ["reels", "reelsinstagram", "viralreels", "trendingreels", "explorepage", "instareels", "funnyreels", "gamingreels", "foryou", "explore", "trending"]
    all_tags = list(dict.fromkeys(base_tags + ig_viral))[:28]
    parts.append(" ".join("#" + t for t in all_tags))
    if creator.get("post_footer"):
        parts.append(creator["post_footer"])
    return "\n".join(parts)


def _format_tiktok_caption(clip, creator):
    hook = clip.get("hook") or clip.get("title") or "Must watch"
    tags = clip.get("hashtags") or []
    tt_tags = list(dict.fromkeys([h.lstrip("#") for h in tags] + ["fyp", "foryou", "viral", "trending"]))[:6]
    ht_str = " ".join("#" + t for t in tt_tags)
    return f"{hook} 💀🔥 {ht_str}"[:200]


def _format_facebook_caption(clip, creator):
    title = clip.get("title") or clip.get("hook") or "Must Watch Clip"
    desc = clip.get("description") or ""
    parts = [title]
    if desc:
        parts.append(desc)
    parts.append("Watch till the end! Like and Follow our page for daily viral moments! 🎬")
    if creator.get("post_footer"):
        parts.append(creator["post_footer"])
    return "\n\n".join(parts)


def _post(p):
    job = jobs.get(p["job"])
    clip = next((c for c in job["clips"] if c["id"] == p["clip"]), None) if job else None
    acc = accounts.get(p["account"])
    try:
        if not clip or clip.get("status") != "done":
            raise RuntimeError("The clip no longer exists or is not finished.")
        if not acc:
            raise RuntimeError("That account was disconnected.")
        path = Path(job["dir"]) / "clips" / clip["file"]
        creator = creators.get(job["creator"]) or dict(creators.DEFAULTS, name="clips")
        title = clip.get("title") or clip.get("hook") or "Clip"
        
        if acc["platform"] == "youtube":
            yt_tags = clip.get("tags") or [h.lstrip("#") for h in clip.get("hashtags", [])]
            if "#Shorts" not in title and "#shorts" not in title and len(title) <= 90:
                title = f"{title} #Shorts"
            yt_cap = _format_youtube_caption(clip, creator)
            rid, url = accounts.youtube_upload(acc, path, title, yt_cap, yt_tags, creator["privacy"])
            accounts.youtube_post_comment(acc, rid, "🔴 Full stream replay on channel! Drop a like & subscribe for daily viral highlights! 👇🔥")
        elif acc["platform"] == "instagram":
            ig_cap = _format_instagram_caption(clip, creator)
            rid, url = accounts.instagram_upload(acc, path, ig_cap, job["id"])
            if rid:
                accounts.instagram_post_comment(acc, rid, "Tag a friend who needs to see this! 😂 Drop a ❤️ if you loved it!")
        elif acc["platform"] == "tiktok":
            tt_cap = _format_tiktok_caption(clip, creator)
            rid, url = accounts.tiktok_upload(acc, path, tt_cap, creator["privacy"])
        elif acc["platform"] == "facebook":
            fb_cap = _format_facebook_caption(clip, creator)
            rid, url = accounts.facebook_upload(acc, path, title, fb_cap, job["id"])
        else:
            raise RuntimeError("That kind of account is no longer supported.")
        p.update(status="posted", posted_at=time.time(), remote_id=rid, url=url, error=None)
        creators.log(p["creator"], f"Posted to {acc['name']}: {title}")
    except Exception as e:  # noqa: BLE001
        p["tries"] += 1
        p["error"] = str(e)[-300:]
        if p["tries"] < 3 and clip and acc:
            p.update(status="scheduled", due_at=time.time() + 600)  # try again in 10 minutes
        else:
            p["status"] = "failed"
            creators.log(p["creator"], f"Post failed on {p['account_name']}: {p['error']}")
            alerts.notify(f"post failed on {p['account_name']} ({p['title']}): {p['error'][:200]}", kind="post")
    _save()
    _mirror(p)


def _run():
    while True:
        time.sleep(15)
        due = [p for p in list(_posts) if p["status"] == "scheduled" and p["due_at"] <= time.time() and p.get("user")]
        for p in due:
            try:
                with ctx.as_user(p["user"]):
                    if accounts.settings()["paused"]:
                        continue
                    with _lock:
                        if p["status"] != "scheduled":
                            continue
                        p["status"] = "posting"
                    _post(p)
            except Exception:  # noqa: BLE001
                pass


def _stats_for(recent):
    for aid in {p["account"] for p in recent if p["platform"] == "youtube"}:
        acc = accounts.get(aid)
        if acc:
            views = accounts.youtube_views(acc, [p["remote_id"] for p in recent if p["account"] == aid])
            for p in recent:
                if p["account"] == aid and p["remote_id"] in views:
                    p["views"] = views[p["remote_id"]]
    for p in recent:
        acc = accounts.get(p["account"]) if p["platform"] == "instagram" else None
        if acc:
            v = accounts.instagram_views(acc, p["remote_id"])
            if v is not None:
                p["views"] = v


def _stats():
    while True:
        for uid in {p.get("user") for p in _posts if p.get("user")}:
            try:
                with ctx.as_user(uid):
                    _stats_for([p for p in _mine() if p["status"] == "posted" and time.time() - p["posted_at"] < 14 * 86400])
            except Exception:  # noqa: BLE001
                pass
        _save()
        time.sleep(1800)


def cancel(pid):
    with _lock:
        p = next((p for p in _mine() if p["id"] == pid), None)
        if not p or p["status"] != "scheduled":
            raise ValueError("Only posts that are still waiting can be cancelled.")
        p["status"] = "cancelled"
        _save()
    _mirror(p)


def retry(pid):
    with _lock:
        p = next((p for p in _mine() if p["id"] == pid), None)
        if not p or p["status"] not in ("failed", "cancelled"):
            raise ValueError("Only failed or cancelled posts can be retried.")
        p.update(status="scheduled", due_at=time.time(), tries=0, error=None)
        _save()
    _mirror(p)


def overview() -> dict:
    today = _day(time.time())
    _posts = _mine()  # everything below is about the signed-in user only
    rows = []
    all_cs, all_js = creators.all_creators(), jobs.list_jobs()
    for c in all_cs:
        js = [j for j in all_js if j["creator"] == c["id"]]
        clips = [k for j in js for k in j["clips"] if k.get("status") == "done"]
        ps = [p for p in _posts if p["creator"] == c["id"]]
        views = sum(p["views"] or 0 for p in ps)
        rows.append({
            "id": c["id"], "name": c["name"],
            "state": "recording" if live.active_for(c["id"]) else "waiting" if c["auto_watch"] and c["channel"] else "idle",
            "autopost": c["autopost"] and bool(c["accounts"]),
            "clips_today": sum(1 for k in clips if _day(k.get("made_at", 0)) == today), "clips_total": len(clips),
            "posted_today": sum(1 for p in ps if p["status"] == "posted" and _day(p["posted_at"]) == today),
            "posted_total": sum(1 for p in ps if p["status"] == "posted"),
            "queued": sum(1 for p in ps if p["status"] in OPEN), "failed": sum(1 for p in ps if p["status"] == "failed"),
            "views": views, "earnings": round(views / 1000 * c["rate_per_1k"], 2)})
    names = {c["id"]: c["name"] for c in all_cs}
    queue = sorted((p for p in _posts if p["status"] in OPEN), key=lambda p: p["due_at"])
    done = sorted((p for p in _posts if p["status"] in ("posted", "failed")), key=lambda p: -(p.get("posted_at") or p["due_at"]))[:15]
    show = [{**{k: v for k, v in p.items() if k != "user"}, "creator_name": names.get(p["creator"], "")} for p in queue + done]
    # last 14 days, oldest first, for the home graph
    days = [_day(time.time() - 86400 * i) for i in range(13, -1, -1)]
    made, posted, views = {d: 0 for d in days}, {d: 0 for d in days}, {d: 0 for d in days}
    for j in all_js:
        for k in j["clips"]:
            d = _day(k.get("made_at") or j["created"])
            if k.get("status") == "done" and d in made:
                made[d] += 1
    for p in _posts:
        if p["status"] == "posted" and _day(p["posted_at"]) in posted:
            posted[_day(p["posted_at"])] += 1
            views[_day(p["posted_at"])] += p["views"] or 0
    daily = [{"day": d, "clips": made[d], "posted": posted[d], "views": views[d]} for d in days]
    return {"paused": accounts.settings()["paused"], "creators": rows, "posts": show, "daily": daily,
            "alerts": alerts.configured(), "recording": len(live.active_mine())}


def history(limit: int = 100) -> list:
    """List posts for the current user, most recent first."""
    return sorted(_mine(), key=lambda p: p.get("created", 0), reverse=True)[:limit]


def digest_text() -> str:
    o = overview()
    lines = ["PeakCut daily summary"]
    for r in o["creators"]:
        lines.append(f"- {r['name']}: {r['state']}, {r['clips_today']} clips today, {r['posted_today']} posted today, "
                     f"{r['queued']} waiting, {r['failed']} failed, {r['views']} views")
    if not o["creators"]:
        lines.append("No creators set up yet.")
    if o["paused"]:
        lines.append("Posting is paused.")
    return "\n".join(lines)


def start():
    with _lock:
        for p in _posts:
            if p["status"] == "posting":  # interrupted mid-upload last time
                p.update(status="failed", error="The studio closed during this upload. Check the account, then retry.")
        _save()
    jobs.on_clip_ready.append(on_clip_ready)
    threading.Thread(target=_run, daemon=True).start()
    threading.Thread(target=_stats, daemon=True).start()
    threading.Thread(target=alerts.digest_loop, args=(digest_text,), daemon=True).start()
    threading.Thread(target=alerts.keep_awake_loop,
                     args=(lambda: bool(live.active()) or any(p["status"] in OPEN for p in _posts),), daemon=True).start()
