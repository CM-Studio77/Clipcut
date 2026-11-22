import re

path = r'C:\Users\Kesha\Downloads\ai\PeakCut\web\index.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Add CSS for viral pills and sample bar
css_snippet = '''
/* Viral Tag Pills & Badges */
.vtag-pill{display:inline-flex;align-items:center;gap:3px;font-size:10px;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;padding:2px 7px;border-radius:4px;line-height:1.3;white-space:nowrap}
.vtag-hook{background:rgba(255,139,51,0.18);color:#D45B0A;border:1px solid rgba(255,139,51,0.35)}
.vtag-action{background:rgba(229,50,63,0.15);color:#D3343F;border:1px solid rgba(229,50,63,0.3)}
.vtag-funny{background:rgba(15,138,87,0.15);color:#0F8A57;border:1px solid rgba(15,138,87,0.3)}
.vtag-pro{background:rgba(99,102,241,0.15);color:#4F46E5;border:1px solid rgba(99,102,241,0.3)}
.vtag-default{background:rgba(42,26,18,0.08);color:var(--brand-ink);border:1px solid rgba(42,26,18,0.15)}

.vmeta-row{display:flex;align-items:center;justify-content:space-between;gap:6px;margin:2px 0 4px}
.vcap-pill{font-size:10px;color:var(--dim);background:var(--muted);padding:2px 6px;border-radius:4px;font-weight:600;white-space:nowrap}

/* Sample Bar */
.sample-bar{display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--brand-soft);border:1px solid var(--brand-line);border-radius:10px;margin-top:10px;font-size:12px;color:var(--brand-ink);flex-wrap:wrap}
.sample-bar b{color:var(--brand-deep)}
.sample-chip{display:inline-flex;align-items:center;gap:5px;padding:4px 12px;border-radius:999px;background:#fff;border:1px solid var(--brand-line);font-size:12px;font-weight:600;color:var(--brand-ink);cursor:pointer;transition:all .15s}
.sample-chip:hover{background:var(--brand);color:#fff;border-color:var(--brand)}
'''

if '.vtag-pill' not in c:
    c = c.replace('</style>', css_snippet + '\n</style>')

# 2. Add sample-bar to drawAdd
sample_bar_html = '''
    <div class="sample-bar">
      <span><b>⚡ Instant Demo Shorts:</b> Test 9:16 vertical viral shorts with facecam split & captions:</span>
      <button type="button" class="sample-chip" data-act="loadtechno">🎮 Techno Gamerz (GTA 6 Gameplay Viral Clips)</button>
    </div>'''

if '<div class="sample-bar">' not in c:
    c = c.replace('</div>\n    <div class="composer-opts" inert>', '</div>' + sample_bar_html + '\n    <div class="composer-opts" inert>')

# 3. Update clipHtml
old_clip_html = '''function clipHtml(j, c) {
  const m = `/media/${j.id}/`, a = `data-j="${j.id}" data-c="${esc(c.id)}"`;
  const body = c.status === "done" ? `<img src="${m}${esc(c.cover)}?v=${c.version}" alt="" loading="lazy"><span class="veil"><span>${ic("play")}</span></span>`
    : c.status === "error" ? `<span class="making" style="animation:none;color:var(--bad);background:var(--bad-soft)">Could not make this clip. Open it to try again.</span>`
    : `<span class="making">${c.status === "rendering" ? "Making this clip…" : "Waiting its turn…"}</span>`;
  const key = `c:${j.id}:${c.id}`, busyClip = c.status === "queued" || c.status === "rendering";
  return `<article class="clip ${sel().has(key) ? "picked" : ""}">
    <button class="shot" data-act="openclip" ${a} aria-label="Open clip: ${esc(c.title || c.hook)}">${body}
      <span class="badge l ${scoreCls(c.score)}" title="AI score">${c.score || "Hand"}</span><span class="badge r">${fmt(c.end - c.start)}</span></button>
    <div class="clip-body">
      <div class="hook">${esc(c.hook || "Untitled clip")}</div>
      <div class="ttl">${esc(c.title)}</div>
      ${postPills(c) ? `<div class="row" style="gap:4px">${postPills(c)}</div>` : ""}
      <div class="clip-foot">
        ${busyClip ? "" : `<label class="selck" title="Select this clip"><input type="checkbox" data-sel="${key}" ${sel().has(key) ? "checked" : ""} aria-label="Select this clip"></label>`}
        ${c.status === "done" ? `<a class="btn sm icon ghost" href="${m}${esc(c.file)}?download=1" title="Download" aria-label="Download">${ic("down")}</a>` : ""}
        <button class="btn sm icon ghost" data-act="copy" ${a} title="Copy post text" aria-label="Copy post text">${ic("copy")}</button>
        ${busyClip ? "" : `<button class="btn sm icon ghost" data-act="delclip" ${a} title="Delete this clip" aria-label="Delete this clip">${ic("trash")}</button>`}
        <span class="grow"></span>
        ${c.status === "done" ? `<button class="btn sm" data-act="openclip" ${a}>${ic("send")}Post</button>` : ""}
      </div>
    </div></article>`;
}'''

new_clip_html = '''function capName(s) {
  return {"mrbeast": "MrBeast Bold", "hormozi": "Hormozi Pop", "neon_green": "Neon Green", "clean": "Clean Minimal", "bounce": "Bounce Cyan", "hype": "Hype Red"}[s] || "MrBeast Bold";
}

function clipHtml(j, c) {
  const m = `/media/${j.id}/`, a = `data-j="${j.id}" data-c="${esc(c.id)}"`;
  const videoCover = c.thumbnailUrl || (c.cover ? `${m}${esc(c.cover)}?v=${c.version}` : "/brand/techno-thumb.jpg");
  const body = c.status === "done" ? `<img src="${videoCover}" alt="" loading="lazy"><span class="veil"><span>${ic("play")}</span></span>`
    : c.status === "error" ? `<span class="making" style="animation:none;color:var(--bad);background:var(--bad-soft)">Could not make this clip. Open it to try again.</span>`
    : `<span class="making">${c.status === "rendering" ? "Making this clip…" : "Waiting its turn…"}</span>`;
  const key = `c:${j.id}:${c.id}`, busyClip = c.status === "queued" || c.status === "rendering";
  const vScore = c.virality_score || c.score || 95;
  const tag = (c.tag || "VIRAL HOOK").toUpperCase();
  const tagClass = tag.includes("HOOK") ? "vtag-hook" : tag.includes("ACTION") || tag.includes("CLIMAX") ? "vtag-action" : tag.includes("FUNNY") ? "vtag-funny" : "vtag-pro";
  const capLabel = c.captions || capName(c.style);
  return `<article class="clip ${sel().has(key) ? "picked" : ""}">
    <button class="shot" data-act="openclip" ${a} aria-label="Open clip: ${esc(c.title || c.hook)}">${body}
      <span class="badge l ${scoreCls(vScore)}" title="Virality Score">🔥 ${vScore}</span>
      <span class="badge r">9:16 · ${fmt(c.end - c.start)}</span></button>
    <div class="clip-body">
      <div class="vmeta-row">
        <span class="vtag-pill ${tagClass}">${esc(tag)}</span>
        <span class="vcap-pill">${esc(capLabel)}</span>
      </div>
      <div class="hook">${esc(c.hook || "Untitled clip")}</div>
      <div class="ttl">${esc(c.title)}</div>
      ${postPills(c) ? `<div class="row" style="gap:4px">${postPills(c)}</div>` : ""}
      <div class="clip-foot">
        ${busyClip ? "" : `<label class="selck" title="Select this clip"><input type="checkbox" data-sel="${key}" ${sel().has(key) ? "checked" : ""} aria-label="Select this clip"></label>`}
        ${c.status === "done" ? `<a class="btn sm icon ghost" href="${c.videoUrl || (m + esc(c.file) + '?download=1')}" download title="Download" aria-label="Download">${ic("down")}</a>` : ""}
        <button class="btn sm icon ghost" data-act="copy" ${a} title="Copy post text" aria-label="Copy post text">${ic("copy")}</button>
        ${busyClip ? "" : `<button class="btn sm icon ghost" data-act="delclip" ${a} title="Delete this clip" aria-label="Delete this clip">${ic("trash")}</button>`}
        <span class="grow"></span>
        ${c.status === "done" ? `<button class="btn sm" data-act="openclip" ${a}>${ic("send")}Post</button>` : ""}
      </div>
    </div></article>`;
}'''

if old_clip_html in c:
    c = c.replace(old_clip_html, new_clip_html)
else:
    print("Warning: old_clip_html not found exactly")

# 4. Update stage video src in drawClipDlg
old_stage = 'const stage = c.status === "done" ? `<video src="${m}${esc(c.file)}?v=${c.version}" poster="${m}${esc(c.cover)}?v=${c.version}" controls autoplay playsinline></video>`'
new_stage = 'const videoSrc = c.videoUrl || (`${m}${esc(c.file)}?v=${c.version}`); const posterSrc = c.thumbnailUrl || (`${m}${esc(c.cover)}?v=${c.version}`); const stage = c.status === "done" ? `<video src="${videoSrc}" poster="${posterSrc}" controls autoplay playsinline></video>`'

if old_stage in c:
    c = c.replace(old_stage, new_stage)

# 5. Add loadtechno action handler
if 'a === "loadtechno"' not in c:
    c = c.replace('if (a === "feedback") {', '''if (a === "loadtechno") {
      $("#url").value = "https://youtu.be/1O_GCgCu-j4";
      toast("Loaded Techno Gamerz GTA 6 link. Click 'Make clips' to generate viral shorts!", "ok");
      return;
    }
    if (a === "feedback") {''')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("Applied virality frontend enhancements to web/index.html successfully!")
