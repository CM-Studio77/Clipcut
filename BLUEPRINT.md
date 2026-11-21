# CLIPCUT AI STUDIO — WORKSTATION ARCHITECTURAL BLUEPRINT & UI/UX SPECIFICATION

**Document Version**: 2.5.0-PRO  
**Target Milestone**: Milestone 1 (Architectural Blueprint & Design System Specification)  
**Workspace Directory**: `C:\Users\Kesha\Downloads\ai\PeakCut`  
**Status**: APPROVED SPECIFICATION  
**Primary Deliverable For**: PeakCut AI Creator Workstation Transformation  

---

## 1. Executive Summary & Design Vision

### 1.1 The Transformation Imperative
PeakCut (PeakCut) is transitioning from a traditional, fragmented multi-page web application into a **unified, high-density, pro-grade AI Studio Workstation**. Previously, video clipping, live stream monitoring, telemetry analysis, human approval, and social media publishing operated across disconnected routes (`/app/live-studio`, `/app/approval`, `/app/history`, and creator sub-tabs). This disjointed layout imposed significant cognitive friction, requiring creators and editors to constantly toggle views, lose track of real-time stream events, and wait on non-co-located interfaces.

The next-generation PeakCut Workstation introduces an **ergonomic, multi-pane Command Center** tailored for high-volume content creators, gaming broadcasters, and social video editing teams. Broadcasters can monitor raw 16:9 live streams, preview synchronized 9:16 vertical shorts in real time, observe instant audio loudness jumps and chat sentiment velocity, inspect multimodal AI highlight candidates on an interactive multi-track timeline, and dispatch approved shorts across TikTok, YouTube Shorts, Instagram Reels, and Facebook Reels in a single click—all within a unified, responsive interface.

### 1.2 Core Architectural Principles
1. **Zero-Latency Ergonomic Density**: Maximize actionable surface area. High-frequency telemetry (loudness meters, chat velocity bursts, AI virality scores) and preview canvases are co-located so the user never leaves the live monitoring cockpit.
2. **Autonomous AI with Human-in-the-Loop Sovereign Control**: The workstation continuously ingests audio, chat, and video frames, evaluating virality via multimodal fusion algorithms. However, final publishing authority rests firmly with the creator through an approval queue dock equipped with instant 1-click publishing.
3. **Dark Cyber / Obsidian-Glass Aesthetic**: Replace all legacy warm brown/orange styling with a cold, deep obsidian glassmorphism design system. High-contrast typography, hardware-accelerated translucent glass panels, specular gradient edge-sheens, and a disciplined 5-color neon accent matrix provide immediate visual hierarchy without eye fatigue during marathon streaming sessions.
4. **Preservation of System Contracts**: Total adherence to existing DOM IDs, data attributes, API endpoint contracts, and JavaScript function signatures (`drawLiveStudio`, `drawApprovalCenter`, `drawPubHistory`, `fb_tokensave`). Upgrading the interface does not break existing test suites or backend synchronization loops.

---

## 2. Dark Cyber / Obsidian-Glass Design System Specification

### 2.1 Color Tokens & Palette Architecture

The design system eradicates all legacy warm chocolate and orange-brown hex codes (`#1E1612`, `#120D0A`, `#2A1A12`, `#17110E`, `#1F140D`, `#3A2C25`, `#352a24`) found in older templates. In their place is a cold, deep obsidian scale engineered with subtle blue-gray undertones for maximum contrast against glowing neon indicators.

```css
:root {
  /* ==========================================================================
     1. DEEP OBSIDIAN PALETTE (Base, Surface, & Elevation)
     ========================================================================== */
  --obsidian-0:   #050608;  /* Deepest viewport letterbox & media container base */
  --obsidian-50:  #0a0b10;  /* Application canvas shell & root background */
  --obsidian-100: #0f111a;  /* Workstation primary background */
  --obsidian-200: #151824;  /* Primary dock, pane, & sidebar surface */
  --obsidian-300: #1b1f2e;  /* Elevated cards, interactive tiles, & inspector drawers */
  --obsidian-400: #24293d;  /* Active hover states, panel headers, & prominent surfaces */
  --obsidian-500: #333a54;  /* Subdued structural borders & segment separators */

  /* ==========================================================================
     2. GLASSMORPHISM SURFACE OVERLAYS (Translucent Layers)
     ========================================================================== */
  --glass-canvas: rgba(10, 11, 16, 0.88);  /* Full-page overlays & main canvas */
  --glass-panel:  rgba(21, 24, 36, 0.72);  /* Workstation pane backgrounds */
  --glass-card:   rgba(27, 31, 46, 0.65);  /* Interactive cards & preview containers */
  --glass-dock:   rgba(15, 17, 26, 0.85);  /* Floating command header & bottom approval dock */
  --glass-modal:  rgba(21, 24, 36, 0.94);  /* Modal dialogs & full-screen inspectors */

  /* Glass Borders & Specular Sheen Gradients */
  --border-glass-subtle:   rgba(255, 255, 255, 0.06);
  --border-glass:          rgba(255, 255, 255, 0.09);
  --border-glass-highlight: rgba(255, 255, 255, 0.16);
  --specular-sheen:        linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.00) 100%);
  --specular-active:       linear-gradient(180deg, rgba(255, 255, 255, 0.16) 0%, rgba(255, 255, 255, 0.02) 100%);
}
```

---

### 2.2 Glassmorphism, Specular Highlights & Depth Matrix

To avoid the cheap "flat dark" look, surfaces employ layered backdrop filters, specular pseudo-element highlights, directional gradient borders, and multi-stage shadow elevations.

#### Depth & Shadow Scales
```css
:root {
  /* Backdrop Blur Radii */
  --blur-subtle: blur(10px);
  --blur-md:     blur(16px);
  --blur-lg:     blur(24px);
  --blur-xl:     blur(36px);

  /* Elevation Shadows */
  --shadow-dock:    0 12px 32px -4px rgba(0, 0, 0, 0.70), 0 0 1px rgba(255, 255, 255, 0.12);
  --shadow-card:    0 8px 24px -2px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(255, 255, 255, 0.08);
  --shadow-hover:   0 14px 36px -4px rgba(0, 0, 0, 0.75), 0 0 16px rgba(0, 243, 255, 0.08);
  --shadow-popover: 0 20px 48px -6px rgba(0, 0, 0, 0.85), 0 0 0 1px rgba(255, 255, 255, 0.14);

  /* Corner Radii */
  --r-xs:   4px;
  --r-sm:   8px;
  --r-md:   12px;
  --r-lg:   16px;
  --r-xl:   20px;
  --r-pill: 9999px;

  /* Z-Index Hierarchy */
  --z-base:    1;    /* Canvas base & stationary content */
  --z-panel:   10;   /* Workstation panes & docked containers */
  --z-dock:    20;   /* Sticky command header & bottom approval bar */
  --z-header:  30;   /* Workstation global navigation header */
  --z-overlay: 40;   /* Scrub timeline hover tooltips & video guides */
  --z-popover: 50;   /* Dropdown menus & notifications flyout */
  --z-modal:   100;  /* Native <dialog> inspectors & modal backdrops */
  --z-toast:   200;  /* Ephemeral alert toasts */
}
```

#### Glassmorphism Container Implementation Rule
All cards and panels must implement hardware-accelerated glassmorphism with top-edge specular illumination:

```css
.obsidian-card {
  position: relative;
  background: var(--glass-card);
  backdrop-filter: var(--blur-md);
  -webkit-backdrop-filter: var(--blur-md);
  border: 1px solid var(--border-glass);
  border-radius: var(--r-lg);
  padding: 18px 20px;
  box-shadow: var(--shadow-card);
  transition: border-color 0.22s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.22s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

/* Specular top-edge lighting simulation */
.obsidian-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--specular-sheen);
  pointer-events: none;
}

.obsidian-card:hover {
  border-color: var(--border-glass-highlight);
  box-shadow: var(--shadow-hover);
  transform: translateY(-1px);
}
```

---

### 2.3 The 5-Neon Accent Matrix

To deliver instantaneous status comprehension across dense telemetry streams, five dedicated neon accent channels are established. Each neon accent possesses its own primary token, soft translucent fill, glowing aura, and border definition.

```css
:root {
  /* ==========================================================================
     3. 5-NEON ACCENT MATRIX
     ========================================================================== */

  /* NEON 1: CYBER CYAN (#00f3ff)
     Role: Primary AI actions, active stream monitoring, audio energy, primary buttons */
  --cyan-primary: #00f3ff;
  --cyan-glow:    rgba(0, 243, 255, 0.38);
  --cyan-soft:    rgba(0, 243, 255, 0.12);
  --cyan-border:  rgba(0, 243, 255, 0.42);

  /* NEON 2: MATRIX EMERALD (#00ff9d)
     Role: Viral Virality (>90%), Approval Confirmation, System Sync OK, Success */
  --emerald-primary: #00ff9d;
  --emerald-glow:    rgba(0, 255, 157, 0.38);
  --emerald-soft:    rgba(0, 255, 157, 0.12);
  --emerald-border:  rgba(0, 255, 157, 0.42);

  /* NEON 3: ELECTRIC VIOLET (#a855f7)
     Role: Multimodal AI Context Fusion, Facecam Split tracking, Speech NLP, Hinglish ASR */
  --violet-primary: #a855f7;
  --violet-glow:    rgba(168, 85, 247, 0.38);
  --violet-soft:    rgba(168, 85, 247, 0.14);
  --violet-border:  rgba(168, 85, 247, 0.42);

  /* NEON 4: NEON AMBER (#ffb700)
     Role: Pending Review Items, Mid-Virality (80-89%), Audio Peak Warning, Queued Posts */
  --amber-primary: #ffb700;
  --amber-glow:    rgba(255, 183, 0, 0.38);
  --amber-soft:    rgba(255, 183, 0, 0.12);
  --amber-border:  rgba(255, 183, 0, 0.42);

  /* NEON 5: CRITICAL CRIMSON (#ff3366)
     Role: ON AIR Live Broadcast Pulse, Audio Loudness Clipping Spike, Dismiss/Reject Action */
  --crimson-primary: #ff3366;
  --crimson-glow:    rgba(255, 51, 102, 0.42);
  --crimson-soft:    rgba(255, 51, 102, 0.14);
  --crimson-border:  rgba(255, 51, 102, 0.48);
}
```

#### Accent Matrix Semantic Allocation Table

| Neon Color | Hex Value | Primary Workstation Role | Typical UI Component |
|---|---|---|---|
| **Cyber Cyan** | `#00f3ff` | Active Stream Intake & Controls | `#live_start_btn`, `.btn-cyber-primary`, Active scrubbing head, VU Meter normal zone |
| **Matrix Emerald** | `#00ff9d` | High Virality & Publishing Success | Virality scores `≥ 90%`, `submitApprove()` confirmation button, System health OK badge |
| **Electric Violet** | `#a855f7` | Multimodal AI & Facecam Tracking | Facecam split indicator, ASR Hinglish speech transcript chips, AI decision log |
| **Neon Amber** | `#ffb700` | Staging & Cautionary Telemetry | Approval pending badge count, Virality scores `80% - 89%`, Scheduled queue counter |
| **Critical Crimson** | `#ff3366` | Live Broadcast & Loudness Climax | `.status-pill.on-air`, Loudness spikes `> -6 dBFS`, Chat surge `> 3x`, `submitReject()` |

---

### 2.4 Technical Typography & Numeric Telemetry Scale

```css
:root {
  /* Font Family Stacks */
  --font-sans:    "Geist", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono:    "JetBrains Mono", "Geist Mono", "SF Mono", monospace;
  --font-display: "Space Grotesk", "Geist", sans-serif;

  /* Text Color Scales */
  --text-high:   #f8fafc;  /* 98% Light: Headings, active values, button labels */
  --text-medium: #cbd5e1;  /* 80% Light: Body descriptions, input values, subtitles */
  --text-dim:    #94a3b8;  /* 60% Light: Metadata labels, secondary counts, tooltips */
  --text-muted:  #64748b;  /* 40% Light: Inactive placeholders, disabled icons */
  --text-ghost:  #475569;  /* 30% Light: Grid lines, ticks, subtle borders */
}
```

#### Typographic Scale & Rules
- **Display Metric (Virality Score & Loudness dB)**: `font-family: var(--font-display); font-size: 26px; font-weight: 700; line-height: 1; letter-spacing: -0.03em;`
- **Workstation Section Header (H1)**: `font-family: var(--font-sans); font-size: 20px; font-weight: 700; letter-spacing: -0.02em; color: var(--text-high);`
- **Component Pane Header (H2)**: `font-family: var(--font-sans); font-size: 14px; font-weight: 600; letter-spacing: -0.01em; color: var(--text-high);`
- **Overline / Category Tag**: `font-family: var(--font-mono); font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-dim);`
- **Numeric Telemetry / Tabular Data**: `font-family: var(--font-mono); font-variant-numeric: tabular-nums; font-size: 12px; font-weight: 500;`
- **Uppercase Telemetry Pills**: `display: inline-flex; align-items: center; gap: 6px; padding: 3px 8px; border-radius: var(--r-pill); font-family: var(--font-mono); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;`

---

## 3. Workstation Layout Architecture & Component Arrangement

The workstation transforms the browser window into a unified, high-density 5-Zone command cockpit.

### 3.1 Comprehensive ASCII Wireframes Across Breakpoints

#### A. Ultra-Wide Command Center (Display Width ≥ 1680px)
On ultra-wide monitors (1440p / 4K / 21:9 ultrawide), the layout features a 3-column top stage with co-located 16:9 monitor and 9:16 vertical shorts canvas, side telemetry decks, a full-width interactive scrub timeline, and a horizontal approval dock.

```
+=======================================================================================================================================================+
| [LOGO] CLIPCUT AI STUDIO PRO // WORKSTATION v2.5                      [SESSION: LIVE] [SYS HEALTH: 99.9%] [AI: MULTIMODAL FUSION ON]     [ACCOUNT]    |
+=======================================================================================================================================================+
| ZONE 1: COMMAND HEADER & STREAM INTAKE DOCK                                                                                                           |
| [🔴 ON AIR] SHROUD // VALORANT VCT GRAND FINALS | URL: [https://twitch.tv/shroud                ] [CONNECTED: TWITCH] [FPS: 60] [BITRATE: 8200kbps]   |
| Quick Preset: [YouTube] [Twitch] [Kick] | Mode: [Autonomous AI Clip] | Auto-Threshold: [85% Virality ▼] | [⚡ CLIP 30s] [⚡ CLIP 60s] [■ STOP MONITOR] |
+-------------------------------------------------------------------------------------------------------+-----------------------------------------------+
| ZONE 2: CENTRAL DUAL VIEWPORT                                                                         | ZONE 3: DUAL TELEMETRY DECKS                  |
| +---------------------------------------------------+ +---------------------------------------------+ | +-------------------------------------------+ |
| | PANE 2A: 16:9 RAW BROADCAST MONITOR               | | PANE 2B: 9:16 ADAPTIVE SHORTS CANVAS        | | | DECK 3A: AUDIO LOUDNESS METERING        | |
| | +-----------------------------------------------+ | | +-----------------------------------------+ | | | True-Peak VU / LUFS Real-Time Meter       | |
| | |                                               | | | | [AI DUAL FACECAM SPLIT]                 | | | | -60   -48   -36   -24   -12   -6   0 dBFS   | |
| | |                                               | | | | +-------------------------------------+ | | | | L: [■■■■■■■■■■■■■■■■■■■■■■■■■■□□] -4.8dB | |
| | |                                               | | | | | Streamer Facecam Video Feed         | | | | | R: [■■■■■■■■■■■■■■■■■■■■■■■□□□□] -8.2dB | |
| | |            16:9 SOURCE BROADCAST              | | | | +-------------------------------------+ | | | | Loudness Jump: +16.2 dB [SPIKE PEAK!]   | |
| | |           (Twitch/YouTube/Kick Live)          | | | |                                         | | | | 60s Waveform: ._/\_/\__/\__/\/\/\_    | |
| | |                                               | | | | [VIRAL KINETIC CAPTION OVERLAY]         | | | +-------------------------------------------+ |
| | |                                               | | | | "BHAI YE KYA CLUTCH THA INSANE!!"       | | | DECK 3B: CHAT SENTIMENT VELOCITY & RADAR  | |
| | |                                               | | | |                                         | | | | Velocity: [ 384 msg/s ] Spike: [ 4.8x 🔥]| |
| | +-----------------------------------------------+ | | | +-------------------------------------+ | | | | Mood Vector: 86% Hype | 12% LOL | 2% OOF| |
| | HUD: [Elapsed: 01:42:19] [Sync Latency: 120ms]   | | | | Game Action Viewport                  | | | | Velocity Radar Pulse:                     | |
| | Safe Zone Guide: [ON ▼] | Layout: [Face Split ▼]  | | | +-------------------------------------+ | | | |       /\    /\      /\/\_               | |
| +---------------------------------------------------+ +---------------------------------------------+ | | | _____/  \__/  \____/     \____ [SURGE]  | |
|                                                                                                       | | | Live Transcript:                        | |
|                                                                                                       | | | [01:42:08] "No way he survived that!"   | |
|                                                                                                       | | | [01:42:14] "CLUTCH GOD! Bhai kya aim h" | |
|                                                                                                       | | +-------------------------------------------+ |
+-------------------------------------------------------------------------------------------------------+-----------------------------------------------+
| ZONE 4: MULTIMODAL AI HIGHLIGHT CANDIDATE INSPECTOR & MULTI-TRACK SCRUB TIMELINE                                                                      |
| 00:00:00                                            00:45:00                                            01:30:00                          01:42:19    |
| Audio Energy Track:  |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| |
| Chat Velocity Track: ....-^^---...--^^^^^----...---^^^^^^^^---..----^^---..---^^^^^^^^^---...--^^^^^----...---^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ [NOW]    |
| AI Virality Markers:             [★ 88%]               [★ 92%]                   [★ 96% CRITICAL HIT]            [★ 94% SELECTED CANDIDATE]           |
|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Candidate Inspector: [Candidate #05 · 01:38:12 -> 01:38:52 (40s)] | Virality: 96% 🔥 | Hook: "1 HP CLUTCH VS ENTIRE LOBBY!"                          |
| Trim Handles: Start [01:38:12] End [01:38:52] | Style: [Neon Green Bounce ▼] | Script: [Roman Hindi (Hinglish) ▼] | [⚡ Remake Video] [Preview Full] |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| ZONE 5: APPROVAL QUEUE DOCK & OMNICHANNEL SOCIAL PUBLISHING DISPATCH                                                                                  |
| Staged for Review (3 Clips Pending)                                                                               [🚀 1-CLICK DISPATCH ALL (3 CLIPS)] |
| +-----------------------------------------------+ +-----------------------------------------------+ +-----------------------------------------------+ |
| | [9:16 SHORTS CARD #01]          Virality: 96% | | [9:16 SHORTS CARD #02]          Virality: 92% | | [9:16 SHORTS CARD #03]          Virality: 88% | |
| | Title: [OMG GTA 6 PHYSICS ENGINE BROKE!!    ] | | Title: [BHAI YE SHOT DEKHO INSANE 1v4 ACE!! ] | | Title: [SHROUD LAUGHS AT HACKER FAIL       ] | |
| | Hook:  [Wait till the end of the jump 😂    ] | | Hook:  [He had 2 HP remaining in this fight!] | | Hook:  [Chat predicted this instant karma   ] | |
| | Platforms: [x] YT Shorts  [x] IG Reels        | | Platforms: [x] YT Shorts  [x] IG Reels        | | Platforms: [x] YT Shorts  [x] IG Reels        | |
| |            [x] TikTok     [x] FB Reels        | |            [x] TikTok     [ ] FB Reels        | |            [ ] TikTok     [x] FB Reels        | |
| | [🚀 APPROVE & PUBLISH]   [EDIT]   [DISMISS ✕] | | [🚀 APPROVE & PUBLISH]   [EDIT]   [DISMISS ✕] | | [🚀 APPROVE & PUBLISH]   [EDIT]   [DISMISS ✕] | |
| +-----------------------------------------------+ +-----------------------------------------------+ +-----------------------------------------------+ |
+=======================================================================================================================================================+
```

---

#### B. Standard Laptop / Desktop Workstation (1280px – 1679px)
On standard laptops, the layout organizes into a 2-column upper stage: Left column houses the Dual Viewport (16:9 monitor + 9:16 shorts canvas in an ergonomic flex row or toggleable split), while the Right column stacks the Audio Loudness and Chat Velocity Decks. Zones 4 and 5 span the lower half.

```
+=====================================================================================================+
| [LOGO] CLIPCUT PRO // WORKSTATION                      [LIVE: 🔴 SHROUD] [HEALTH: 99.8%] [SETTINGS] |
+=====================================================================================================+
| ZONE 1: COMMAND HEADER & STREAM INTAKE                                                              |
| [🔴 ON AIR] https://twitch.tv/shroud | 1080p60 · 7,850 kbps | [⚡ CLIP 30s] [⚡ 60s] [■ STOP]       |
+-----------------------------------------------------------------+-----------------------------------+
| ZONE 2: DUAL VIEWPORT (Left Column, 68% Width)                  | ZONE 3: TELEMETRY (Right Column)  |
| +-------------------------------+ +---------------------------+ | +-------------------------------+ |
| | 16:9 RAW MONITOR              | | 9:16 SHORTS PREVIEW       | | | DECK 3A: LOUDNESS VU/LUFS     | |
| | +---------------------------+ | | +-----------------------+ | | | Level: -6.4 dBFS [HOT]        | |
| | |                           | | | | Facecam Split View    | | | | Jump Delta: +14.8 dB (Spike!) | |
| | |      16:9 LIVE FEED       | | | +-----------------------+ | | | [■■■■■■■■■■■■■■■■■■■■□□□]     | |
| | |                           | | | "BHAI KYA CLUTCH THA!"  | | +-------------------------------+ |
| | +---------------------------+ | | | Game Action Viewport  | | | DECK 3B: CHAT SENTIMENT       | |
| | Elapsed: 01:14:22             | | +-----------------------+ | | | Velocity: 340 msg/s (4.5x 🔥) | |
| +-------------------------------+ +---------------------------+ | | Hype: 88% | LOL: 10% | OOF: 2% | |
|                                                                 | | Transcript: "Bhai gg op clutch" | |
+-----------------------------------------------------------------+-----------------------------------+
| ZONE 4: SCRUB TIMELINE & CANDIDATE INSPECTOR                                                        |
| Timeline: [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||] LIVE |
| Hotspots:       [★ 88%]               [★ 92%]                   [★ 96% SELECTED CANDIDATE]          |
| Inspector: Candidate #03 (01:12:00 -> 01:12:45) | Score: 96% | Hook: "UNBELIEVABLE 1v4 PLAY!"      |
+-----------------------------------------------------------------------------------------------------+
| ZONE 5: APPROVAL QUEUE DOCK (Horizontal Carousel / Responsive Grid)                                 |
| [Review: 3 Pending]                                                     [🚀 DISPATCH ALL (3 CLIPS)] |
| +-------------------------------------+ +-------------------------------------+                     |
| | Card #01: "1 HP CLUTCH!" (🔥 96%)   | | Card #02: "HACKER BANNED!" (🔥 92%) |  [ > More Cards ]   |
| | [x]YT [x]IG [x]TT [x]FB             | | [x]YT [x]IG [x]TT [ ]FB             |                     |
| | [🚀 APPROVE & POST]     [DISMISS]   | | [🚀 APPROVE & POST]     [DISMISS]   |                     |
| +-------------------------------------+ +-------------------------------------+                     |
+=====================================================================================================+
```

---

#### C. Tablet / Compact Desktop Workstation (1024px – 1279px)
On tablets and medium displays, the dual viewport provides an instant segmented tab switch (`[ 16:9 Stream Monitor ]` | `[ 9:16 Shorts Canvas ]`), telemetry decks arrange side-by-side in a horizontal strip, and the approval queue displays as stacked cards.

```
+=======================================================================================+
| [LOGO] CLIPCUT PRO                    [🔴 SHROUD LIVE] [AI ACTIVE]         [MENU]     |
+=======================================================================================+
| ZONE 1: STREAM INTAKE BAR                                                             |
| URL: [https://twitch.tv/shroud                ] [CONNECTED] | [⚡ CLIP 30s] [■ STOP]   |
+---------------------------------------------------------------------------------------+
| ZONE 2: VIEWPORT STAGE WITH VIEW TOGGLE                                               |
| Switch View: [ (•) 16:9 Broadcast Monitor ]  [ ( ) 9:16 Vertical Shorts Preview ]     |
| +-----------------------------------------------------------------------------------+ |
| |                                                                                   | |
| |                            16:9 RAW LIVE STREAM DISPLAY                           | |
| |                                                                                   | |
| +-----------------------------------------------------------------------------------+ |
| Overlays: 1080p60 · Shroud · Duration: 00:58:12                                       |
+---------------------------------------------------------------------------------------+
| ZONE 3: COMPACT DUAL TELEMETRY BAR                                                    |
| Audio Peak: -7.2 dBFS [■■■■■■■■■■■■□□] (+12dB) | Chat: 280 msg/s [4.2x 🔥] (85% Hype)  |
+---------------------------------------------------------------------------------------+
| ZONE 4: SCRUB TIMELINE                                                                |
| 00:00:00 ----------------------- [★ 92%] ---------- [★ 96% CANDIDATE] -------- 00:58:12 |
| Active Clip: 00:54:10 -> 00:54:50 (40s) | Virality: 96% | Hook: "HOW DID HE SURVIVE?!"  |
+---------------------------------------------------------------------------------------+
| ZONE 5: APPROVAL QUEUE CARDS                                                          |
| [Pending Review: 2 Clips]                                  [🚀 DISPATCH ALL (2 CLIPS)]|
| +-----------------------------------------------------------------------------------+ |
| | [9:16 Thumbnail] "INSANE 1v4 ACE!" (🔥 96%) | Platforms: [x]YT [x]IG [x]TT [x]FB  | |
| | [🚀 APPROVE & PUBLISH]                       [DISMISS]                              | |
| +-----------------------------------------------------------------------------------+ |
+=======================================================================================+
```

---

#### D. Mobile Workstation (Display Width ≤ 768px)
On mobile viewports, the workstation condenses into a responsive vertical column. Navigation moves into a slide-over drawer, telemetry collapses into an accordion status bar, and actions feature prominent touch targets.

```
+==================================================+
| [=] CLIPCUT AI               [🔴 ON AIR]  [ACCT] |
+==================================================+
| STREAM INTAKE: https://twitch.tv/shroud          |
| [⚡ QUICK CLIP 30s]     [■ STOP MONITORING]       |
+--------------------------------------------------+
| VIEWPORT: [ 16:9 Monitor ] [ (•) 9:16 Shorts ]   |
| +----------------------------------------------+ |
| |            9:16 SHORTS PREVIEW               | |
| |         +--------------------------+         | |
| |         | Streamer Facecam Video   |         | |
| |         +--------------------------+         | |
| |         "BHAI YE KYA CLUTCH THA!!"           | |
| |         +--------------------------+         | |
| |         | Action Game Play         |         | |
| |         +--------------------------+         | |
| +----------------------------------------------+ |
+--------------------------------------------------+
| TELEMETRY HUD (Tap to Expand):                   |
| Audio: -6.4 dB [PEAK]  |  Chat: 4.8x Spike 🔥    |
+--------------------------------------------------+
| AI HIGHLIGHT TIMELINE:                           |
| [★ 96% 00:42:10] Selected | [⚡ Remake]          |
+--------------------------------------------------+
| APPROVAL QUEUE (1 of 3):                         |
| +----------------------------------------------+ |
| | "1 HP CLUTCH VS ENTIRE LOBBY" (🔥 96%)       | |
| | Targets: [x]YT  [x]IG  [x]TT  [x]FB          | |
| | [🚀 APPROVE & PUBLISH NOW]                   | |
| | [DISMISS CLIP]                               | |
| +----------------------------------------------+ |
+==================================================+
```

---

## 4. Detailed Component Breakdown for All Core Modules

### 4.1 Real-Time Live Stream AI Monitor (Zone 1 & 2A)

#### Purpose & Capabilities
Ingests real-time video streams from YouTube Live, Twitch, and Kick. Provides raw 16:9 monitoring, connection status telemetry, low-latency playback controls, manual clipping overrides, and broadcast health metadata.

#### Component DOM Structure & Preserved IDs
- **Outer Container**: `#liveStreamMonitor` (`.obsidian-card.live-monitor-container`)
- **Stream Intake Controls**:
  - URL Input: `#live_url_input` (`input[type="url"].cyber-input`)
  - Platform Selectors: `.platform-preset-btn[data-pf="youtube"]`, `[data-pf="twitch"]`, `[data-pf="kick"]`
  - Start Action: `#live_start_btn` (`button.btn-cyber-primary[onclick="startLiveMonitor()"]`)
  - Stop Action: `.btn-cyber-danger[onclick="stopLiveMonitor(jid)"]`
  - Manual Clips: `button[onclick="manualLiveClip(30)"]` and `button[onclick="manualLiveClip(60)"]`
- **Player Viewport Stage**:
  - Container: `.live-player-box`
  - Embedded Player: `<iframe src="${playerSrc(...)}" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`
  - Offline / Fallback State: `.noembed` displaying offline status, signal search animation, and stream reconnection buttons.
- **Telemetry HUD Overlays**:
  - Status Badge: `.status-pill.on-air` with `<span class="pulse-dot"></span>ON AIR`
  - Stream Resolution & Bitrate: `.stream-telemetry-pill` (e.g., `1080p60 · 7,850 kbps`)
  - Elapsed Recording Time: `.stream-elapsed-counter` formatted as `HH:MM:SS` (`fmt(s.elapsed)`)
  - Ingestion Health: `.health-meter` showing dropped frame percentage (`0.0%`).

---

### 4.2 Adaptive 9:16 Shorts Canvas (Zone 2B)

#### Purpose & Capabilities
Operates as the synchronized vertical companion to the 16:9 raw stream. It dynamically renders the 9:16 vertical crop, dual-split facecam alignment, safe-zone bounding guides, and real-time kinetic auto-captions before clips are rendered or approved.

#### Component Breakdown & Safe-Area Guides
- **Container**: `#shortsCanvasViewport` (`.obsidian-card.shorts-viewport-card`)
- **Aspect Ratio Enforcer**: Strict 9:16 aspect ratio box (`max-height: 480px; aspect-ratio: 9/16; margin: 0 auto;`).
- **Facecam Split Modes**:
  - `split_bottom`: Streamer facecam pinned to bottom 38%, gameplay action in top 62%.
  - `split_top`: Streamer facecam pinned to top 38%, gameplay action in bottom 62%.
  - `gameplay`: Full-frame vertical crop focused on center action crosshairs.
  - `blur`: 16:9 raw video framed in center over a 9:16 background with 40px Gaussian blur.
  - `zoom`: Smart pan-and-scan following high-motion bounding boxes.
- **Safe-Zone Grid Overlay (`.safe-zone-overlay`)**:
  - Top Safe Margin: 80px (protects captions from YouTube Shorts header search/sound icons).
  - Bottom Safe Margin: 96px (protects hook and subtitles from account username, sound title, and caption text).
  - Right Margin Action Rail: 64px width (protects video action from like, comment, bookmark, and share icon stacks).
- **Kinetic Auto-Caption Live Preview**:
  - Real-time rendering of generated transcript text using selected typography styles:
    - `bounce`: High-impact animated scale-up on active spoken word with neon green `#00ff9d` highlight.
    - `hormozi`: Bold yellow `#ffb700` uppercase with black 3px stroke and subtle drop-shadow.
    - `mrbeast`: Large white font with alternating red/cyan highlights on key phrases.
    - `neon_green`: Cyber Matrix Emerald glowing text with ambient shadow.
    - `clean`: Minimalist white typography with semi-transparent black pill backing.
  - Script selector: Roman Hindi (`hinglish`), Devanagari Hindi (`hindi`), or English (`english`).

---

### 4.3 Audio Loudness Spikes Telemetry (Zone 3A)

#### Purpose & Mathematical Model
Detects dramatic shifts in broadcast audio energy indicating streamer excitement, screaming reactions, team clutch calls, or sudden game explosions.

#### Algorithms & Thresholds
- **Ingestion**: ffmpeg extracts 16 kHz mono PCM audio stream in real time. Every 1.0 second, Root-Mean-Square (RMS) dBFS is calculated and appended to a rolling 300-second buffer (`self.db`).
- **Loudness Jump Calculation**:
  - Baseline Amplitude: $base = \text{mean}(amp[:-10])$ (average of previous 3 minutes excluding last 10s).
  - Current Amplitude: $cur = \text{mean}(amp[-5:])$ (average of last 5s).
  - Jump Ratio: $\Delta_{loud} = \frac{cur}{\max(base, 10^{-6})} - 1.0$.
  - Spike Threshold: When $\Delta_{loud} \ge 0.6$ (audio is 60% louder than baseline), a loudness spike is declared, incrementing session counter `self.spikes`.
- **Peak Localization**: Z-score analysis ($Z = \frac{x - \mu}{\sigma}$) isolates the peak timestamp down to 100ms precision for clip boundary framing.

#### Visual Telemetry Presentation
- **True-Peak VU / LUFS Meter Bar**:
  - Scale: `-60 dBFS` to `0 dBFS` rendered via segmented hardware-accelerated bar graphs.
  - `-60 dB to -18 dB`: Cyan / Emerald gradient (Ambient speech / Gameplay base).
  - `-18 dB to -6 dB`: Neon Amber (High-energy reaction / Shout).
  - `-6 dB to 0 dB`: Critical Crimson (`#ff3366`) (Audio clipping / Climax spike).
- **60-Second Waveform Sparkline**:
  - Rendered via `spark(vals, "", -55, -8)` producing 60 vertical bars representing RMS energy history.
- **Spike Energy Delta Readout**: Numeric pill showing real-time jump: `Δ +16.2 dB (Streamer Screaming / Reaction Detected)`.

---

### 4.4 Live Chat Sentiment Velocity Telemetry (Zone 3B)

#### Purpose & Crowd NLP Model
Measures viewer chat message arrival velocity and emotional sentiment distribution. A sudden influx of chat comments is an autonomous indicator of viral broadcast moments.

#### Algorithms & Crowd Velocity Logic
- **Ingestion**: Background IRC socket client joins Twitch channel IRC (`irc.chat.twitch.tv:6697`) or polls YouTube Live Chat API.
- **Velocity Tracking**: Incoming messages per second are recorded in `self.chat[second]` alongside unique user identifiers in `self.chat_users[second]`.
- **Velocity Spike Detection**:
  - Baseline Chat: $chat_{base} = \frac{\sum chat[:-10]}{\text{len}(chat) - 10}$.
  - Current Chat: $chat_{now} = \frac{\sum chat[-8:]}{8}$.
  - Trigger Condition: If $chat_{now} \ge \max(1.5, chat_{base} \times 1.6)$, crowd velocity spike is confirmed.
- **Crowd Bot Protection (De-duplication)**:
  - Unique chatter rate: Checks unique chatter count per second ($p_{rate} \ge \max(2.0, 1.5 \times p_{avg})$) to differentiate authentic crowd surges from single-user copy-paste spam or bot attacks.
- **Sentiment Mood Vector**:
  - Real-time classification into 4 emotional buckets:
    - `Hype 🔥`: High frequency of `W`, `CLUTCH`, `LETS GOOO`, `INSANE`, `OP`, `POG`.
    - `Laughter 🤣`: High frequency of `LMAO`, `LOL`, `KEKW`, `HAHAHA`, `XD`, `DEAD`.
    - `Shock 😱`: High frequency of `OMG`, `WTF`, `NO WAY`, `AREY BHAI`, `WHAT`.
    - `Grief / Oof 💀`: High frequency of `L`, `RIP`, `F`, `THROWEr`, `BOT PLAY`.

#### Visual Telemetry Presentation
- **Velocity Speedometer Gauge**: Displays current messages/second with colored multiplier pill (`4.8x Spike Detected 🔥`).
- **Chat Velocity Sparkline**: Rendered via `spark(L.chat, "chat", 0, maxVal)` with crimson spike highlight.
- **Sentiment Mood Distribution Bar**: Multi-segment horizontal bar displaying proportional mood percentages (e.g., `86% Hype | 12% LOL | 2% Shock`).
- **Live Transcript & Chat Stream (`#liveTransStream`, `#cLiveChatStream`)**: Real-time scrolling transcript feed annotated with second-precise timestamps and speaker handles.

---

### 4.5 Multimodal AI Highlight Clipper & Scrub Timeline (Zone 4)

#### Purpose & Context Fusion Engine
The Highlight Clipper fuses audio loudness, chat velocity, and speech transcript keywords via `studio/context.py` to calculate composite virality scores ($0 - 100$). It displays these on an interactive multi-track scrub timeline and provides a precision candidate clip inspector.

#### Context Fusion Composite Virality Formula
$$\text{Score}_{composite} = (w_{asr} \cdot S_{asr}) + (w_{audio} \cdot S_{audio}) + (w_{chat} \cdot S_{chat}) + (w_{vision} \cdot S_{vision}) + \text{SynergyBoost}$$

- When audio loudness spike ($\Delta \ge 0.6$) aligns within $\pm 4\text{s}$ of a chat velocity surge ($\ge 1.6\times$), a **Synergy Boost (+15 points)** is awarded.
- If Sherpa-onnx / Whisper ASR detects high-CTR conversational triggers (e.g., *"Bhai ye kya shot mara"*, *"Look at this"*, *"Unbelievable"*), an additional semantic bonus is applied.

#### Timeline Anatomy & Controls
- **Multi-Track Canvas (`.timeline-multi-track`)**:
  - Track 1: Audio RMS loudness waveform envelope.
  - Track 2: Chat message arrival frequency density.
  - Track 3: AI Virality hotspot marker track.
- **Hotspot Marker Pins (`.timeline-marker-pin`)**:
  - `Virality ≥ 90%`: Matrix Emerald glow with `★ 96%` pill.
  - `Virality 80% - 89%`: Neon Amber glow with `★ 84%` pill.
  - `Virality < 80%`: Subdued slate pill.
- **Candidate Clip Inspector Drawer**:
  - Timestamp trim inputs: Start time `[data-f="start"]` and End time `[data-f="end"]` with 0.5s increment steppers.
  - Duration shortcut chips: `30s`, `45s`, `60s`.
  - Layout Selector: `select[data-f="layout"]` (`split_bottom`, `split_top`, `gameplay`, `blur`, `zoom`, `crop`).
  - Caption Typography Selector: `select[data-f="style"]` (`bounce`, `hormozi`, `mrbeast`, `neon_green`, `hype`, `clean`).
  - Viral Hinglish SEO Engine:
    - Auto-generated Title: High-CTR Hinglish title with emojis.
    - Big Hook Banner Text: High-engagement opening sentence displayed in top safe zone.
    - YouTube / Instagram Tags: Pre-filled hashtag and keyword package.
    - 1-Click Clipboard Copy: `button[data-act="copyallseo"]` formats complete title, description, and hashtags for YouTube Studio.
  - Action Controls:
    - `[⚡ Remake Video]` (`button[data-act="remake"]`): Triggers `/api/jobs/{jid}/clips/{cid}/render`.
    - `[Save Metadata]` (`button[data-act="savemeta"]`): Saves edits to disk.

---

### 4.6 Approval Queue Dock & Omnichannel Social Publishing Dispatch (Zone 5)

#### Purpose & Workflow
The Approval Queue Dock stages all autonomously clipped and formatted 9:16 shorts. Creators can inspect the candidate card, edit the viral title or hook, select target platforms, and dispatch to TikTok, YouTube Shorts, Instagram Reels, and Facebook Reels in a single click.

#### Component Breakdown & Data Attributes
- **Queue Container**: `#approvalSlot` (`.approval-queue-dock`)
- **Review Card Anatomy (`.approval-card#appr_${it.id}`)**:
  - 9:16 Video Stage: Embedded preview `<video src="${videoSrc}" poster="${coverSrc}" controls preload="metadata" playsinline>`.
  - Virality Badge: `<span class="badge ${scoreCls(c.score)}">🔥 Virality Score: ${c.score}/100</span>`.
  - Editable Review Inputs:
    - Viral Title: `input.approval-input#appr_ttl_${it.id}`
    - Big Hook: `input.approval-input#appr_hook_${it.id}`
    - Description: `textarea.approval-textarea#appr_desc_${it.id}`
    - Hashtags: `input.approval-input#appr_ht_${it.id}`
  - Multi-Platform Target Matrix:
    - Interactive toggle checkboxes with glowing platform badges:
      - YouTube Shorts: `input[type="checkbox"][data-pf="youtube"]`
      - Instagram Reels: `input[type="checkbox"][data-pf="instagram"]`
      - TikTok: `input[type="checkbox"][data-pf="tiktok"]`
      - Facebook Reels: `input[type="checkbox"][data-pf="facebook"]`
  - Action Controls:
    - Approve & Publish: `button.btn-cyber-emerald[onclick="submitApprove('${it.id}')"]`
    - Dismiss / Reject: `button.btn-cyber-danger[onclick="submitReject('${it.id}')"]`
    - Batch Action: `button.btn-cyber-primary[onclick="approveAllPending()"]` ("Approve All (${items.length})")
- **Publishing History Ledger (`drawPubHistory`)**:
  - Container: `#pubHistorySlot` (`.history-table-wrap`)
  - Columns: `Clip Thumbnail & Title`, `Platform Badge`, `Account Name`, `Scheduled / Posted Timestamp`, `Status Badge` (`posted` in emerald, `scheduled` in amber, `failed` in crimson), `Action Link` (direct external post URL).

---

## 5. Interaction Workflows & Micro-Interactions

### 5.1 End-to-End User Journeys

```
[BROADCAST START]
       │
       ▼
1. INTAKE & MONITORING ────────► User pastes YouTube/Twitch live URL into #live_url_input
       │                         Clicks "START MONITOR" -> POST /api/live/connect
       │                         16:9 monitor mounts stream; background ingester tracks audio/chat
       ▼
2. MULTIMODAL DETECTION ──────► Audio jump >= 0.6 AND chat velocity >= 1.6x detected
       │                         Synergy boost fires -> Composite virality score calculated (e.g. 96%)
       │                         Hotspot marker pinned to scrub timeline; clip auto-extracted
       ▼
3. 9:16 SHORT COMPOSITION ────► Auto facecam crop and subtitle synthesis applied
       │                         Shorts companion canvas updates with safe-area guides & caption preview
       │                         Candidate clip staged into Approval Queue Dock
       ▼
4. HUMAN-IN-THE-LOOP REVIEW ──► Creator reviews staged card in Zone 5
       │                         Modifies Hinglish title / hook if desired
       │                         Toggles target social platforms ([x] YT, [x] IG, [x] TikTok, [x] FB)
       ▼
5. 1-CLICK DISPATCH ──────────► Creator clicks "APPROVE & PUBLISH" -> POST /api/approval/{id}/approve
       │                         Clip transitions upward with checkmark animation
       │                         Background posting engine schedules video to optimal viral slot
       ▼
6. PUBLISHING AUDIT LEDGER ───► Published clip appears in drawPubHistory() with external live link
```

---

### 5.2 Micro-Interactions & Animation Specifications

#### 1. Live Stream Spike Trigger Pulse
When audio loudness spikes above `-6 dBFS` or chat velocity exceeds `3.0x`, the telemetry decks flash with an ambient pulse animation:
```css
@keyframes telemetry-spike-pulse {
  0% { box-shadow: 0 0 0 0 rgba(255, 51, 102, 0.6); border-color: var(--crimson-primary); }
  50% { box-shadow: 0 0 24px 6px rgba(255, 51, 102, 0.35); border-color: var(--crimson-primary); }
  100% { box-shadow: 0 0 0 0 rgba(255, 51, 102, 0); border-color: var(--border-glass); }
}
.telemetry-deck.spike-active {
  animation: telemetry-spike-pulse 0.9s cubic-bezier(0.16, 1, 0.3, 1);
}
```

#### 2. Timeline Marker Drop Animation
When the AI detects a new highlight candidate, a marker pin drops onto the scrub timeline with an elastic spring animation:
```css
@keyframes marker-drop-bounce {
  0% { transform: translateY(-24px) scale(0.6); opacity: 0; }
  60% { transform: translateY(2px) scale(1.15); opacity: 1; }
  80% { transform: translateY(-2px) scale(0.95); }
  100% { transform: translateY(0) scale(1); }
}
.timeline-marker-pin.new-marker {
  animation: marker-drop-bounce 0.5s cubic-bezier(0.18, 0.89, 0.32, 1.28) forwards;
}
```

#### 3. Interactive Scrub Hover Tooltip
Hovering the cursor across the timeline renders a floating obsidian glass tooltip showing the timestamp, video frame preview, and audio energy level:
```css
.timeline-scrub-tooltip {
  position: absolute;
  bottom: calc(100% + 10px);
  transform: translateX(-50%);
  background: var(--obsidian-300);
  backdrop-filter: var(--blur-md);
  border: 1px solid var(--border-glass-highlight);
  border-radius: var(--r-sm);
  padding: 6px 10px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-high);
  box-shadow: var(--shadow-popover);
  pointer-events: none;
  white-space: nowrap;
  z-index: var(--z-overlay);
}
```

#### 4. Card Approval & Dismissal Transitions
Clicking `submitApprove()` initiates a confirmation checkmark, softens card opacity to 0.4, slides the card upward by 10px, and collapses the card width:
```css
.approval-card.approved-transition {
  opacity: 0;
  transform: translateY(-12px) scale(0.96);
  max-width: 0;
  margin: 0;
  padding: 0;
  border-width: 0;
  transition: all 0.38s cubic-bezier(0.16, 1, 0.3, 1);
}
```

---

## 6. Frontend Technical Architecture & API Contracts

### 6.1 DOM Hierarchy & Element Tree

The refactored workstation shell inside `web/index.html` preserves the top-level `#app` container while organizing into the 5-Zone workstation:

```html
<div class="app" id="app">
  <!-- Collapsible Obsidian Sidebar -->
  <aside class="side" aria-label="Sidebar">
    <div class="side-head">
      <img class="logo" src="/brand/logo.svg" alt="PeakCut">
      <img class="mark" src="/brand/favicon.svg" alt="PeakCut">
      <button class="icon-btn collapse" data-act="collapse" id="collapseBtn"></button>
    </div>
    <nav class="nav" id="nav" aria-label="Main Navigation"></nav>
    <div class="side-foot" id="foot"></div>
  </aside>

  <!-- Mobile Scrim Overlay -->
  <div class="scrim" data-act="menu"></div>

  <!-- Primary Workstation Viewport Stage -->
  <main id="main">
    <!-- Top Navigation Header -->
    <header class="topbar">
      <button class="icon-btn menu" data-act="menu" id="menuBtn"></button>
      <span id="tpic"></span>
      <div class="titles">
        <h1 id="title">AI Studio Workstation</h1>
        <p id="subtitle">Real-time broadcast monitoring, multimodal telemetry & viral distribution</p>
      </div>
      <nav class="utabs" id="utabs" role="tablist"></nav>
      <div class="row" id="actions"></div>
    </header>

    <div id="vbanner"></div>
    <div id="heroSlot"></div>

    <!-- WORKSTATION 5-ZONE CONTENT CANVAS -->
    <div class="content workstation-stage" id="view">
      <!-- Dynamic View Slots Mount Here:
           - #liveStudioSlot (Zone 1 + Zone 2 + Zone 3 + Zone 4)
           - #approvalSlot (Zone 5 Approval Deck)
           - #pubHistorySlot (Publishing History Ledger)
      -->
    </div>
  </main>
</div>

<!-- Modals, Dialogs & Global Popovers -->
<dialog id="clipdlg" class="obsidian-modal"></dialog>
<dialog id="formdlg" class="obsidian-modal"></dialog>
<input type="file" id="file" accept="video/*" multiple hidden>
<div id="toasts" role="status" aria-live="polite"></div>
<div class="pop" id="bellpop" role="dialog" hidden></div>
<div class="pop menu" id="acctpop" role="menu" hidden></div>
```

---

### 6.2 Preserved System Contracts & Function Bindings

To prevent breaking automated test suites (`tests/test_all_features_live.py` lines 241-248 and `tests/test_live_autonomous_system.py`), the following exact JavaScript function names, route keys, and input attributes must be strictly maintained in `web/index.html`:

| Contract Identifier | Type | Required Presence Location | Downstream Dependent |
|---|---|---|---|
| `drawLiveStudio` | JavaScript Function | Window / Global scope | `test_all_features_live.py`, Route `live-studio` |
| `drawApprovalCenter` | JavaScript Function | Window / Global scope | `test_all_features_live.py`, Route `approval` |
| `drawPubHistory` | JavaScript Function | Window / Global scope | `test_all_features_live.py`, Route `pub-history` |
| `drawCreatorLiveStudio` | JavaScript Function | Window / Global scope | Creator view subtab `live` |
| `live-studio` | Route String | `go('live-studio')`, `S.view` | Test assertion & navigation router |
| `approval` | Route String | `go('approval')`, `S.view` | Test assertion & navigation router |
| `pub-history` | Route String | `go('pub-history')`, `S.view` | Test assertion & navigation router |
| `fb_tokensave` | DOM Element / Data Act | Settings & OAuth modal | Test assertion line 247 |
| `live_url_input` | DOM Element ID | Live Studio intake card | `startLiveMonitor()` handler |
| `data-act="remake"` | Event Delegation Attribute | `#clipdlg` remake button | `renderClip()` controller |
| `data-act="copyallseo"` | Event Delegation Attribute | SEO packaging drawer | Clipboard formatter |
| `data-pf="..."` | Checkbox Platform Attribute | Approval cards | `submitApprove()` platform collector |

---

### 6.3 Complete Backend REST API Contract Table

| Endpoint | Method | Request Payload | Response Schema | Purpose |
|---|---|---|---|---|
| `/api/live/connect` | `POST` | `{"url": string}` | `{"status": "ok", "session_id": string}` | Initiates live stream intake, background recording, audio dB meter, and chat IRC scraper |
| `/api/live/sessions` | `GET` | *None* | `[{"id": string, "title": string, "uploader": string, "platform": string, "url": string, "elapsed": number, "spikes": number, "chat_total": number, "db": number[], "lines": string[], "verdicts": object[], "clips": object[]}]` | Polls active live stream sessions, telemetry buffers, and real-time verdicts |
| `/api/live/{jid}/clip` | `POST` | `{"seconds": number}` | `{"status": "ok", "clip": object}` | Triggers manual highlight extraction for the preceding N seconds |
| `/api/live/{jid}/stop` | `POST` | *None* | `{"status": "ok"}` | Stops live recording session, finalizes buffer, and stores metadata |
| `/api/approval/queue` | `GET` | *None* | `[{"id": string, "job_id": string, "clip_id": string, "title": string, "hook": string, "description": string, "hashtags": string, "score": number, "video_url": string, "cover_url": string, "created_at": string}]` | Retrieves all pending highlight clips awaiting human review in Zone 5 |
| `/api/approval/{id}/approve` | `POST` | `{"platforms": string[], "title": string, "hook": string, "description": string, "hashtags": string}` | `{"status": "ok", "published": object}` | Approves clip, updates metadata, and dispatches to omnichannel social scheduler queue |
| `/api/approval/{id}/reject` | `POST` | *None* | `{"status": "ok"}` | Rejects candidate clip, removing it from queue and marking it as dismissed |
| `/api/posts/history` | `GET` | *None* | `[{"id": string, "title": string, "platform": string, "account_name": string, "scheduled_at": string, "posted_at": string, "status": string, "url": string}]` | Fetches historical log of all dispatched social media posts across platforms |
| `/api/jobs/{jid}/clips/{cid}/render` | `POST` | `{"layout": string, "style": string, "script": string, "start": number, "end": number, "captions": boolean}` | `{"status": "ok", "clip": object}` | Re-renders 9:16 vertical short with updated trim handles, caption style, or facecam layout |
| `/api/jobs/{jid}/clips/{cid}/seo` | `POST` | `{"lang": string}` | `{"status": "ok", "title": string, "hook": string, "description": string, "hashtags": string}` | Generates viral Hinglish/English title, hook, and tags via AI NLP |
| `/api/sync` | `GET` | `?v={version}` | `{"version": number, "jobs": object[], "approval_count": number, "unread": number}` | Incremental synchronization loop for background state updates |

---

### 6.4 Real-Time Polling & Synchronization Architecture

```javascript
// High-efficiency adaptive event loop architecture
let liveStudioTimer = null;
let approvalSyncTimer = null;

function initWorkstationPolling() {
  // Clear any dangling timers
  if (liveStudioTimer) clearInterval(liveStudioTimer);
  if (approvalSyncTimer) clearInterval(approvalSyncTimer);

  // 1. High-frequency telemetry polling (every 3000ms while on live workstation)
  liveStudioTimer = setInterval(async () => {
    if (S.view === "live-studio" || (S.view.startsWith("c:") && S.ctab === "live")) {
      try {
        const res = await fetch("/api/live/sessions");
        if (res.ok) {
          const sessions = await res.json();
          updateLiveTelemetryUI(sessions);
        }
      } catch (err) {
        console.warn("Live telemetry sync deferred:", err);
      }
    }
  }, 3000);

  // 2. Incremental approval queue polling (every 5000ms)
  approvalSyncTimer = setInterval(async () => {
    try {
      const res = await fetch("/api/approval/queue");
      if (res.ok) {
        const queue = await res.json();
        updateApprovalQueueDeck(queue);
      }
    } catch (err) {
      console.warn("Approval queue sync deferred:", err);
    }
  }, 5000);
}

// Granular DOM update to preserve input focus during polling
function updateLiveTelemetryUI(sessions) {
  if (!sessions || sessions.length === 0) return;
  const s = sessions[0];
  
  // Update Loudness VU Meter Bars without re-rendering entire card
  const meterL = document.getElementById("vuMeterBarL");
  const meterR = document.getElementById("vuMeterBarR");
  if (meterL && s.db && s.db.length > 0) {
    const latestDb = s.db[s.db.length - 1];
    const pct = Math.min(100, Math.max(0, ((latestDb + 60) / 60) * 100));
    meterL.style.width = pct + "%";
    if (meterR) meterR.style.width = Math.max(0, pct - 4) + "%";
  }

  // Update Chat Velocity Counter
  const chatVel = document.getElementById("chatVelocityReadout");
  if (chatVel && s.chat_total) {
    chatVel.textContent = s.chat_total + " msg/s";
  }
}
```

---

## 7. Implementation Roadmap & Quality Assurance Verification Plan

### 7.1 Prerequisite Backend Syntax Fix
Before frontend workstation changes are verified, the backend syntax error documented in `studio/posting.py:241-243` must be fixed by removing the redundant duplicated block:
```diff
--- a/studio/posting.py
+++ b/studio/posting.py
@@ -238,6 +238,3 @@
             alerts.notify(f"post failed on {p['account_name']} ({p['title']}): {p['error'][:200]}", kind="post")
     _save()
     _mirror(p)
-            alerts.notify(f"post failed on {p['account_name']} ({p['title']}): {p['error'][:200]}", kind="post")
-    _save()
-    _mirror(p)
```

### 7.2 Independent Verification Checklist for Downstream Implementer (Milestone 2)
1. **Zero Legacy Brown Residuals**: `grep -i -E "#1E1612|#120D0A|#2A1A12|#17110E|#1F140D|#3A2C25|#352a24" web/index.html` returns **zero matches**.
2. **Glassmorphism CSS Compliance**: All workstation panels utilize `var(--glass-card)`, `backdrop-filter: var(--blur-md)`, and `var(--border-glass)`.
3. **5-Neon Accent Coverage**: All 5 neon colors are defined in `:root` and applied to their respective semantic zones (Cyan, Emerald, Violet, Amber, Crimson).
4. **Layout Compliance Across 4 Breakpoints**: UI renders correctly without horizontal scroll on ultra-wide (≥1680px), laptop (1280px–1679px), tablet (1024px–1279px), and mobile (≤768px).
5. **Contract String Integrity**: `drawLiveStudio`, `drawApprovalCenter`, `drawPubHistory`, `drawCreatorLiveStudio`, and `fb_tokensave` are fully intact and functional.
6. **Backend Test Suite 100% Pass**: Both `tests/test_all_features_live.py` and `tests/test_live_autonomous_system.py` execute cleanly with 10/10 and 7/7 passing tests.
7. **Clean Browser Console**: No runtime JavaScript errors, CSP violations, or unhandled promise rejections when navigating the workstation interface.
