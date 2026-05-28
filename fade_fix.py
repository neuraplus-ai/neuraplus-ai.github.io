#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║   NeuraPulse — Universal Page Fix Script v2.0                  ║
║   Fixes ALL black/invisible page bugs across 285+ pages        ║
║                                                                  ║
║   WHAT IT FIXES:                                                 ║
║   1. .fade { opacity:0 } black screen (OLD pages)              ║
║   2. .reveal { opacity:0 } black screen (NEW pages)            ║
║   3. Images jumping / layout shift (missing aspect-ratio)      ║
║   4. Benchmark bars stuck at 0% (JS animation fallback)        ║
║   5. Stat counters showing 0 (JS animation fallback)           ║
║   6. Emergency reveal: shows content after 800ms if JS fails   ║
║                                                                  ║
║   DROP IN REPO ROOT AND RUN:  python fade_fix.py               ║
╚══════════════════════════════════════════════════════════════════╝
"""

from pathlib import Path
import re

ROOT = Path(".").resolve()

# ── FOLDERS / FILES TO SKIP ──────────────────────────────────────
SKIP_DIRS  = {".git", "node_modules", ".github", "assets", "schema",
              "scripts", "_cleanup_backup"}
SKIP_FILES = {"seo_engine.py", "fade_fix.py", "neurapulse_cleanup.py"}

# ── UNIQUE MARKER — used to detect if a file is already patched ──
MARKER = "NP:UNIVERSAL-FIX-V2"

# ══════════════════════════════════════════════════════════════════
#  THE UNIVERSAL FIX BLOCK
#  Injected just before </head> on every page
# ══════════════════════════════════════════════════════════════════
UNIVERSAL_FIX = """\
<!-- {marker} -->
<style id="np-universal-fix">
/* ── FIX 1: BLACK SCREEN (.fade AND .reveal both fixed) ── */
.fade,
.reveal,
.fade-up,
.animate,
[data-animate],
[data-reveal] {{
  opacity: 1 !important;
  transform: translateY(0) !important;
  transition: opacity 0.55s ease, transform 0.55s ease !important;
}}
.fade.vis, .fade.in,
.reveal.vis, .reveal.in {{
  opacity: 1 !important;
  transform: translateY(0) !important;
}}

/* ── FIX 2: IMAGE LAYOUT SHIFT / JUMPING ── */
.blog-hero-image,
img[loading="lazy"] {{
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 1200 / 630;
  object-fit: cover;
  background: #0c1120;
  border-radius: 8px;
  margin: 0 auto 2rem;
  max-width: 1200px;
}}

/* ── FIX 3: BENCHMARK BARS FALLBACK (show at full width) ── */
.bfill {{
  width: var(--w, 80%) !important;
  transition: width 1.2s ease !important;
}}
.context-fill {{
  width: var(--w, 80%) !important;
}}

/* ── FIX 4: SCROLL PADDING (content not hidden behind sticky nav) ── */
html {{
  scroll-padding-top: 80px;
}}

/* ── FIX 5: NAV Z-INDEX ── */
#np-nav {{ z-index: 500 !important; }}
#np-mob {{ z-index: 499 !important; }}
</style>
<script>
/* NeuraPulse Universal Fix JS v2 */
(function(){{
  function npFix(){{
    /* 1. Reveal all hidden elements */
    var sel = '.reveal,.fade,.fade-up,.animate';
    var els = document.querySelectorAll(sel);
    if ('IntersectionObserver' in window) {{
      var obs = new IntersectionObserver(function(entries){{
        entries.forEach(function(e){{
          if(e.isIntersecting){{
            e.target.classList.add('in','vis');
            obs.unobserve(e.target);
          }}
        }});
      }},{{threshold:0.05,rootMargin:'0px 0px -20px 0px'}});
      els.forEach(function(el){{obs.observe(el);}});
      /* Emergency fallback: show ALL content after 800ms */
      setTimeout(function(){{
        document.querySelectorAll(sel).forEach(function(el){{
          el.classList.add('in','vis');
        }});
      }},800);
    }} else {{
      els.forEach(function(el){{el.classList.add('in','vis');}});
    }}

    /* 2. Fix broken images — replace with placeholder */
    document.querySelectorAll('img').forEach(function(img){{
      img.addEventListener('error',function(){{
        if(!this.dataset.errFixed){{
          this.dataset.errFixed = '1';
          this.src = 'https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=1200&h=630&fit=crop';
        }}
      }});
    }});

    /* 3. Fix benchmark bars */
    setTimeout(function(){{
      document.querySelectorAll('.bfill[data-w]').forEach(function(b){{
        b.style.width = b.getAttribute('data-w') + '%';
      }});
    }},600);

    /* 4. Fix stat counters showing 0 */
    setTimeout(function(){{
      document.querySelectorAll('[data-target]').forEach(function(el){{
        if(el.textContent === '0' || el.textContent.trim() === ''){{
          el.textContent = el.getAttribute('data-target');
        }}
      }});
    }},1000);
  }}

  /* Run on DOM ready */
  if(document.readyState === 'loading'){{
    document.addEventListener('DOMContentLoaded', npFix);
  }} else {{
    npFix();
  }}
}})();
</script>
<!-- /{marker} -->""".format(marker=MARKER)


# ══════════════════════════════════════════════════════════════════
#  HELPER: Detect page type for reporting
# ══════════════════════════════════════════════════════════════════
def detect_page_type(html):
    issues = []
    if 'class="reveal"' in html or "class='reveal'" in html:
        if "opacity: 0" in html or "opacity:0" in html:
            issues.append("reveal-blackout")
    if 'class="fade"' in html or "class='fade'" in html:
        if "opacity: 0" in html or "opacity:0" in html:
            issues.append("fade-blackout")
    if 'blog-hero-image' in html and 'aspect-ratio' not in html:
        issues.append("image-jump")
    if 'class="bfill"' in html and 'data-w' in html:
        issues.append("bars-invisible")
    if 'data-target' in html:
        issues.append("counter-zero")
    return issues


# ══════════════════════════════════════════════════════════════════
#  HELPER: Remove OLD fade fix (v1) to avoid duplication
# ══════════════════════════════════════════════════════════════════
OLD_MARKER_START = "<!-- NP:FADE-FIX -->"
OLD_MARKER_END   = "<!-- /NP:FADE-FIX -->"

def remove_old_fix(html):
    """Remove the old v1 NP:FADE-FIX block if present."""
    if OLD_MARKER_START not in html:
        return html, False
    # Remove everything between old markers (inclusive)
    pattern = re.compile(
        re.escape(OLD_MARKER_START) + r".*?" + re.escape(OLD_MARKER_END),
        re.DOTALL
    )
    cleaned = pattern.sub("", html)
    return cleaned, True


# ══════════════════════════════════════════════════════════════════
#  CORE: Process one HTML file
# ══════════════════════════════════════════════════════════════════
def fix_file(path):
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return "error", str(e), []

    # Already patched with v2 — skip
    if MARKER in html:
        return "already_fixed", "", []

    # No </head> tag — can't inject
    if "</head>" not in html:
        return "no_head", "", []

    # Detect what issues this page has
    issues = detect_page_type(html)

    # Remove old v1 fade fix if present
    html, removed_old = remove_old_fix(html)

    # Inject new universal fix just before </head>
    fixed_html = html.replace("</head>", UNIVERSAL_FIX + "\n</head>", 1)

    try:
        path.write_text(fixed_html, encoding="utf-8")
        status = "fixed_upgraded" if removed_old else "fixed"
        return status, "", issues
    except Exception as e:
        return "error", str(e), []


# ══════════════════════════════════════════════════════════════════
#  SCAN: Get all HTML files
# ══════════════════════════════════════════════════════════════════
def get_all_html_files():
    files = []
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        files.append(p)
    return files


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    print("\n" + "═" * 62)
    print("  NeuraPulse — Universal Page Fix Script v2.0")
    print(f"  Root: {ROOT}")
    print("═" * 62 + "\n")

    files = get_all_html_files()
    print(f"  Found {len(files)} HTML files to scan\n")
    print(f"  {'File':<55} {'Status'}")
    print(f"  {'─'*55} {'─'*12}")

    counts = {
        "fixed": 0,
        "fixed_upgraded": 0,
        "already_fixed": 0,
        "no_head": 0,
        "error": 0
    }

    all_issues = {}

    for f in files:
        result, err, issues = fix_file(f)
        counts[result] += 1
        rel = str(f.relative_to(ROOT))

        if issues:
            all_issues[rel] = issues

        icon = {
            "fixed":          "✅",
            "fixed_upgraded": "🔄",
            "already_fixed":  "⏭️ ",
            "no_head":        "⚠️ ",
            "error":          "❌"
        }.get(result, "?")

        label = {
            "fixed":          "Fixed",
            "fixed_upgraded": "Fixed + Upgraded (removed old v1)",
            "already_fixed":  "Already fixed (v2)",
            "no_head":        "Skipped (no </head>)",
            "error":          f"ERROR: {err}"
        }.get(result, result)

        # Truncate long paths for clean output
        display = rel if len(rel) <= 54 else "..." + rel[-51:]
        print(f"  {icon}  {display:<54} {label}")

    # ── SUMMARY ──────────────────────────────────────────────────
    total_fixed = counts["fixed"] + counts["fixed_upgraded"]
    print("\n" + "═" * 62)
    print(f"  ✅  Fixed              : {total_fixed} pages")
    print(f"  🔄  Upgraded (v1→v2)   : {counts['fixed_upgraded']} pages")
    print(f"  ⏭️   Already fixed (v2) : {counts['already_fixed']} pages")
    print(f"  ⚠️   Skipped            : {counts['no_head']} pages")
    print(f"  ❌  Errors             : {counts['error']} pages")

    # ── ISSUE BREAKDOWN ──────────────────────────────────────────
    if all_issues:
        print("\n  Issues found and fixed:")
        issue_counts = {}
        for rel, issues in all_issues.items():
            for issue in issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        labels = {
            "reveal-blackout": "Black screen (.reveal class)",
            "fade-blackout":   "Black screen (.fade class)",
            "image-jump":      "Image layout shift / jumping",
            "bars-invisible":  "Benchmark bars stuck at 0%",
            "counter-zero":    "Stat counters showing 0",
        }
        for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
            print(f"  → {labels.get(issue, issue):<40} {count} pages")

    # ── NEXT STEPS ───────────────────────────────────────────────
    print("\n" + "═" * 62)
    print("  NEXT STEPS:")
    print("  1. git add .")
    print("  2. git commit -m 'fix: universal page fix v2 - black screen, image jump, bars'")
    print("  3. git push")
    print("\n  Then verify in browser:")
    print("  - Open any blog page")
    print("  - Content should be visible IMMEDIATELY (no black screen)")
    print("  - Images should not jump/shift as page loads")
    print("  - Benchmark bars should show at correct width")
    print("═" * 62 + "\n")


if __name__ == "__main__":
    main()
