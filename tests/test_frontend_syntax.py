import re
import subprocess
import os
import sys

def test_frontend_syntax_and_integrity():
    html_path = os.path.join(os.path.dirname(__file__), "..", "web", "index.html")
    assert os.path.exists(html_path), f"File {html_path} does not exist"
    
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Check for legacy warm/brown hex colors
    banned_hexes = [
        r"#1E1612", r"#120D0A", r"#2A1A12", r"#17110E", r"#1F140D", 
        r"#352a24", r"#3A2C25", r"#FFE2CC", r"#F1EBE6", r"#FCFAF8", 
        r"#FFD2AE", r"#B9A597", r"#FFF4EA"
    ]
    for b in banned_hexes:
        matches = re.findall(b, html, re.IGNORECASE)
        assert len(matches) == 0, f"Found legacy warm hex: {b}"
    print("[PASS] 1. Legacy warm/brown hexes eliminated (0 matches)")

    # 2. Check Obsidian-Glass tokens
    assert "--obsidian-0" in html and "--obsidian-500" in html
    assert "--glass-panel" in html and "--glass-card" in html
    assert "--cyan-" in html and "--emerald-" in html and "--violet-" in html
    print("[PASS] 2. Obsidian-Glass and 5-Neon Accent tokens present")

    # 3. Check critical IDs and contracts
    required_ids = [
        "live_url_input", "liveTimelineBar", "liveTransStream", "liveClipsGrid",
        "approvalSlot", "pubHistorySlot", "appr_ttl_", "appr_hook_", "appr_ht_",
        "vuMeterBarL", "vuMeterBarR", "chatVelocityReadout", "chatSentimentDeck",
        "sentiment-vector-bar", "shortsSplitBox", "kineticLiveCaption",
        "candidate-inspector-card", "live-player-box"
    ]
    for rid in required_ids:
        assert rid in html, f"Missing required ID or token: {rid}"
    print("[PASS] 3. All required UI elements and contract IDs present")

    # 4. Check JS function contracts
    required_funcs = [
        "drawLiveStudio", "drawApprovalCenter", "drawPubHistory", "drawCreatorLiveStudio",
        "updateShortsLayout", "updateCaptionStyle", "updateLiveTelemetryUI"
    ]
    for rf in required_funcs:
        assert rf in html, f"Missing required function: {rf}"
    print("[PASS] 4. All contract functions defined")

    # 5. Check JS syntax with Node.js
    scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', html, re.DOTALL)
    assert len(scripts) > 0, "No script tags found"
    
    temp_js_path = os.path.join(os.path.dirname(__file__), "temp_check.js")
    with open(temp_js_path, "w", encoding="utf-8") as f:
        f.write("\n".join(scripts))
    
    try:
        proc = subprocess.run(["node", "--check", temp_js_path], capture_output=True, text=True)
        assert proc.returncode == 0, f"Node --check failed: {proc.stderr}"
        print("[PASS] 5. Node.js verified clean JS syntax without errors")
    finally:
        if os.path.exists(temp_js_path):
            os.remove(temp_js_path)

    print("\nAll frontend syntax & contract checks passed successfully!")

if __name__ == "__main__":
    test_frontend_syntax_and_integrity()
