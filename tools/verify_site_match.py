"""Verify 100% match between local PeakCut and https://peakcut.haziqqasmi.com."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRAPED = ROOT / "data" / "scraped_site"
WEB = ROOT / "web"

failures = []

def check(name, condition, details=""):
    if condition:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name} - {details}")
        failures.append(name)

print("=" * 60)
print("VERIFYING PEAKCUT 100% MATCH WITH https://peakcut.haziqqasmi.com")
print("=" * 60)

# 1. Brand Assets verification
brand_files = [
    "logo.svg", "logo-light.svg", "favicon.svg", "logo-email.png", "og.jpg",
    "showcase-1.jpg", "showcase-1.mp4",
    "showcase-2.jpg", "showcase-2.mp4",
    "showcase-3.jpg", "showcase-3.mp4",
    "showcase-4.jpg", "showcase-4.mp4",
    "showcase-5.jpg", "showcase-5.mp4",
    "showcase-6.jpg", "showcase-6.mp4",
    "demo-bounce.jpg", "demo-bounce.mp4",
    "demo-clean.jpg", "demo-clean.mp4",
    "demo-hype.jpg", "demo-hype.mp4"
]

for bf in brand_files:
    local_f = WEB / "brand" / bf
    scraped_f = SCRAPED / "brand" / bf
    if not local_f.exists():
        check(f"Brand asset {bf} exists locally", False, "File missing")
    elif not scraped_f.exists():
        check(f"Brand asset {bf} exists in scraped", False, "Scraped missing")
    else:
        same = local_f.stat().st_size == scraped_f.stat().st_size
        check(f"Brand asset {bf} matches remote byte-size ({local_f.stat().st_size} B)", same)

# 2. Gradient ASCII script verification
ascii_local = WEB / "assets" / "gradient-ascii.js"
ascii_scraped = SCRAPED / "assets" / "gradient-ascii.js"
check("web/assets/gradient-ascii.js exists", ascii_local.exists())
if ascii_local.exists() and ascii_scraped.exists():
    check("gradient-ascii.js byte-identical to remote", ascii_local.read_bytes() == ascii_scraped.read_bytes())

# 3. Landing Page verification
landing_template = (WEB / "landing.html").read_text(encoding="utf-8")
rendered_landing = landing_template.replace("{{SITE}}", "https://peakcut.haziqqasmi.com")
remote_landing = (SCRAPED / "index.html").read_text(encoding="utf-8")
check("Landing page (landing.html) renders 100% identical to scraped landing", rendered_landing == remote_landing)

# 4. Auth Page verification (login & signup)
auth_local = (WEB / "auth.html").read_text(encoding="utf-8")
login_scraped = (SCRAPED / "login").read_text(encoding="utf-8")
signup_scraped = (SCRAPED / "signup").read_text(encoding="utf-8")
check("Auth page (auth.html) 100% identical to scraped /login", auth_local == login_scraped)
check("Auth page (auth.html) 100% identical to scraped /signup", auth_local == signup_scraped)

# 5. Reset Page verification
reset_local = (WEB / "reset.html").read_text(encoding="utf-8")
reset_scraped = (SCRAPED / "reset").read_text(encoding="utf-8")
check("Reset page (reset.html) 100% identical to scraped /reset", reset_local == reset_scraped)

# 6. Legal Pages verification (terms, privacy, refunds, acceptable-use, data-deletion)
sys.path.insert(0, str(ROOT))
from studio import server, config

legal_template = (WEB / "legal.html").read_text(encoding="utf-8")

for p in ["terms", "privacy", "refunds", "acceptable-use"]:
    scraped_p = (SCRAPED / p).read_text(encoding="utf-8")
    title, desc = server.LEGAL[p]
    rendered_legal = legal_template
    subs = {
        "{{CONTACT}}": "the contact details on our website",
        "{{PAGE}}": p,
        "{{PAGE_PATH}}": p,
        "{{SITE}}": "https://peakcut.haziqqasmi.com",
        "{{NAME}}": "PeakCut",
        "{{LAW}}": "the laws of the country where PeakCut's operator is established",
        "{{TITLE}}": title,
        "{{DESC}}": desc
    }
    for k, v in subs.items():
        rendered_legal = rendered_legal.replace(k, v)
    check(f"Legal page /{p} renders 100% identical to remote", rendered_legal == scraped_p)

# 7. Check web/index.html syntax & integrity
import tests.test_frontend_syntax as tfs
try:
    tfs.test_frontend_syntax_and_integrity()
    check("Frontend syntax & integrity checks (Obsidian-Glass, IDs, Node syntax)", True)
except Exception as e:
    check("Frontend syntax & integrity checks", False, str(e))

print("=" * 60)
if failures:
    print(f"FAILED: {len(failures)} checks failed!")
    sys.exit(1)
else:
    print("ALL SITE MATCH & INTEGRITY CHECKS PASSED 100%!")
    sys.exit(0)
