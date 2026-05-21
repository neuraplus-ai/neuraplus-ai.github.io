import os, sys

# ─────────────────────────────────────────────
# NeuraPulse – Add "Guide" link to every page
# Run:  python add_guide_nav.py
# Place this file in your site ROOT folder
# ─────────────────────────────────────────────

SITE_ROOT = "."   # change if needed

# ── Patterns to find & what depth they appear at ──
PATTERNS = [
    # Root pages  (index.html, blog.html, about.html, contact.html …)
    {
        "find":    '<li><a href="https://neuraplus-ai.github.io/blog.html">Blog</a></li>',
        "replace": '<li><a href="https://neuraplus-ai.github.io/blog.html">Blog</a></li>\n    <li><a href="https://neuraplus-ai.github.io/guide.html">Guide</a></li>',
    },
    # One level deep  (blog/*.html)
    {
        "find":    '<li><a href="../blog.html">Blog</a></li>',
        "replace": '<li><a href="../blog.html">Blog</a></li>\n    <li><a href="../guide.html">Guide</a></li>',
    },
    # Two levels deep  (blog/category/*.html)  — safety net
    {
        "find":    '<li><a href="../../blog.html">Blog</a></li>',
        "replace": '<li><a href="../../blog.html">Blog</a></li>\n    <li><a href="../../guide.html">Guide</a></li>',
    },
]

SKIP_FILES = {"guide.html", "add_guide_nav.py", "add-guide-nav.html"}

updated = []
skipped = []
already  = []

for root, dirs, files in os.walk(SITE_ROOT):
    # skip hidden folders (.git, node_modules, etc.)
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']

    for fname in files:
        if not fname.endswith('.html'):
            continue
        if fname in SKIP_FILES:
            continue

        path = os.path.join(root, fname)

        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                original = fh.read()
        except Exception as e:
            skipped.append((path, str(e)))
            continue

        # Skip if Guide link already present
        if 'guide.html">Guide</a>' in original or "guide.html'>Guide</a>" in original:
            already.append(path)
            continue

        new = original
        changed = False
        for p in PATTERNS:
            if p["find"] in new:
                new = new.replace(p["find"], p["replace"])
                changed = True

        if changed:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(new)
            updated.append(path)
        else:
            skipped.append((path, "nav pattern not found"))

# ── Report ──
print("\n" + "="*55)
print("  NeuraPulse – Guide Nav Updater")
print("="*55)

if updated:
    print(f"\n✅  UPDATED  ({len(updated)} files):")
    for p in updated:
        print(f"    ✓  {p}")

if already:
    print(f"\n⏭   ALREADY HAD GUIDE  ({len(already)} files) — skipped")

if skipped:
    print(f"\n⚠️   SKIPPED  ({len(skipped)} files — nav pattern not matched or error):")
    for p, reason in skipped:
        print(f"    –  {p}  [{reason}]")

print("\n" + "="*55)
print(f"  Done.  {len(updated)} updated · {len(already)} already done · {len(skipped)} skipped")
print("="*55 + "\n")
