#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║   NeuraPulse — Universal Page Fix Script v3.0                  ║
║   Fixes ALL black/invisible page bugs across all pages         ║
║                                                                  ║
║   WHAT IT FIXES vs v2:                                          ║
║   ✅ NEW: .fi { opacity:0 } black screen (YOUR main bug!)      ║
║   ✅ NEW: .fi elements not getting .v class via observer        ║
║   1. .fade { opacity:0 } black screen (OLD pages)              ║
║   2. .reveal { opacity:0 } black screen (NEW pages)            ║
║   3. Images jumping / layout shift (missing aspect-ratio)      ║
║   4. Benchmark bars stuck at 0% (JS animation fallback)        ║
║   5. Stat counters showing 0 (JS animation fallback)           ║
║   6. Emergency reveal: shows content after 300ms if JS fails   ║
║                                                                  ║
║   DROP IN REPO ROOT AND RUN:  python fade_fix_v3.py            ║
╚══════════════════════════════════════════════════════════════════╝
"""

from pathlib import Path
import re

ROOT = Path(".").resolve()

# ── FOLDERS / FILES TO SKIP ──────────────────────────────────────
SKIP_DIRS  = {".git", "node_modules", ".github", "assets", "schema",
              "scripts", "_cleanup_backup"}
SKIP_FILES = {"seo_engine.py", "fade_fix.py", "fade_fix_v3.py",
              "neurapulse_cleanup.py"}

# ── UNIQUE MARKER — used to detect if a file is already patched ──
MARKER     = "NP:UNIVERSAL-FIX-V3"
OLD_MARKERS = ["NP:UNIVERSAL-FIX-V2", "NP:UNIVERSAL-FIX-V1", "NP:FADE-FIX"]

# ══════════════════════════════════════════════════════════════════
#  THE UNIVERSAL FIX BLOCK  (v3)
#  Key addition: .fi class is now fully handled
# ══════════════════════════════════════════════════════════════════
UNIVERSAL_FIX = """\
<!-- {marker} -->
<style id="np-universal-fix-v3">
/* ════════════════════════════════════════════════════
   FIX 1 — BLACK SCREEN
   Covers .fi  .fade  .reveal  .fade-up  .animate
   and any data-animate / data-reveal attribute
   ════════════════════════════════════════════════════ */
.fi,
.fade,
.reveal,
.fade-up,
.animate,
[data-animate],
[data-reveal] {{
  opacity: 1 !important;
  transform: translateY(0) !important;
  transition: opacity 0.55s ease, transform 0.55s ease !important;
  visibility: visible !important;
}}

/* Activated states — keep visible once class is added */
.fi.v, .fi.in, .fi.vis,
.fade.vis, .fade.in,
.reveal.vis, .reveal.in {{
  opacity: 1 !important;
  transform: translateY(0) !important;
  visibility: visible !important;
}}

/* ════════════════════════════════════════════════════
   FIX 2 — IMAGE LAYOUT SHIFT / JUMPING
   ════════════════════════════════════════════════════ */
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

/* ════════════════════════════════════════════════════
   FIX 3 — BENCHMARK BARS STUCK AT 0%
   ════════════════════════════════════════════════════ */
.bfill {{
  width: var(--w, 80%) !important;
  transition: width 1.2s ease !important;
}}
.context-fill {{
  width: var(--w, 80%) !important;
}}

/* ════════════════════════════════════════════════════
   FIX 4 — SCROLL PADDING (content behind sticky nav)
   ════════════════════════════════════════════════════ */
html {{
  scroll-padding-top: 80px;
}}

/* ════════════════════════════════════════════════════
   FIX 5 — NAV Z-INDEX
   ════════════════════════════════════════════════════ */
#np-nav {{ z-index: 500 !important; }}
#np-mob {{ z-index: 499 !important; }}
</style>
<script>
/* NeuraPulse Universal Fix JS v3 — fixes .fi + all animation classes */
(function(){{
  /* ALL selectors that can cause black screens */
  var SEL = '.fi,.reveal,.fade,.fade-up,.animate,[data-animate],[data-reveal]';

  function showEl(el) {{
    el.style.opacity    = '1';
    el.style.transform  = 'translateY(0)';
    el.style.visibility = 'visible';
    el.classList.add('v','in','vis');
  }}

  function npFix() {{
    var els = document.querySelectorAll(SEL);

    /* ── IntersectionObserver path (modern browsers) ── */
    if ('IntersectionObserver' in window) {{
      var obs = new IntersectionObserver(function(entries) {{
        entries.forEach(function(e) {{
          if (e.isIntersecting) {{
            showEl(e.target);
            obs.unobserve(e.target);
          }}
        }});
      }}, {{ threshold: 0.01, rootMargin: '0px 0px 60px 0px' }});

      els.forEach(function(el) {{ obs.observe(el); }});

      /* ── Emergency fallback: force-show ALL after 300ms ──
         This fires even if observer works, ensuring nothing
         stays hidden due to off-screen elements or timing  */
      setTimeout(function() {{
        document.querySelectorAll(SEL).forEach(showEl);
      }}, 300);

    }} else {{
      /* No IntersectionObserver — show everything immediately */
      els.forEach(showEl);
    }}

    /* ── Fix broken images ── */
    document.querySelectorAll('img').forEach(function(img) {{
      img.addEventListener('error', function() {{
        if (!this.dataset.errFixed) {{
          this.dataset.errFixed = '1';
          this.src = 'https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=1200&h=630&fit=crop';
        }}
      }});
    }});

    /* ── Fix benchmark bars ── */
    setTimeout(function() {{
      document.querySelectorAll('.bfill[data-w]').forEach(function(b) {{
        b.style.width = b.getAttribute('data-w') + '%';
      }});
    }}, 600);

    /* ── Fix stat counters stuck at 0 ── */
    setTimeout(function() {{
      document.querySelectorAll('[data-target]').forEach(function(el) {{
        if (el.textContent === '0' || el.textContent.trim() === '') {{
          el.textContent = el.getAttribute('data-target');
        }}
      }});
    }}, 1000);
  }}

  /* Run immediately if DOM ready, otherwise wait */
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', npFix);
  }} else {{
    npFix();
  }}
}})();
</script>
<!-- /{marker} -->""".format(marker=MARKER)


# ══════════════════════════════════════════════════════════════════
#  HELPER: Detect page issues for reporting
# ══════════════════════════════════════════════════════════════════
def detect_page_issues(html):
    issues = []
    if re.search(r'class=["\'][^"\']*\bfi\b[^"\']*["\']', html):
        if 'opacity:0' in html or 'opacity: 0' in html:
            issues.append("fi-blackout")
    if 'class="reveal"' in html or "class='reveal'" in html:
        if 'opacity:0' in html or 'opacity: 0' in html:
            issues.append("reveal-blackout")
    if 'class="fade"' in html or "class='fade'" in html:
        if 'opacity:0' in html or 'opacity: 0' in html:
            issues.append("fade-blackout")
    if 'blog-hero-image' in html and 'aspect-ratio' not in html:
        issues.append("image-jump")
    if 'class="bfill"' in html and 'data-w' in html:
        issues.append("bars-invisible")
    if 'data-target' in html:
        issues.append("counter-zero")
    return issues


# ══════════════════════════════════════════════════════════════════
#  HELPER: Remove ALL old fix versions to avoid duplication
# ══════════════════════════════════════════════════════════════════
def remove_old_fixes(html):
    removed_any = False
    # Remove v1 (NP:FADE-FIX)
    old_v1_start = "<!-- NP:FADE-FIX -->"
    old_v1_end   = "<!-- /NP:FADE-FIX -->"
    if old_v1_start in html:
        pattern = re.compile(
            re.escape(old_v1_start) + r".*?" + re.escape(old_v1_end),
            re.DOTALL
        )
        html = pattern.sub("", html)
        removed_any = True

    # Remove v2 (NP:UNIVERSAL-FIX-V2)
    old_v2_start = "<!-- NP:UNIVERSAL-FIX-V2 -->"
    old_v2_end   = "<!-- /NP:UNIVERSAL-FIX-V2 -->"
    if old_v2_start in html:
        pattern = re.compile(
            re.escape(old_v2_start) + r".*?" + re.escape(old_v2_end),
            re.DOTALL
        )
        html = pattern.sub("", html)
        removed_any = True

    return html, removed_any


# ══════════════════════════════════════════════════════════════════
#  CORE: Process one HTML file
# ══════════════════════════════════════════════════════════════════
def fix_file(path):
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return "error", str(e), []

    # Already patched with v3 — skip
    if MARKER in html:
        return "already_fixed", "", []

    # No </head> tag — can't inject
    if "</head>" not in html:
        return "no_head", "", []

    # Detect issues before patching
    issues = detect_page_issues(html)

    # Remove old v1/v2 fixes
    html, removed_old = remove_old_fixes(html)

    # Inject v3 fix just before </head>
    fixed_html = html.replace("</head>", UNIVERSAL_FIX + "\n</head>", 1)

    try:
        path.write_text(fixed_html, encoding="utf-8")
        status = "upgraded" if removed_old else "fixed"
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
    print("\n" + "═" * 66)
    print("  NeuraPulse — Universal Page Fix Script v3.0")
    print(f"  Root: {ROOT}")
    print("  KEY FIX: .fi class black screen (missed by v2)")
    print("═" * 66 + "\n")

    files = get_all_html_files()
    print(f"  Found {len(files)} HTML files to scan\n")
    print(f"  {'File':<55} {'Status'}")
    print(f"  {'─'*55} {'─'*14}")

    counts = {
        "fixed":         0,
        "upgraded":      0,
        "already_fixed": 0,
        "no_head":       0,
        "error":         0,
    }
    all_issues = {}

    for f in files:
        result, err, issues = fix_file(f)
        counts[result] += 1
        rel = str(f.relative_to(ROOT))

        if issues:
            all_issues[rel] = issues

        icon = {
            "fixed":         "✅",
            "upgraded":      "🔄",
            "already_fixed": "⏭️ ",
            "no_head":       "⚠️ ",
            "error":         "❌",
        }.get(result, "?")

        label = {
            "fixed":         "Fixed (v3 injected)",
            "upgraded":      "Upgraded v2→v3 (old block removed)",
            "already_fixed": "Already on v3",
            "no_head":       "Skipped (no </head>)",
            "error":         f"ERROR: {err}",
        }.get(result, result)

        display = rel if len(rel) <= 54 else "..." + rel[-51:]
        print(f"  {icon}  {display:<54} {label}")

    # ── SUMMARY ──────────────────────────────────────────────────
    total_touched = counts["fixed"] + counts["upgraded"]
    print("\n" + "═" * 66)
    print(f"  ✅  Fixed (fresh)       : {counts['fixed']} pages")
    print(f"  🔄  Upgraded (v2 → v3)  : {counts['upgraded']} pages")
    print(f"  ⏭️   Already on v3       : {counts['already_fixed']} pages")
    print(f"  ⚠️   Skipped             : {counts['no_head']} pages")
    print(f"  ❌  Errors              : {counts['error']} pages")
    print(f"  ─────────────────────────────────────────")
    print(f"  📄  Total patched       : {total_touched} pages")

    # ── ISSUE BREAKDOWN ──────────────────────────────────────────
    if all_issues:
        print("\n  Issues detected and fixed:")
        issue_counts = {}
        for _, issues in all_issues.items():
            for issue in issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        labels = {
            "fi-blackout":     "Black screen (.fi class)       ← YOUR BUG",
            "reveal-blackout": "Black screen (.reveal class)",
            "fade-blackout":   "Black screen (.fade class)",
            "image-jump":      "Image layout shift / jumping",
            "bars-invisible":  "Benchmark bars stuck at 0%",
            "counter-zero":    "Stat counters showing 0",
        }
        for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
            print(f"  → {labels.get(issue, issue):<46} {count} pages")

    # ── NEXT STEPS ───────────────────────────────────────────────
    print("\n" + "═" * 66)
    print("  NEXT STEPS:")
    print("  1. git add .")
    print("  2. git commit -m 'fix: universal fix v3 - fi blackout, all pages'")
    print("  3. git push")
    print("\n  Verify in browser:")
    print("  • Content visible IMMEDIATELY on page load (no black flash)")
    print("  • .fi elements appear without needing to scroll")
    print("  • Images don't jump/shift")
    print("  • Benchmark bars render at correct width")
    print("═" * 66 + "\n")


if __name__ == "__main__":
    main()
