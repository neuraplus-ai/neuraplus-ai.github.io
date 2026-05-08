"""
NeuraPulse — Full Site SEO Fixer (Fixed for your file format)
=============================================================
PROBLEMS THIS FIXES:
1. Title truncated  → "AI Agents for SEO... — Neur..."  fixed to full clean title
2. og:title truncated → same fix
3. Description 156 chars → shortened to under 155
4. og:image missing → added to all files
5. Twitter card tags missing → all 6 added
6. Privacy popup script → added to all files
7. Modified date → added/updated

HOW TO USE:
1. Delete the OLD fix_all_blogs.py from your GitHub repo
2. Upload this NEW file to root of your GitHub repo
3. Go to Actions tab → Fix All Blog SEO → Run workflow
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

try:
    from bs4 import BeautifulSoup
except ImportError:
    os.system("pip install beautifulsoup4")
    from bs4 import BeautifulSoup


# ================================================================
# CONFIGURATION
# ================================================================
SITE_URL         = "https://neuraplus-ai.github.io"
SITE_NAME        = "NeuraPulse"
TWITTER_HANDLE   = "@neuraplus_ai"
DEFAULT_OG_IMAGE = "https://neuraplus-ai.github.io/images/og-default.jpg"
AUTHOR           = "Prashant Lalwani"

SCAN_FOLDERS = [".", "blog"]

SKIP_FILES = ["404.html", "sitemap.html", "privacy-policy.html"]
# ================================================================


def fix_truncated_text(text):
    """Remove truncation artifacts like '— Neur...', '...', 'Neur...' from end of text"""
    if not text:
        return text
    # Remove common truncation patterns
    patterns = [
        r'\s*—\s*Neur\.\.\.$',       # — Neur...
        r'\s*—\s*NeuraPulse\.\.\.$',  # — NeuraPulse...
        r'\s*-\s*Neur\.\.\.$',        # - Neur...
        r'\s*\|\s*Neur\.\.\.$',       # | Neur...
        r'\s*\.\.\.$',                # just ...
        r'\s*…$',                     # ellipsis character
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text.strip())
    return text.strip()


def build_full_title(title, site_name=SITE_NAME):
    """Remove site name suffix then add it back cleanly"""
    # Remove existing site name suffix
    for sep in [f" — {site_name}", f" - {site_name}", f" | {site_name}"]:
        if sep in title:
            title = title.replace(sep, "").strip()
    # Clean truncation
    title = fix_truncated_text(title)
    return title


def shorten_title(title, max_length=60):
    """Shorten to max 60 chars"""
    # First fix truncation
    title = build_full_title(title)
    if len(title) <= max_length:
        return title
    # Remove year in parentheses
    title = re.sub(r'\s*\(\d{4}\)', '', title).strip()
    if len(title) <= max_length:
        return title
    # Truncate at word boundary
    return title[:max_length - 3].rsplit(' ', 1)[0] + "..."


def shorten_description(desc, max_length=155):
    """Shorten to max 155 chars"""
    desc = fix_truncated_text(desc)
    if len(desc) <= max_length:
        return desc
    truncated   = desc[:max_length - 3]
    last_period = truncated.rfind('.')
    last_comma  = truncated.rfind(',')
    if last_period > max_length * 0.7:
        return truncated[:last_period + 1]
    elif last_comma > max_length * 0.7:
        return truncated[:last_comma] + "..."
    return truncated.rsplit(' ', 1)[0] + "..."


def get_page_url(filepath):
    rel = Path(filepath).as_posix().lstrip("./")
    return f"{SITE_URL}/{rel}"


def collect_html_files():
    all_files, seen = [], set()
    for folder in SCAN_FOLDERS:
        fp = Path(folder)
        if not fp.exists():
            print(f"  ⚠️  Folder not found: {folder}")
            continue
        files = list(fp.glob("*.html")) if folder == "." else list(fp.rglob("*.html"))
        for f in files:
            r = str(f.resolve())
            if r not in seen and f.name not in SKIP_FILES:
                seen.add(r)
                all_files.append(f)
    return sorted(all_files)


def fix_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    soup    = BeautifulSoup(content, 'html.parser')
    changes = []

    head = soup.find('head')
    if not head:
        return False, ["No <head> tag — skipped"]

    page_url = get_page_url(filepath)

    # ── 1. FIX TITLE TAG ─────────────────────────────────────
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        original  = title_tag.string.strip()
        fixed     = shorten_title(original)
        if fixed != original:
            title_tag.string = fixed
            changes.append(f"Title fixed: '{original[:40]}...' → '{fixed}'")
    clean_title = title_tag.string.strip() if title_tag and title_tag.string else SITE_NAME

    # ── 2. FIX META DESCRIPTION ──────────────────────────────
    meta_desc        = soup.find('meta', attrs={'name': 'description'})
    description_text = ""
    if meta_desc:
        original         = meta_desc.get('content', '')
        description_text = shorten_description(original)
        if description_text != original:
            meta_desc['content'] = description_text
            changes.append(f"Description: {len(original)} → {len(description_text)} chars")
        else:
            description_text = original

    # ── 3. FIX og:title (most important — was truncated) ─────
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    if og_title:
        original = og_title.get('content', '')
        fixed    = fix_truncated_text(original)
        # Also remove site name for og:title (keep it shorter)
        fixed    = build_full_title(fixed)
        if len(fixed) > 60:
            fixed = shorten_title(fixed)
        if fixed != original:
            og_title['content'] = fixed
            changes.append(f"og:title fixed: '{original[:40]}...' → '{fixed}'")
    else:
        # Add og:title if missing
        tag = soup.new_tag('meta')
        tag['property'] = 'og:title'
        tag['content']  = clean_title
        head.append(tag)
        changes.append("Added og:title")

    # ── 4. ADD MISSING OG TAGS ───────────────────────────────
    og_missing = {
        'og:description': description_text,
        'og:image'      : DEFAULT_OG_IMAGE,
        'og:site_name'  : SITE_NAME,
    }
    for prop, val in og_missing.items():
        existing = soup.find('meta', attrs={'property': prop})
        if not existing:
            tag = soup.new_tag('meta')
            tag['property'] = prop
            tag['content']  = val
            head.append(tag)
            changes.append(f"Added {prop}")
        elif prop == 'og:description' and existing.get('content', '') != val and val:
            existing['content'] = val
            changes.append(f"Updated {prop}")

    # ── 5. ADD TWITTER CARD TAGS ─────────────────────────────
    twitter_tags = {
        'twitter:card'       : 'summary_large_image',
        'twitter:title'      : clean_title,
        'twitter:description': description_text[:200] if description_text else '',
        'twitter:image'      : DEFAULT_OG_IMAGE,
        'twitter:site'       : TWITTER_HANDLE,
        'twitter:creator'    : TWITTER_HANDLE,
    }
    for name, val in twitter_tags.items():
        existing = soup.find('meta', attrs={'name': name})
        if not existing:
            tag = soup.new_tag('meta')
            tag['name']    = name
            tag['content'] = val
            head.append(tag)
            changes.append(f"Added {name}")

    # ── 6. MODIFIED DATE ─────────────────────────────────────
    modified_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')
    existing_mod  = soup.find('meta', attrs={'property': 'article:modified_time'})
    if existing_mod:
        existing_mod['content'] = modified_time
    else:
        tag = soup.new_tag('meta')
        tag['property'] = 'article:modified_time'
        tag['content']  = modified_time
        head.append(tag)
        changes.append("Added modified time")

    # ── 7. FIX H1 POSITION ───────────────────────────────────
    body = soup.find('body')
    if body:
        all_headings = body.find_all(['h1', 'h2', 'h3', 'h4'])
        h1_tags      = body.find_all('h1')
        if all_headings and h1_tags and all_headings[0].name != 'h1':
            all_headings[0].insert_before(h1_tags[0].extract())
            changes.append("Fixed H1 position")

    # ── 8. ADD PRIVACY POPUP SCRIPT ──────────────────────────
    if body:
        already = any(
            'privacy-popup' in (s.get('src') or '')
            for s in body.find_all('script', src=True)
        )
        if not already:
            tag = soup.new_tag('script')
            tag['src'] = '/privacy-popup.js'
            body.append(tag)
            changes.append("Added privacy popup")

    # ── 9. SAVE ───────────────────────────────────────────────
    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True, changes

    return False, []


def fix_all():
    print("=" * 65)
    print("  NeuraPulse — Full Site Fixer")
    print("=" * 65)

    all_files = collect_html_files()
    if not all_files:
        print("\n❌ No HTML files found. Run from repo ROOT folder.")
        return

    print(f"\n✅ Found {len(all_files)} HTML files\n")

    fixed, skipped, errors = 0, 0, []

    for i, fp in enumerate(all_files, 1):
        try:
            print(f"[{i:>3}/{len(all_files)}] {fp}")
            was_fixed, changes = fix_html_file(fp)
            if was_fixed:
                fixed += 1
                for c in changes:
                    print(f"         ✅ {c}")
            else:
                skipped += 1
                print(f"         ⏭️  No changes needed")
        except Exception as e:
            errors.append(str(fp))
            print(f"         ❌ Error: {e}")

    print("\n" + "=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    print(f"  Total   : {len(all_files)}")
    print(f"  Fixed   : {fixed}")
    print(f"  Skipped : {skipped}")
    print(f"  Errors  : {len(errors)}")
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
    print("=" * 65)
    print("\n✅ Done! GitHub Action will commit and push all changes.")


def fix_specific_files(file_list):
    """Fix only the files passed via --files argument (for auto trigger)"""
    print("=" * 65)
    print("  NeuraPulse — Auto SEO Fix (New/Updated Files)")
    print("=" * 65)

    files = [Path(f.strip()) for f in file_list.split() if f.strip().endswith('.html')]
    files = [f for f in files if f.exists() and f.name not in SKIP_FILES]

    if not files:
        print("\n⚠️  No valid HTML files found in the changed list.")
        print("   Running full site fix instead...")
        fix_all()
        return

    print(f"\n✅ Fixing {len(files)} changed file(s)\n")
    fixed, errors = 0, []

    for fp in files:
        try:
            print(f"  → {fp}")
            was_fixed, changes = fix_html_file(fp)
            if was_fixed:
                fixed += 1
                for c in changes:
                    print(f"     ✅ {c}")
            else:
                print(f"     ⏭️  Already good")
        except Exception as e:
            errors.append(str(fp))
            print(f"     ❌ Error: {e}")

    print(f"\n✅ Done! {fixed} file(s) fixed automatically.")


if __name__ == "__main__":
    # If --files argument passed, fix only those files
    # Otherwise fix all files (manual run)
    if "--files" in sys.argv:
        idx = sys.argv.index("--files")
        file_list = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        fix_specific_files(file_list)
    else:
        fix_all()
