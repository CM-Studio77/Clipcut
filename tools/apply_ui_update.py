import re

path = r'C:\Users\Kesha\Downloads\ai\PeakCut\web\index.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update const I to include calendar
if '"calendar":' not in c:
    c = c.replace('"money":', '"calendar": "<path d=\\"M208,32H184V24a8,8,0,0,0-16,0v8H88V24a8,8,0,0,0-16,0v8H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM72,48v8a8,8,0,0,0,16,0V48h80v8a8,8,0,0,0,16,0V48h24V80H48V48ZM208,208H48V96H208V208Z\\"/>",\n "money":')

# 2. Update .side-head markup
old_sh = '''<div class="side-head"><img class="logo" src="/brand/logo-light.svg" alt="PeakCut"><img class="mark" src="/brand/favicon.svg" alt="PeakCut">
      <button class="icon-btn collapse" data-act="collapse" id="collapseBtn" aria-label="Collapse sidebar"></button></div>'''
new_sh = '''<div class="side-head">
      <div class="brand-link" data-act="go" data-v="overview" title="Peak Cut Home">
        <img class="mark" src="/brand/favicon.svg" alt="Peak Cut">
        <span class="brand-title">Peak Cut</span>
      </div>
      <button class="icon-btn collapse" data-act="collapse" id="collapseBtn" aria-label="Collapse sidebar"></button>
    </div>'''
if old_sh in c:
    c = c.replace(old_sh, new_sh)
else:
    print("Warning: old_sh not found exactly")

# 3. Add CSS for header pill buttons, suggested streamers, and empty state
css_to_add = '''
/* Header pill buttons matching live screenshot */
.hdr-pill-btn{display:inline-flex;align-items:center;gap:8px;height:36px;padding:0 16px;border-radius:9999px;background:#ffffff;border:1px solid #E5E7EB;color:#1F2937;font-size:13px;font-weight:600;cursor:pointer;box-shadow:0 1px 2px rgba(0,0,0,0.04);transition:all .15s ease}
.hdr-pill-btn:hover{background:#F9FAFB;border-color:#D1D5DB;color:#111827}
.hdr-pill-btn svg{width:16px;height:16px;flex:none}
.hdr-pill-icons{display:inline-flex;align-items:center;gap:3px}
.hdr-pill-icons svg{display:block;border-radius:3px}

/* Side head branding */
.side-head .brand-link{display:flex;align-items:center;gap:10px;text-decoration:none;cursor:pointer;flex:1;min-width:0}
.side-head .mark{display:block;width:34px;height:34px;border-radius:8px;flex:none}
.side-head .brand-title{font-size:20px;font-weight:700;color:#ffffff;letter-spacing:-0.02em;font-family:system-ui,-apple-system,BlinkMacSystemFont,'Geist','Segoe UI',sans-serif;white-space:nowrap}
.app.mini .side-head .brand-title{display:none}

/* Suggested streamers in sidebar */
.suggest-item{display:flex;align-items:center;gap:8px;padding:5px 8px;border-radius:8px;color:var(--frame-text);font-size:13px;transition:background .12s}
.suggest-item:hover{background:rgba(255,255,255,0.05)}
.suggest-item .avatar{width:24px;height:24px;border-radius:50%;object-fit:cover;flex:none}
.suggest-item .sname{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500;color:var(--frame-text)}
.badge-live-pill{display:inline-flex;align-items:center;gap:4px;padding:2px 7px;border-radius:999px;background:rgba(229,50,63,0.22);color:#FF5A65;font-size:10px;font-weight:700;flex:none;line-height:1.2}
.badge-live-pill::before{content:"";display:inline-block;width:5px;height:5px;border-radius:50%;background:#FF4450}
.suggest-item .btn-add{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:4px;background:rgba(255,255,255,0.08);color:var(--frame-dim);border:0;cursor:pointer;font-size:14px;font-weight:600;transition:all .15s}
.suggest-item .btn-add:hover{background:rgba(255,255,255,0.2);color:#fff}
.app.mini .suggest-item{justify-content:center;padding:4px 0}
.app.mini .suggest-item .sname,.app.mini .suggest-item .badge-live-pill,.app.mini .suggest-item .btn-add{display:none}

/* Enhanced Empty State */
.empty{border:1px dashed #E5E0DB;border-radius:16px;padding:60px 20px;text-align:center;color:var(--dim);display:flex;flex-direction:column;align-items:center;gap:6px;background:#ffffff}
.empty img{width:64px;height:64px;border-radius:14px;margin-bottom:8px}
.empty b{display:block;color:#1E1612;font-size:18px;font-weight:700}
.empty span{font-size:14px;color:#6D6159;max-width:460px;line-height:1.5}
'''

if '/* Header pill buttons matching live screenshot */' not in c:
    c = c.replace('</style>', css_to_add + '\n</style>')

# 4. Replace drawShell and ROUTES
idx1 = c.find('function drawShell()')
idx2 = c.find('function pathFor(', idx1)

new_draw_shell = '''function drawShell() {  const nav = (v, icon, label, extra = "") => `<button class="nav-item ${S.view === v ? "on" : ""}" data-act="go" data-v="${esc(v)}" title="${esc(label)}">${icon}<span class="label">${esc(label)}</span>${extra}</button>`;
  put($("#nav"), nav("overview", navIc("home", "overview"), "Home") +
    nav("library", navIc("film", "library"), "All videos", (() => { const w = S.jobs.filter(j => ["queued", "running"].includes(j.status)).length;
      return w ? `<span class="working" title="${w} working now"><i></i>${w} working</span>` : S.jobs.length ? `<span class="count">${S.jobs.length}</span>` : ""; })()) +
    nav("streamers", ic("radio"), "Streamers", `<span class="count">1</span>`) +
    nav("campaigns", ic("money"), "Campaigns", `<span class="count">1</span>`) +
    nav("schedule", ic("calendar"), "Schedule") +
    `<h4><span>Your streamers</span></h4>` +
    S.creators.map(c => nav("c:" + c.id, cav(c), c.name,
      c.live_job ? `<span class="sb-tag rec" title="Recording now"><i></i>Rec</span>`
        : liveOn(c).length ? `<span class="sb-tag" title="Live on ${esc(liveOn(c).map(([k]) => PLAT[k].name).join(" and "))}"><i></i>Live</span>` : "")).join("") +
    `<h4><span>Suggested for you</span></h4>` +
    `<div class="suggest-item">
      <img class="avatar" src="/brand/jasontheween.jpg" alt="JasonTheWeen" onerror="this.src='/brand/favicon.svg'">
      <span class="sname" title="JasonTheWeen">JasonTh...</span>
      <span class="badge-live-pill">Live</span>
      <button class="btn-add" data-act="addsuggested" data-name="JasonTheWeen" data-ch="https://www.youtube.com/@jasontheween" title="Add JasonTheWeen">+</button>
    </div>
    <div class="suggest-item">
      <img class="avatar" src="/brand/tfue.jpg" alt="Tfue" onerror="this.src='/brand/favicon.svg'">
      <span class="sname" title="Tfue">Tfue</span>
      <span class="badge-live-pill">Live</span>
      <button class="btn-add" data-act="addsuggested" data-name="Tfue" data-ch="https://www.youtube.com/@Tfue" title="Add Tfue">+</button>
    </div>` +
    (S.status.user?.role === "admin" && S.status.accounts !== false ? `<h4><span>Owner</span></h4><a class="nav-item" href="/admin" title="Admin dashboard" style="text-decoration:none">${ic("shield")}<span class="label">Admin dashboard</span></a>` : ""));
  const st = S.status;
  const k = S.status.ai;
  put($("#foot"), (k ? `<button class="ai-card ${S.view === "usage" ? "on" : ""}" data-act="go" data-v="usage" title="${k.ready ? `AI: ${esc(k.provider || "ready")}, ${k.today_calls || 0} calls today` : "The AI is not set up"}">
      <span class="ai-ic">${ic("bolt")}</span><span class="ai-tx"><small>AI</small><b>${k.ready ? esc(k.provider || "Ready") : "Not set up"}</b></span>${k.ready ? `<span class="ai-n">${(k.today_calls || 0).toLocaleString()} today</span>` : ""}</button>` : "") +
    (S.status.user ? `<div class="me"><button class="me-btn" data-act="acctmenu" aria-haspopup="menu" aria-expanded="false">${meAvatar(S.status.user)}
      <span class="who">${S.status.accounts === false ? `<b>Settings</b><span>AI key, connected apps</span>` : `<b>${esc(S.status.user.name)}</b><span>${esc(S.status.user.email)}</span>`}</span></button>
      <button class="icon-btn bell" data-act="bell" title="Notifications" aria-label="Notifications${S.status.unread ? `, ${S.status.unread} new` : ""}" aria-haspopup="dialog">${ic("bell")}${S.status.unread ? `<span class="dotn">${S.status.unread > 9 ? "9+" : S.status.unread}</span>` : ""}</button></div>` : ""));
  const c = creator();
  const recording = S.creators.filter(x => x.live_job).length;
  let title = {overview:"Home", library:"All videos", streamers:"Streamers", campaigns:"Campaigns", schedule:"Schedule", settings:"Settings", usage:"AI usage"}[S.view] || "", sub = "", act = "";
  if (S.view === "usage") sub = "What the AI has been used for.";
  if (S.view === "overview") sub = "Every video and recording.";
  if (S.view === "library") sub = "Every video and recording.";
  if (S.view === "streamers") sub = "Manage connected streamers, channels and recordings.";
  if (S.view === "campaigns") sub = "Track campaigns, views, and clip performance.";
  if (S.view === "schedule") sub = "Scheduled posts across connected social platforms.";
  if (S.view === "settings") sub = (S.status.accounts === false ? "Your AI key and connected apps." : "Your profile, security and connected apps.");
  let pic = "", subHtml = null, tabs = "";
  if (c) {
    title = c.name;
    pic = cav(c);
    subHtml = statusBadge(c);
    const nJobs = S.jobs.filter(j => j.creator === c.id).length, nLog = (c.log || []).length;
    tabs = [["clips", "Clips", "scissors", nJobs], ["setup", "Setup", "cog", 0], ["activity", "Activity", "clock", nLog]].map(([k, l, i, n]) =>
      `<button class="tabbtn ${S.ctab === k ? "on" : ""}" data-act="tab" data-t="${k}" role="tab" aria-selected="${S.ctab === k}">${ic(i)}${l}${n ? `<span class="n">${n > 99 ? "99+" : n}</span>` : ""}</button>`).join("");
    act = c.live_job ? `<button class="btn danger" data-act="stoplive" data-j="${esc(c.live_job)}">${ic("stop")}Stop recording</button>`
                     : `<button class="btn primary" data-act="golive"><span class="rdot"></span>${liveOn(c).length ? "Record live stream" : "Start recording"}</button>`;
  }
  if (["overview", "library", "streamers", "campaigns", "schedule"].includes(S.view)) {
    act = `<button class="hdr-pill-btn" data-act="go" data-v="settings" data-tab="apps" title="Connect apps">
      <span class="hdr-pill-icons">
        <svg width="16" height="16" viewBox="0 0 24 24"><rect width="24" height="24" rx="5" fill="#FF0000"/><polygon points="9.5,7.5 16.5,12 9.5,16.5" fill="#FFFFFF"/></svg>
        <svg width="16" height="16" viewBox="0 0 24 24"><rect width="24" height="24" rx="5" fill="#000000"/><path d="M16.5 9.2a4.5 4.5 0 0 1-3.2-1.4V14a3.8 3.8 0 1 1-3.8-3.8c.4 0 .8.1 1.2.2V13a1.8 1.8 0 1 0 1.8 1.8V5.5h2.2a4.4 4.4 0 0 0 4.1 3.7v2z" fill="#FFFFFF"/></svg>
      </span>
      <span>Connect apps</span>
    </button>
    <button class="hdr-pill-btn" data-act="feedback" title="Feedback">
      ${ic("chat")}
      <span>Feedback</span>
    </button>`;
  }
  const me = S.status.user;
  const kk = S.status.ai;
  const up = S.status.update;
  let upSeen = "";
  try { upSeen = localStorage.getItem("peakcut_update_seen") || ""; } catch {}
  const upBar = up && up.latest !== upSeen ? `<div class="vb" role="status">${ic("up")}<span>${up.restart ? "<b>The new version is downloaded.</b> Close PeakCut and start it again to use it." : `A new version of PeakCut is out${up.behind ? `: <b>${up.behind} update${up.behind === 1 ? "" : "s"}</b> since yours` : ""}.`}</span>
    <button class="btn sm primary" data-act="updhow">${up.restart ? "What's new" : "How to update"}</button><button class="btn sm ghost" data-act="updlater" aria-label="Hide until the next version">Later</button></div>` : "";
  const toolBar = S.status.no_ffmpeg ? `<div class="vb" role="alert">${ic("warn")}<span><b>PeakCut can't make clips yet: ffmpeg isn't installed on this computer.</b> Open a terminal, run <code>winget install Gyan.FFmpeg</code> (Mac: <code>brew install ffmpeg</code>, Linux: <code>sudo apt install ffmpeg</code>), then close PeakCut and start it again.</span></div>` : "";
  const aiBar = !toolBar && S.status.ai?.problem && me?.is_admin && S.view !== "settings" ? `<div class="vb" role="status">${ic("warn")}<span><b>The AI isn't answering.</b> ${esc(S.status.ai.problem)} Until then, clips are picked by loudness.</span><button class="btn sm primary" data-act="go" data-v="settings" data-tab="ai">Open AI settings</button></div>` : "";
  const diskBar = !toolBar && S.status.disk_full && S.view !== "settings" ? `<div class="vb" role="alert">${ic("warn")}<span><b>The drive PeakCut saves to is almost full, so it can't take new videos.</b> Free up space on it, or move PeakCut's folder to a bigger drive.</span>${me?.is_admin ? `<button class="btn sm primary" data-act="go" data-v="settings" data-tab="storage">Open Storage</button>` : ""}</div>` : "";
  put($("#vbanner"), toolBar ? toolBar : diskBar ? diskBar : aiBar ? aiBar : upBar ? upBar : me && me.verified === false ? `<div class="vb" role="status">${ic("warn")}<span>Confirm your email to start clipping. We sent a link to <b>${esc(me.email)}</b>.</span><button class="btn sm" data-act="resendverify">Send a new link</button></div>`
    : kk && kk.ready === false && S.view !== "usage" ? `<div class="vb" role="status">${ic("bolt")}<span>${me?.is_admin ? "Add your AI key to let the AI pick clips and write titles. Until then, clips are picked by loudness." : "The AI isn't set up on this server yet, so clips are picked by loudness."}</span>${me?.is_admin && S.view !== "settings" ? `<button class="btn sm primary" data-act="go" data-v="settings" data-tab="ai">${ic("plus")}Add AI key</button>` : ""}</div>` : "");
  put($("#tpic"), pic); $("#tpic").classList.toggle("live", !!(c && (c.live_job || liveOn(c).length)));
  put($("#utabs"), tabs); moveInd(); $(".topbar").classList.toggle("tabbed", !!tabs);
  put($("#title"), `<span>${esc(title)}</span>`); put($("#subtitle"), subHtml ?? esc(sub)); put($("#actions"), act);
}

const ROUTES = {overview: "", library: "videos", streamers: "streamers", campaigns: "campaigns", schedule: "schedule", settings: "settings", usage: "usage"};
'''
c = c[:idx1] + new_draw_shell + c[idx2 + len('function pathFor('):]
# restore function pathFor(
c = c[:idx1 + len(new_draw_shell)] + 'function pathFor(' + c[idx1 + len(new_draw_shell):]

# 5. Update picker in drawAdd
c = c.replace('picker("o_creator", "File under creator", [{v:"", label:"No creator"',
              'picker("o_creator", "File under streamer", [{v:"", label:"No streamer"')

# 6. Update empty state in drawJobs
c = c.replace('<b>${cid ? "No clips for this creator yet" : "No videos yet"}</b>${cid ? "Start recording their stream, or paste a link to one of their videos above." : "Paste a link above and the studio will find the best moments and turn them into clips."}',
              '<b>${cid ? "No clips for this streamer yet" : "No videos yet"}</b><span>${cid ? "Start recording their stream, or paste a link to one of their videos above." : "Paste a link above and the studio will find the best moments and turn them into clips."}</span>')

# 7. Update go() routing for streamers, campaigns, schedule
old_go_views = '''if (v === "overview") view.innerHTML = `<div id="ov"></div>`;
  else if (v === "library") view.innerHTML = `<div id="add"></div><div id="jobs"></div>`;
  else if (v === "settings") view.innerHTML = `<div id="sform"></div>`;'''

new_go_views = '''if (v === "overview") view.innerHTML = `<div id="ov"></div>`;
  else if (v === "library") view.innerHTML = `<div id="add"></div><div id="jobs"></div>`;
  else if (v === "streamers") { view.innerHTML = `<div id="streamersView"></div>`; drawStreamersView(); }
  else if (v === "campaigns") { view.innerHTML = `<div id="campaignsView"></div>`; drawCampaignsView(); }
  else if (v === "schedule") { view.innerHTML = `<div id="scheduleView"></div>`; drawScheduleView(); }
  else if (v === "settings") view.innerHTML = `<div id="sform"></div>`;'''

if old_go_views in c:
    c = c.replace(old_go_views, new_go_views)
else:
    print("Warning: old_go_views not matched exactly")

# 8. Add implementations for drawStreamersView, drawCampaignsView, drawScheduleView
views_impl = '''
function drawStreamersView() {
  const root = $("#streamersView"); if (!root) return;
  root.innerHTML = `<div style="display:flex;flex-direction:column;gap:20px;padding:10px 0">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px">
      ${S.creators.map(c => `
        <div class="card" style="padding:18px;display:flex;align-items:center;gap:16px;border-radius:14px">
          ${cav(c)}
          <div style="flex:1;min-width:0">
            <b style="display:block;font-size:16px;color:var(--text);margin-bottom:4px">${esc(c.name)}</b>
            <div style="display:flex;align-items:center;gap:6px">${statusBadge(c)}</div>
          </div>
          <button class="btn sm primary" data-act="go" data-v="c:${esc(c.id)}">Open</button>
        </div>
      `).join("")}
      <button class="card" data-act="newcreator" style="padding:18px;display:flex;align-items:center;justify-content:center;gap:10px;border:2px dashed var(--line-2);border-radius:14px;background:transparent;cursor:pointer">
        ${ic("plus")}<b>Add new streamer</b>
      </button>
    </div>
  </div>`;
}

function drawCampaignsView() {
  const root = $("#campaignsView"); if (!root) return;
  root.innerHTML = `<div style="display:flex;flex-direction:column;gap:20px;padding:10px 0">
    <div class="tiles">
      <div class="tile"><i>${ic("money")}</i><b>$0.00</b><span>Est. clip rewards</span></div>
      <div class="tile"><i>${ic("film")}</i><b>${S.jobs.length}</b><span>Clips active</span></div>
      <div class="tile"><i>${ic("eye")}</i><b>0</b><span>Campaign views</span></div>
      <div class="tile"><i>${ic("crown")}</i><b>Tier 1</b><span>Creator level</span></div>
    </div>
    <div class="card" style="padding:24px;border-radius:14px">
      <div class="card-head"><div><h2>Affiliate & Sponsorship Campaigns</h2><p class="sub">Earn rewards by clipping popular streamer moments</p></div></div>
      <div style="display:flex;flex-direction:column;gap:12px;margin-top:16px">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:16px;border-radius:12px;background:var(--muted)">
          <div style="display:flex;align-items:center;gap:14px">
            <img src="/brand/favicon.svg" style="width:40px;height:40px;border-radius:10px">
            <div><b style="font-size:15px;color:var(--brand-ink)">PeakCut Creator Boost Campaign</b><div style="font-size:13px;color:var(--dim)">Earn $5.00 per 10,000 views on YouTube Shorts & TikTok clips.</div></div>
          </div>
          <span class="pill ok">Active</span>
        </div>
      </div>
    </div>
  </div>`;
}

function drawScheduleView() {
  const root = $("#scheduleView"); if (!root) return;
  root.innerHTML = `<div style="display:flex;flex-direction:column;gap:20px;padding:10px 0">
    <div class="card" style="padding:24px;border-radius:14px">
      <div class="card-head"><div><h2>Publishing Schedule</h2><p class="sub">Manage automated publishing queues and upcoming schedules</p></div>
        <button class="btn primary" data-act="go" data-v="settings" data-tab="apps">Manage accounts</button>
      </div>
      <div style="padding:48px 20px;text-align:center;color:var(--dim)">
        <div style="font-size:40px;margin-bottom:12px">${ic("calendar")}</div>
        <b style="font-size:16px;color:var(--text);display:block;margin-bottom:4px">No scheduled posts</b>
        <p style="font-size:14px;margin:0">Create clips and choose a publishing schedule to automate posting.</p>
      </div>
    </div>
  </div>`;
}
'''
if 'function drawStreamersView()' not in c:
    c = c.replace('function drawOverview()', views_impl + '\nfunction drawOverview()')

# 9. Add click handlers for feedback and addsuggested
click_handlers = '''
    if (a === "feedback") {
      const dlg = $("#formdlg");
      dlg.innerHTML = `<div class="dlg-box" style="max-width:440px">
        <div class="dlg-head"><h3>Feedback & Support</h3><button class="icon-btn" data-act="dlgclose">${ic("x")}</button></div>
        <div style="padding:16px 20px;display:flex;flex-direction:column;gap:14px">
          <p style="font-size:14px;color:var(--dim);margin:0">Tell us what you think of PeakCut, or report any issues you run into.</p>
          <textarea id="feedbackText" rows="4" placeholder="What's on your mind?..." style="width:100%;border:1px solid var(--line-2);border-radius:10px;padding:12px;font-family:inherit;font-size:14px;resize:vertical"></textarea>
          <div style="display:flex;justify-content:flex-end;gap:10px">
            <button class="btn" data-act="dlgclose">Cancel</button>
            <button class="btn primary" data-act="sendfeedback">Send feedback</button>
          </div>
        </div>
      </div>`;
      dlg.showModal();
      return;
    }
    if (a === "sendfeedback") {
      toast("Thank you for your feedback!", "ok");
      $("#formdlg").close();
      return;
    }
    if (a === "addsuggested") {
      b.disabled = true;
      try {
        await send("/api/creators", {name: d.name, channel: d.ch, channels: {youtube: d.ch}});
        await tick();
        toast("Added " + d.name + " to your streamers!", "ok");
      } catch (err) {
        toast(err.message, "bad");
      } finally {
        b.disabled = false;
      }
      return;
    }
'''
if 'if (a === "feedback")' not in c:
    c = c.replace('if (a === "go") { closePops(); return go(d.v, d.tab); }',
                  'if (a === "go") { closePops(); return go(d.v, d.tab); }' + click_handlers)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("Successfully applied UI update to web/index.html! New length:", len(c))
