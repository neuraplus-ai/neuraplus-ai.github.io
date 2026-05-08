#!/usr/bin/env python3
"""
NeuraPulse — Fix All 300+ HTML Pages
=====================================
What this script does to EVERY .html file:
  1. Expands thin meta descriptions to 150–160 characters
  2. Expands/adds proper <title> tags (50–60 chars)
  3. Adds missing og:title, og:description, og:image tags
  4. Adds missing twitter:card / twitter:title / twitter:description
  5. Fixes privacy policy links — adds target="_blank" + prevents page refresh
  6. Adds <link rel="stylesheet" href="/popup.css"> if missing
  7. Adds <script src="/popup.js"></script> before </body> if missing
  8. Adds canonical tag if missing
  9. Adds robots meta if missing

Run via GitHub Actions — no local Python install needed.
"""

import os
import re
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
SITE_ROOT = "."
SITE_URL   = "https://neuraplus-ai.github.io"
OG_IMAGE   = "https://neuraplus-ai.github.io/og-default.jpg"
SKIP_FILES = {"404.html", "sitemap.html", "googlea8e9563d4c0c037a.html"}

# Per-page overrides: filename (relative to repo root) → (title, description)
PAGE_META = {
    "index.html": (
        "NeuraPulse — 200+ Expert AI Articles on Gemini AI, ChatGPT Ads & LLMs",
        "NeuraPulse is your expert AI hub — 200+ research-backed articles on Gemini AI advertising, "
        "ChatGPT ads, AI automation, LLMs, and the future of intelligence. Updated weekly. Free to read."
    ),
    "about.html": (
        "About NeuraPulse — Expert AI Writers & Researchers Behind 200+ Articles",
        "Meet the NeuraPulse team — ML engineers, researchers and writers making artificial intelligence "
        "understandable for marketers, developers and curious minds worldwide."
    ),
    "contact.html": (
        "Contact NeuraPulse — Guest Posts, Sponsorship & Free Newsletter",
        "Get in touch with NeuraPulse — submit a guest post, explore sponsorship, or subscribe to our "
        "free weekly AI newsletter. Trusted by 32,000+ monthly readers. Reply within 24–48 hours."
    ),
    "blog.html": (
        "NeuraPulse Blog — All 200+ AI Articles on Gemini, ChatGPT & Automation",
        "Browse all 200+ expert AI articles on NeuraPulse. Topics include Gemini AI advertising, "
        "ChatGPT ads, AI tools, LLMs, automation, ethics and the future of artificial intelligence."
    ),
    "privacy-policy.html": (
        "Privacy Policy — NeuraPulse AI Blog",
        "Read the NeuraPulse privacy policy. Learn how we collect, use and protect your personal "
        "information when you visit our AI blog or subscribe to our newsletter."
    ),
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_all_html_files():
    """Walk the repo and collect every .html file."""
    found = []
    for root, dirs, files in os.walk(SITE_ROOT):
        # skip hidden folders like .git, .github
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith('.html') and f not in SKIP_FILES:
                found.append(os.path.join(root, f))
    return found


def rel_path(filepath):
    """Return path relative to repo root, e.g. blog/my-article.html"""
    return os.path.relpath(filepath, SITE_ROOT)


def canonical_url(filepath):
    rp = rel_path(filepath).replace("\\", "/")
    if rp == "index.html":
        return SITE_URL + "/"
    return SITE_URL + "/" + rp


def guess_title_desc(filepath, html):
    """Try to infer a good title/description from the existing HTML."""
    rp = rel_path(filepath).replace("\\", "/")

    # Use override table first
    fname = os.path.basename(filepath)
    if fname in PAGE_META:
        return PAGE_META[fname]

    # Extract existing title
    t = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    existing_title = t.group(1).strip() if t else ""

    # Extract existing description
    d = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    existing_desc = d.group(1).strip() if d else ""

    # Extract h1 as fallback
    h = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    h1_text = re.sub(r'<[^>]+>', '', h.group(1)).strip() if h else ""

    # Build title
    title = existing_title if existing_title else (h1_text + " — NeuraPulse" if h1_text else "NeuraPulse AI Blog")
    # Ensure brand suffix
    if "NeuraPulse" not in title:
        title = title + " — NeuraPulse"
    # Trim to ~60 chars
    if len(title) > 65:
        title = title[:62].rstrip() + "..."

    # Build description
    if existing_desc and len(existing_desc) >= 120:
        desc = existing_desc
    else:
        base = existing_desc if existing_desc else (h1_text if h1_text else "Expert AI article on NeuraPulse")
        desc = (base + " — Read expert AI insights, research and analysis on NeuraPulse. "
                "Join 32,000+ monthly readers for the latest on Gemini AI, ChatGPT ads, LLMs and automation.")
    # Trim to ~160 chars
    if len(desc) > 165:
        desc = desc[:162].rstrip() + "..."

    return title, desc


# ─────────────────────────────────────────────
# FIX FUNCTIONS
# ─────────────────────────────────────────────

def fix_title(html, title):
    if re.search(r'<title[^>]*>.*?</title>', html, re.IGNORECASE | re.DOTALL):
        html = re.sub(r'<title[^>]*>.*?</title>', f'<title>{title}</title>', html,
                      flags=re.IGNORECASE | re.DOTALL)
    else:
        html = html.replace('</head>', f'  <title>{title}</title>\n</head>', 1)
    return html


def fix_meta_description(html, desc):
    if re.search(r'<meta\s+name=["\']description["\']', html, re.IGNORECASE):
        html = re.sub(
            r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\'](\s*/?>)',
            f'<meta name="description" content="{desc}"\\2',
            html, flags=re.IGNORECASE
        )
    else:
        html = html.replace('</head>', f'  <meta name="description" content="{desc}">\n</head>', 1)
    return html


def fix_og_tags(html, title, desc, url):
    # og:title
    if re.search(r'<meta\s+property=["\']og:title["\']', html, re.IGNORECASE):
        html = re.sub(
            r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\'](\s*/?>)',
            f'<meta property="og:title" content="{title}"\\2',
            html, flags=re.IGNORECASE
        )
    else:
        html = html.replace('</head>', f'  <meta property="og:title" content="{title}">\n</head>', 1)

    # og:description
    if re.search(r'<meta\s+property=["\']og:description["\']', html, re.IGNORECASE):
        html = re.sub(
            r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\'](\s*/?>)',
            f'<meta property="og:description" content="{desc}"\\2',
            html, flags=re.IGNORECASE
        )
    else:
        html = html.replace('</head>', f'  <meta property="og:description" content="{desc}">\n</head>', 1)

    # og:image
    if not re.search(r'<meta\s+property=["\']og:image["\']', html, re.IGNORECASE):
        html = html.replace('</head>', f'  <meta property="og:image" content="{OG_IMAGE}">\n</head>', 1)

    # og:url
    if re.search(r'<meta\s+property=["\']og:url["\']', html, re.IGNORECASE):
        html = re.sub(
            r'<meta\s+property=["\']og:url["\']\s+content=["\'](.*?)["\'](\s*/?>)',
            f'<meta property="og:url" content="{url}"\\2',
            html, flags=re.IGNORECASE
        )
    else:
        html = html.replace('</head>', f'  <meta property="og:url" content="{url}">\n</head>', 1)

    # og:type
    if not re.search(r'<meta\s+property=["\']og:type["\']', html, re.IGNORECASE):
        html = html.replace('</head>', '  <meta property="og:type" content="article">\n</head>', 1)

    return html


def fix_twitter_tags(html, title, desc):
    if not re.search(r'<meta\s+(?:name|property)=["\']twitter:card["\']', html, re.IGNORECASE):
        html = html.replace('</head>',
            f'  <meta name="twitter:card" content="summary_large_image">\n'
            f'  <meta name="twitter:title" content="{title}">\n'
            f'  <meta name="twitter:description" content="{desc}">\n'
            f'  <meta name="twitter:image" content="{OG_IMAGE}">\n</head>', 1)
    return html


def fix_canonical(html, url):
    if not re.search(r'<link\s+rel=["\']canonical["\']', html, re.IGNORECASE):
        html = html.replace('</head>', f'  <link rel="canonical" href="{url}">\n</head>', 1)
    return html


def fix_robots(html):
    if not re.search(r'<meta\s+name=["\']robots["\']', html, re.IGNORECASE):
        html = html.replace('</head>', '  <meta name="robots" content="index, follow">\n</head>', 1)
    return html


def fix_privacy_links(html):
    """
    Fix ALL privacy policy links so they:
    - Open in new tab (target="_blank")
    - Do NOT refresh the page (onclick prevents default + stops propagation)
    """
    # Match any <a> tag that links to privacy-policy
    pattern = re.compile(
        r'<a\s+([^>]*href=["\'][^"\']*privacy[^"\']*["\'][^>]*)>',
        re.IGNORECASE
    )

    def replace_link(m):
        attrs = m.group(1)
        # Remove existing target, onclick attrs so we can replace cleanly
        attrs = re.sub(r'\s*target=["\'][^"\']*["\']', '', attrs)
        attrs = re.sub(r'\s*onclick=["\'][^"\']*["\']', '', attrs)
        return (f'<a {attrs.strip()} target="_blank" rel="noopener noreferrer" '
                f'onclick="event.stopPropagation();window.open(this.href,\'_blank\');return false;">')

    return pattern.sub(replace_link, html)


def fix_popup_css(html):
    """Add popup.css link if not present."""
    if '/popup.css' not in html:
        html = html.replace('</head>', '  <link rel="stylesheet" href="/popup.css">\n</head>', 1)
    return html


def fix_popup_js(html):
    """Add popup.js script before </body> if not present."""
    if '/popup.js' not in html:
        html = html.replace('</body>', '  <script src="/popup.js"></script>\n</body>', 1)
    return html


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        original = f.read()

    html = original
    url = canonical_url(filepath)
    title, desc = guess_title_desc(filepath, html)

    html = fix_title(html, title)
    html = fix_meta_description(html, desc)
    html = fix_og_tags(html, title, desc, url)
    html = fix_twitter_tags(html, title, desc)
    html = fix_canonical(html, url)
    html = fix_robots(html)
    html = fix_privacy_links(html)
    html = fix_popup_css(html)
    html = fix_popup_js(html)

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True  # changed
    return False  # no change


def main():
    files = get_all_html_files()
    print(f"Found {len(files)} HTML files to process...\n")

    changed = 0
    skipped = 0
    errors = 0

    for fp in sorted(files):
        try:
            was_changed = process_file(fp)
            rp = rel_path(fp)
            if was_changed:
                print(f"  ✅ FIXED  — {rp}")
                changed += 1
            else:
                print(f"  ⏭  SKIP   — {rp} (no changes needed)")
                skipped += 1
        except Exception as e:
            print(f"  ❌ ERROR  — {rel_path(fp)}: {e}")
            errors += 1

    print(f"\n{'='*50}")
    print(f"Done! {changed} files fixed, {skipped} already OK, {errors} errors.")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
