import os
import sys
import json
from pathlib import Path

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from studio.server import app
from studio import approval, context, vision, accounts, live, posting

client = TestClient(app, base_url="http://localhost:8765")

def test_api_status():
    """Verify system status endpoint."""
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert "user" in data
    assert "accounts" in data
    assert "styles" in data

def test_context_fusion_engine():
    """Verify multimodal Context Fusion calculates composite virality and synergy."""
    # Baseline normal score
    score, boosted = context.calculate_composite_score(
        speech_score=30,
        audio_jump_pct=0.0,
        chat_spike_ratio=0.5,
        visual_score=40
    )
    assert 0 <= score <= 100
    assert boosted is False
    
    # Synergistic high virality score (speech >= 70, audio >= 75, chat >= 75, visual >= 75)
    # audio_jump_pct: 0.5 -> 50 + 25 = 75
    # chat_spike_ratio: 3.5 -> min(3.5, 4.0)/4.0 * 100 = 87
    score_hi, boosted_hi = context.calculate_composite_score(
        speech_score=85,
        audio_jump_pct=0.8,
        chat_spike_ratio=3.5,
        visual_score=90
    )
    assert score_hi >= 80
    assert boosted_hi is True

def test_vision_module():
    """Verify vision module returns structured data safely."""
    # Extract frame on non-existent file returns None safely
    frame = vision.extract_frame("non_existent_video.mp4", 10.0)
    assert frame is None
    
    # Fallback analysis for missing/unreadable file returns structured default
    moment = vision.analyze_video_moment(Path("non_existent_video.mp4"), 5.0)
    assert "visual_score" in moment
    assert "reaction" in moment
    assert "action" in moment
    assert isinstance(moment["visual_score"], int)

def test_approval_workflow():
    """Verify end-to-end approval queue, retrieval, approve, reject and history audit."""
    uid = "test_qa_user"
    job_id = "job_test_qa_1"
    clip_id = 1
    
    # 1. Add to approval queue
    item = approval.add(
        uid=uid,
        job_id=job_id,
        clip_id=clip_id,
        platforms=["youtube", "instagram", "tiktok", "facebook"],
        meta={
            "title": "Insane Streamer Reaction",
            "category": "Epic Moments",
            "score": 89,
            "hook": "Wait for this reaction!",
            "hashtags": ["#gaming", "#viral"]
        }
    )
    assert item["id"]
    assert item["status"] == "pending"
    assert item["meta"]["title"] == "Insane Streamer Reaction"
    item_id = item["id"]
    
    # 2. Check item in queue
    q = approval.queue(uid)
    assert any(x["id"] == item_id for x in q)
    
    # 3. Check get item
    fetched = approval.get(uid, item_id)
    assert fetched["id"] == item_id
    
    # 4. Reject workflow
    rejected = approval.reject(uid, item_id, reason="Audio was noisy")
    assert rejected["status"] == "rejected"
    assert rejected["rejection_reason"] == "Audio was noisy"
    
    # Item should no longer be pending in queue
    q_after_reject = approval.queue(uid)
    assert not any(x["id"] == item_id for x in q_after_reject)
    
    # 5. Add second item and approve workflow
    item2 = approval.add(
        uid=uid,
        job_id=job_id,
        clip_id=2,
        platforms=["youtube", "facebook"],
        meta={"title": "Funny Clutch Fail"}
    )
    item2_id = item2["id"]
    
    approved = approval.approve(
        uid=uid,
        item_id=item2_id,
        platforms=["youtube", "facebook"],
        meta={"title": "Updated Title: Ultimate Clutch Fail"}
    )
    assert approved["status"] == "approved"
    assert approved["meta"]["title"] == "Updated Title: Ultimate Clutch Fail"
    assert approved["platforms"] == ["youtube", "facebook"]
    
    # 6. Verify audit history contains both rejected and approved items
    hist = approval.history(uid)
    hist_ids = [h["id"] for h in hist]
    assert item_id in hist_ids
    assert item2_id in hist_ids

def test_approval_api_endpoints():
    """Verify REST API endpoints for Approval Center."""
    # GET queue
    res_q = client.get("/api/approval/queue")
    assert res_q.status_code == 200
    assert isinstance(res_q.json(), list)
    
    # GET history
    res_h = client.get("/api/approval/history")
    assert res_h.status_code == 200
    assert isinstance(res_h.json(), list)
    
    # POST submit custom clip for approval
    res_sub = client.post("/api/approval/submit", json={
        "job_id": "api_test_job",
        "clip_id": "99",
        "platforms": ["youtube", "facebook"],
        "meta": {
            "title": "API Submitted Clip",
            "score": 92
        }
    })
    assert res_sub.status_code == 200
    item = res_sub.json()
    item_id = item["id"]
    
    # POST approve endpoint
    res_app = client.post(f"/api/approval/{item_id}/approve", json={
        "platforms": ["youtube"],
        "meta": {"title": "API Approved Title"}
    })
    assert res_app.status_code == 200
    assert res_app.json()["status"] == "approved"
    
    # POST reject endpoint on another item
    res_sub2 = client.post("/api/approval/submit", json={
        "job_id": "api_test_job_2",
        "clip_id": "100",
        "meta": {"title": "Clip to Reject"}
    })
    item2 = res_sub2.json()
    item2_id = item2["id"]
    res_rej = client.post(f"/api/approval/{item2_id}/reject", json={"reason": "Not engaging enough"})
    assert res_rej.status_code == 200
    assert res_rej.json()["status"] == "rejected"

def test_facebook_reels_adapter():
    """Verify Facebook Reels adapter and account registration."""
    assert "facebook" in accounts.PLATFORM_NAMES
    assert "facebook" in accounts.APPS
    
    # Test public sanitization
    sample_acc = {
        "id": "fb_123",
        "platform": "facebook",
        "name": "My Gamer Page",
        "access_token": "SECRET_TOKEN_DO_NOT_EXPOSE",
        "page_id": "987654"
    }
    pub = accounts.public(sample_acc)
    assert "access_token" not in pub
    assert pub["name"] == "My Gamer Page"
    assert pub["platform"] == "facebook"

def test_live_studio_endpoints():
    """Verify Live Studio API endpoints."""
    # Sessions
    res_sess = client.get("/api/live/sessions")
    assert res_sess.status_code == 200
    assert isinstance(res_sess.json(), list)
    
    # Connect with invalid empty URL returns 400
    res_bad = client.post("/api/live/connect", json={"url": ""})
    assert res_bad.status_code == 400

if __name__ == "__main__":
    tests = [
        test_api_status,
        test_context_fusion_engine,
        test_vision_module,
        test_approval_workflow,
        test_approval_api_endpoints,
        test_facebook_reels_adapter,
        test_live_studio_endpoints
    ]
    passed = 0
    print(f"Running {len(tests)} automated tests for Clipcut Autonomous AI Platform...\n" + "="*70)
    for t in tests:
        try:
            t()
            print(f"  [PASS] {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {t.__name__}: {e}")
            import traceback
            traceback.print_exc()
    print("="*70)
    print(f"Result: {passed}/{len(tests)} passed.")
    if passed != len(tests):
        exit(1)
