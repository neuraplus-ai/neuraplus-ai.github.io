#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  NeuraPulse — ENTERPRISE CLEANUP v1.0                       ║
║  Removes ALL injected code from all HTML pages              ║
║  Safe · Idempotent · Backs up before touching               ║
╚══════════════════════════════════════════════════════════════╝

DROP IN REPO ROOT → python neurapulse_cleanup.py

What it removes:
  1. NP:GEO       — duplicate meta tags in <head>
  2. np:meta      — duplicate OG/Twitter/schema tags
  3. NP:NAV       — injected nav bar + mobile menu + nav JS
  4. NP:ENGAGE    — reading progress bar + scroll reveal scripts
  5. NP:ANALYTICS — scroll depth tracking script
  6. NP:FOOTER    — second injected footer
  7. np-nav-css   — injected nav <style> block (if left orphaned)
  8. np-footer-css— injected footer <style> block (if left orphaned)
  9. np-ilink     — internal anchor links added by the script
 10. <footer id="np-footer"> — injected footer if markers were stripped

What it KEEPS:
  - guide.html and blog.html card injection markers (NP:GUIDE-CARDS, NP:BLOG-CARDS)
  - Your original <nav> (no id="np-nav"), your original <footer> (no id="ng-footer")
  - Your GTM/GA scripts
  - Your chatbot widget
  - <div class="pb" id="pb"> progress bar
  - Everything else untouched
"""

import re
import shutil
import datetime
from pathlib import Path

# ── CONFIG ───────────────────────────────────────────────────────
ROOT = Path(".").resolve()

SKIP_DIRS  = {".git", "node_modules", ".github", "assets", "schema", "scripts"}
SKIP_FILES = {
    "neurapulse_enterprise.py",
    "neurapulse_card_injector.py",
    "neurapulse_cleanup.py",
    "master_inject.py",
    "seo_engine.py",
}

BACKUP_DIR = ROOT / "_cleanup_backup"
TODAY = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# ── COLLECT FILES ────────────────────────────────────────────────
def get_files():
    out = []
    for p in sorted(ROOT.rglob("*.html")):
        parts = p.relative_to(ROOT).parts
        if any(x in SKIP_DIRS for x in parts):
            continue
        if p.name in SKIP_FILES:
            continue
        out.append(p)
    return out

# ── REMOVAL PATTERNS ─────────────────────────────────────────────
# Each entry: (description, regex_pattern)
# Patterns use re.DOTALL and re.IGNORECASE

BLOCK_PATTERNS = [
    # 1. NP:GEO block
    ("NP:GEO block",
     r'<!-- NP:GEO -->[\s\S]*?<!-- /NP:GEO -->'),

    # 2. np:meta block (lowercase markers)
    ("np:meta block",
     r'<!-- np:meta -->[\s\S]*?<!-- /np:meta -->'),

    # 3. NP:NAV block (full nav including style, nav, mobile div, script)
    ("NP:NAV block",
     r'<!-- NP:NAV -->[\s\S]*?<!-- /NP:NAV -->'),

    # 4. NP:ENGAGE block (reading progress bar + scroll reveal)
    ("NP:ENGAGE block",
     r'<!-- NP:ENGAGE -->[\s\S]*?<!-- /NP:ENGAGE -->'),

    # 5. NP:ANALYTICS block
    ("NP:ANALYTICS block",
     r'<!-- NP:ANALYTICS -->[\s\S]*?<!-- /NP:ANALYTICS -->'),

    # 6. NP:FOOTER block
    ("NP:FOOTER block",
     r'<!-- NP:FOOTER -->[\s\S]*?<!-- /NP:FOOTER -->'),

    # 7. Orphaned np-nav-css style tag (if marker was stripped but style remained)
    ("orphaned np-nav-css style",
     r'<style[^>]*id=["\']np-nav-css["\'][^>]*>[\s\S]*?</style>'),

    # 8. Orphaned np-footer-css style tag
    ("orphaned np-footer-css style",
     r'<style[^>]*id=["\']np-footer-css["\'][^>]*>[\s\S]*?</style>'),

    # 9. Orphaned #np-nav element (if markers were stripped but nav HTML stayed)
    ("orphaned #np-nav element",
     r'<nav[^>]*id=["\']np-nav["\'][^>]*>[\s\S]*?</nav>'),

    # 10. Orphaned #np-mob mobile menu div
    ("orphaned #np-mob div",
     r'<div[^>]*id=["\']np-mob["\'][^>]*>[\s\S]*?</div>'),

    # 11. Orphaned #np-footer element
    ("orphaned #np-footer element",
     r'<footer[^>]*id=["\']np-footer["\'][^>]*>[\s\S]*?</footer>'),

    # 12. Orphaned #np-rbar reading progress bar div
    ("orphaned #np-rbar div",
     r'<div[^>]*id=["\']np-rbar["\'][^>]*>[\s\S]*?</div>'),
]

# Internal link pattern — unwrap <a class="np-ilink"...>text</a> → text
NP_ILINK_PATTERN = re.compile(
    r'<a\s[^>]*class=["\'][^"\']*np-ilink[^"\']*["\'][^>]*>(.*?)</a>',
    re.IGNORECASE | re.DOTALL
)

# ── CLEAN ONE FILE ────────────────────────────────────────────────
def clean_file(path):
    original = path.read_text(encoding="utf-8", errors="ignore")
    html = original
    removed = []

    for desc, pattern in BLOCK_PATTERNS:
        new_html = re.sub(pattern, "", html, flags=re.IGNORECASE | re.DOTALL)
        if new_html != html:
            removed.append(desc)
            html = new_html

    # Unwrap np-ilink anchors (keep the link text, remove the <a> wrapper)
    new_html = NP_ILINK_PATTERN.sub(r'\1', html)
    if new_html != html:
        removed.append("np-ilink internal anchors unwrapped")
        html = new_html

    # Clean up excess blank lines left behind (max 2 consecutive blank lines)
    html = re.sub(r'\n{3,}', '\n\n', html)

    if html != original:
        # Back up original
        rel = path.relative_to(ROOT)
        backup_path = BACKUP_DIR / TODAY / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)

        path.write_text(html, encoding="utf-8")
        return removed
    return []

# ── MAIN ─────────────────────────────────────────────────────────
def main():
    files = get_files()
    print("\n" + "═" * 60)
    print("  NeuraPulse Cleanup v1.0")
    print(f"  {len(files)} HTML files found")
    print("═" * 60)
    print(f"\n  Backups → {BACKUP_DIR / TODAY}/\n")

    total_changed = 0
    total_skipped = 0
    all_log = []

    for f in files:
        try:
            removed = clean_file(f)
        except Exception as e:
            print(f"  ❌ ERROR on {f.relative_to(ROOT)}: {e}")
            continue

        if removed:
            total_changed += 1
            rel = str(f.relative_to(ROOT))
            print(f"  ✅ {rel}")
            for r in removed:
                print(f"       — removed: {r}")
            all_log.append(f"{rel}: {', '.join(removed)}")
        else:
            total_skipped += 1

    # Write log
    log_path = ROOT / "cleanup-log.txt"
    with open(log_path, "w", encoding="utf-8") as lf:
        lf.write(f"NeuraPulse Cleanup — {TODAY}\n")
        lf.write(f"Files changed: {total_changed}\n")
        lf.write(f"Files unchanged: {total_skipped}\n\n")
        for line in all_log:
            lf.write(line + "\n")

    print("\n" + "═" * 60)
    print(f"  ✅ Files cleaned  : {total_changed}")
    print(f"  ⏭  Already clean : {total_skipped}")
    print(f"  💾 Backups saved  : {BACKUP_DIR / TODAY}/")
    print(f"  📋 Log written    : cleanup-log.txt")
    print("═" * 60)
    print("\n  NEXT STEPS:")
    print("  1. Review a few files to confirm they look right")
    print("  2. git add .")
    print('  3. git commit -m "Remove NeuraPulse injected code"')
    print("  4. git push\n")
    print("  To RESTORE any file from backup:")
    print(f"  cp '{BACKUP_DIR / TODAY}/<file.html>' ./<file.html>\n")

if __name__ == "__main__":
    main()
