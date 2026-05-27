#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  NeuraPulse — BLACK PAGE FIX                             ║
║  ONE PURPOSE: Fix .fade opacity:0 black pages            ║
║  Safe · Fast · Only touches the CSS · Nothing else       ║
║                                                          ║
║  RUN: python fix_black_pages.py                          ║
╚══════════════════════════════════════════════════════════╝
"""
import re
from pathlib import Path

ROOT = Path(".").resolve()
SKIP_DIRS  = {".git", "node_modules", ".github", "assets"}
SKIP_FILES = {"fix_black_pages.py", "seo_engine.py",
              "neurapulse_enterprise.py", "neurapulse_card_injector.py"}

# The permanent fix — overrides any .fade opacity:0
FADE_FIX = (
    "\n<style id='np-fade-fix'>\n"
    ".fade{opacity:1!important;transform:none!important;transition:none!important;}\n"
    ".fade.vis{opacity:1!important;transform:none!important;}\n"
    "[style*='opacity: 0']{opacity:1!important;}\n"
    "[style*='opacity:0']{opacity:1!important;}\n"
    "</style>\n"
)

def get_files():
    out = []
    for p in sorted(ROOT.rglob("*.html")):
        parts = p.relative_to(ROOT).parts
        if any(x in SKIP_DIRS for x in parts): continue
        if p.name in SKIP_FILES: continue
        out.append(p)
    return out

def fix_file(path):
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except:
        return False

    orig = html
    changed = False

    # 1. Remove old/conflicting fade fix styles first
    html = re.sub(
        r'<style[^>]*id=["\']np-fade-fix["\'][^>]*>.*?</style>',
        '', html, flags=re.DOTALL|re.IGNORECASE
    )

    # 2. Fix .fade{opacity:0} directly inside existing <style> blocks
    def fix_style_block(m):
        css = m.group(0)
        # Replace opacity:0 on .fade rules
        css = re.sub(
            r'(\.fade\s*\{[^}]*?)opacity\s*:\s*0([^}]*\})',
            r'\1opacity:1\2',
            css, flags=re.IGNORECASE
        )
        css = re.sub(
            r'(\.fade\s*\{[^}]*?)transform\s*:\s*translateY\([^)]+\)([^}]*\})',
            r'\1transform:none\2',
            css, flags=re.IGNORECASE
        )
        return css

    html = re.sub(r'<style[\s\S]*?</style>', fix_style_block, html,
                  flags=re.IGNORECASE)

    # 3. Also fix any inline style="opacity:0" on elements with class fade
    html = re.sub(
        r'(class="[^"]*\bfade\b[^"]*"[^>]*)\bstyle="[^"]*opacity\s*:\s*0[^"]*"',
        r'\1',
        html, flags=re.IGNORECASE
    )

    # 4. Inject the nuclear override in <head>
    if '</head>' in html:
        html = html.replace('</head>', FADE_FIX + '</head>', 1)
    elif '<body' in html:
        html = re.sub(r'(<body[^>]*>)', r'\1' + FADE_FIX, html, count=1)

    if html != orig:
        path.write_text(html, encoding="utf-8")
        return True
    return False

def main():
    files = get_files()
    print(f"\n{'='*52}")
    print(f"  BLACK PAGE FIX")
    print(f"  {len(files)} HTML files found")
    print(f"{'='*52}\n")

    fixed = 0
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        if fix_file(f):
            fixed += 1
            print(f"  ✅ Fixed: {rel}")

    print(f"\n{'='*52}")
    print(f"  DONE — {fixed} files fixed")
    print(f"{'='*52}")
    print("""
  NEXT STEPS:
  git add -A
  git commit -m "fix: black pages fade opacity fix"
  git push
""")

if __name__ == "__main__":
    main()
