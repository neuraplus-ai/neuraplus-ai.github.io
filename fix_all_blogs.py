"""
NeuraPulse Blog SEO Fixer
=========================
This script fixes ALL HTML blog files in your /blog/ folder automatically.

What it fixes:
1. Meta title (shortens to under 60 chars)
2. Meta description (shortens to under 155 chars)
3. Adds Open Graph tags (og:title, og:description, og:image, og:url, og:type)
4. Adds Twitter Card tags
5. Fixes H1 position (ensures H1 is first heading)
6. Adds last modified date

HOW TO USE:
1. Download/clone your GitHub repo to your computer
2. Place this script in the ROOT of your repo (same level as /blog/ folder)
3. Install required library: pip install beautifulsoup4
4. Run: python fix_all_blogs.py
5. Check the /blog/ folder - all files will be fixed
6. Push changes to GitHub
"""

import os
import re
from pathlib import Path
from datetime import datetime

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing beautifulsoup4...")
    os.system("pip install beautifulsoup4")
    from bs4 import BeautifulSoup

# ============================================================
# CONFIGURATION - Change these values for your site
# ============================================================
SITE_URL = "https://neuraplus-ai.github.io"
SITE_NAME = "NeuraPulse"
TWITTER_HANDLE = "@neuraplus_ai"  # Change to your Twitter handle
DEFAULT_OG_IMAGE = "https://neuraplus-ai.github.io/images/og-default.jpg"  # Change to your OG image
BLOG_FOLDER = "./blog"  # Path to your blog folder
AUTHOR = "Prashant Lalwani"
# ============================================================


def shorten_title(title, max_length=60):
    """Shorten title to max_length characters intelligently"""
    if len(title) <= max_length:
        return title
    
    # Remove site name suffix if present
    for suffix in [f" — {SITE_NAME}", f" - {SITE_NAME}", f" | {SITE_NAME}"]:
        if suffix in title:
            title = title.replace(suffix, "")
            if len(title) <= max_length:
                return title.strip()
    
    # Remove year in parentheses if too long
    title = re.sub(r'\s*\(\d{4}\)', '', title).strip()
    if len(title) <= max_length:
        return title
    
    # Truncate at last word boundary before max_length
    if len(title) > max_length:
        title = title[:max_length-3].rsplit(' ', 1)[0] + "..."
    
    return title


def shorten_description(desc, max_length=155):
    """Shorten meta description to max_length characters"""
    if len(desc) <= max_length:
        return desc
    
    # Truncate at last sentence or word boundary
    truncated = desc[:max_length-3]
    
    # Try to end at a sentence
    last_period = truncated.rfind('.')
    last_comma = truncated.rfind(',')
    
    if last_period > max_length * 0.7:
        return truncated[:last_period+1]
    elif last_comma > max_length * 0.7:
        return truncated[:last_comma] + "..."
    else:
        return truncated.rsplit(' ', 1)[0] + "..."


def get_page_url(filepath):
    """Generate the full URL for a page based on its file path"""
    # Convert file path to URL
    path = Path(filepath)
    # Get relative path from blog folder
    rel_path = path.name
    return f"{SITE_URL}/blog/{rel_path}"


def fix_html_file(filepath):
    """Fix all SEO issues in a single HTML file"""
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    changes = []
    
    # --------------------------------------------------------
    # 1. GET HEAD TAG
    # --------------------------------------------------------
    head = soup.find('head')
    if not head:
        print(f"  ⚠️  No <head> tag found in {filepath}")
        return False, []
    
    page_url = get_page_url(filepath)
    
    # --------------------------------------------------------
    # 2. FIX TITLE TAG
    # --------------------------------------------------------
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        original_title = title_tag.string.strip()
        short_title = shorten_title(original_title)
        if short_title != original_title:
            title_tag.string = short_title
            changes.append(f"Title shortened: {len(original_title)} → {len(short_title)} chars")
    
    # Get clean title for OG tags
    clean_title = title_tag.string.strip() if title_tag and title_tag.string else SITE_NAME
    
    # --------------------------------------------------------
    # 3. FIX META DESCRIPTION
    # --------------------------------------------------------
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description_text = ""
    
    if meta_desc:
        original_desc = meta_desc.get('content', '')
        description_text = shorten_description(original_desc)
        if description_text != original_desc:
            meta_desc['content'] = description_text
            changes.append(f"Description shortened: {len(original_desc)} → {len(description_text)} chars")
        else:
            description_text = original_desc
    
    # --------------------------------------------------------
    # 4. ADD/FIX OPEN GRAPH TAGS
    # --------------------------------------------------------
    og_tags = {
        'og:title': clean_title,
        'og:description': description_text,
        'og:image': DEFAULT_OG_IMAGE,
        'og:url': page_url,
        'og:type': 'article',
        'og:site_name': SITE_NAME,
    }
    
    for og_property, og_content in og_tags.items():
        existing = soup.find('meta', attrs={'property': og_property})
        if existing:
            if existing.get('content') != og_content:
                existing['content'] = og_content
                changes.append(f"Updated {og_property}")
        else:
            new_tag = soup.new_tag('meta')
            new_tag['property'] = og_property
            new_tag['content'] = og_content
            head.append(new_tag)
            changes.append(f"Added {og_property}")
    
    # --------------------------------------------------------
    # 5. ADD/FIX TWITTER CARD TAGS
    # --------------------------------------------------------
    twitter_tags = {
        'twitter:card': 'summary_large_image',
        'twitter:title': clean_title,
        'twitter:description': description_text[:200] if description_text else '',
        'twitter:image': DEFAULT_OG_IMAGE,
        'twitter:site': TWITTER_HANDLE,
        'twitter:creator': TWITTER_HANDLE,
    }
    
    for tw_name, tw_content in twitter_tags.items():
        existing = soup.find('meta', attrs={'name': tw_name})
        if existing:
            if existing.get('content') != tw_content:
                existing['content'] = tw_content
                changes.append(f"Updated {tw_name}")
        else:
            new_tag = soup.new_tag('meta')
            new_tag['name'] = tw_name
            new_tag['content'] = tw_content
            head.append(new_tag)
            changes.append(f"Added {tw_name}")
    
    # --------------------------------------------------------
    # 6. ADD ARTICLE META TAGS
    # --------------------------------------------------------
    # Add author meta if missing
    if not soup.find('meta', attrs={'name': 'author'}):
        author_tag = soup.new_tag('meta')
        author_tag['name'] = 'author'
        author_tag['content'] = AUTHOR
        head.append(author_tag)
        changes.append("Added author meta tag")
    
    # Add/update article:modified_time
    modified_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')
    existing_modified = soup.find('meta', attrs={'property': 'article:modified_time'})
    if existing_modified:
        existing_modified['content'] = modified_time
    else:
        mod_tag = soup.new_tag('meta')
        mod_tag['property'] = 'article:modified_time'
        mod_tag['content'] = modified_time
        head.append(mod_tag)
        changes.append("Added article:modified_time")
    
    # --------------------------------------------------------
    # 7. FIX H1 POSITION - Ensure H1 is first heading
    # --------------------------------------------------------
    body = soup.find('body')
    if body:
        all_headings = body.find_all(['h1', 'h2', 'h3', 'h4'])
        if all_headings:
            first_heading = all_headings[0]
            h1_tags = body.find_all('h1')
            
            if h1_tags:
                first_h1 = h1_tags[0]
                # Check if H1 is NOT the first heading
                if first_heading.name != 'h1':
                    # Move H1 before the first heading
                    first_heading.insert_before(first_h1.extract())
                    changes.append("Fixed H1 position - moved to top")
    
    # --------------------------------------------------------
    # 8. WRITE FIXED FILE
    # --------------------------------------------------------
    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True, changes
    
    return False, []


def fix_all_blogs():
    """Main function - fix all HTML files in blog folder"""
    
    print("=" * 60)
    print("  NeuraPulse Blog SEO Fixer")
    print("=" * 60)
    
    blog_path = Path(BLOG_FOLDER)
    
    if not blog_path.exists():
        print(f"\n❌ ERROR: Blog folder not found at: {BLOG_FOLDER}")
        print("Make sure you run this script from the ROOT of your repo")
        print("Example: If your repo is at C:/myrepo/, run from there")
        return
    
    # Get all HTML files
    html_files = list(blog_path.glob("*.html"))
    
    if not html_files:
        print(f"\n❌ No HTML files found in {BLOG_FOLDER}")
        return
    
    print(f"\n✅ Found {len(html_files)} HTML files in {BLOG_FOLDER}")
    print(f"   Starting fixes...\n")
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, filepath in enumerate(html_files, 1):
        try:
            print(f"[{i}/{len(html_files)}] Processing: {filepath.name}")
            was_fixed, changes = fix_html_file(filepath)
            
            if was_fixed:
                fixed_count += 1
                for change in changes:
                    print(f"   ✅ {change}")
            else:
                skipped_count += 1
                print(f"   ⏭️  No changes needed")
                
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error: {e}")
    
    # --------------------------------------------------------
    # SUMMARY REPORT
    # --------------------------------------------------------
    print("\n" + "=" * 60)
    print("  SUMMARY REPORT")
    print("=" * 60)
    print(f"  Total files processed : {len(html_files)}")
    print(f"  Files fixed           : {fixed_count}")
    print(f"  Files skipped         : {skipped_count} (already good)")
    print(f"  Files with errors     : {error_count}")
    print("=" * 60)
    
    if fixed_count > 0:
        print(f"\n✅ Done! {fixed_count} files have been fixed.")
        print("\nNext steps:")
        print("  1. Review a few fixed files to make sure they look correct")
        print("  2. Run: git add .")
        print("  3. Run: git commit -m 'Fix SEO meta tags for all blog posts'")
        print("  4. Run: git push")
        print("  5. Wait 1-2 days for Google to re-crawl your pages")
    else:
        print("\n✅ All files were already optimized! No changes needed.")


if __name__ == "__main__":
    fix_all_blogs()
