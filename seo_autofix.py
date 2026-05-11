#!/usr/bin/env python3
"""
NeuraPulse SEO Auto-Fix Script
--------------------------------
Based on actual site analysis (May 2026):

WHAT THIS FIXES:
  index.html:
    - Adds missing og:description + og:image meta tags
    - Adds WebSite + Person JSON-LD schema
    - Fixes broken <li></a></li> nav tag
    - Converts <div class="st"> section divs to <h2> tags

  about.html:
    - Adds missing og:image
    - Adds Twitter Card tags (missing entirely)

  blog.html, contact.html, privacy-policy.html:
    - Ensures og:image, og:description, Twitter Cards present
    - Adds schema if missing

  All 250+ blog posts in /blog/:
    - Adds BlogPosting JSON-LD schema (completely missing on all posts)
    - Upgrades generic meta description to keyword-rich one
    - Ensures og:image present

  Creates:
    - robots.txt  (missing)
    - llms.txt    (missing)

WHAT THIS PRESERVES (never overwrites):
  - Existing canonical tags
  - Existing OG title / url tags
  - Existing meta descriptions that are already unique/good
  - Existing schema on about.html (AboutPage)
  - All page content, styles, scripts
"""

import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

BASE_URL  = "https://neuraplus-ai.github.io"
SITE_NAME = "NeuraPulse"
AUTHOR    = "Prashant Lalwani"
TWITTER   = "@neuraplus_ai"
OG_IMAGE  = f"{BASE_URL}/favicon.svg"

GENERIC_DESC_PATTERN = re.compile(
    r"^Read '.+' on the NeuraPlusAI blog\.$"
)

# ── Create missing root files ─────────────────────────────────────────────────

def write_robots():
    p = Path("robots.txt")
    if not p.exists():
        p.write_text(
            f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n"
        )
        print("✅  robots.txt created")
    else:
        print("⏭️   robots.txt already exists — skipped")


def write_llms():
    p = Path("llms.txt")
    if not p.exists():
        p.write_text(f"""# {SITE_NAME}
> Expert AI blog by {AUTHOR}. Covers Gemini AI advertising, ChatGPT ads, AI automation, AI tools, LLMs, and the future of AI. No hype. Just clarity.

## Pages
- Home: {BASE_URL}/
- Blog: {BASE_URL}/blog.html
- About: {BASE_URL}/about.html
- Contact: {BASE_URL}/contact.html
- Privacy: {BASE_URL}/privacy-policy.html

## Topics
- Gemini AI Advertising & ChatGPT Ads
- AI Automation (n8n, Zapier, Make)
- AI Tools (Groq, ElevenLabs, DeepL, Ollama, Perplexity)
- LLMs, Context Windows, Transformers
- Future of AI & AGI

## Sitemap
{BASE_URL}/sitemap.xml
""")
        print("✅  llms.txt created")
    else:
        print("⏭️   llms.txt already exists — skipped")


# ── Meta helpers ──────────────────────────────────────────────────────────────

def get_meta(soup, *, name=None, property=None):
    if name:
        t = soup.find("meta", {"name": name})
        return t["content"].strip() if t and t.get("content") else None
    if property:
        t = soup.find("meta", {"property": property})
        return t["content"].strip() if t and t.get("content") else None
    return None


def set_meta(soup, *, name=None, property=None, value):
    """Add tag only if missing — never overwrites."""
    if name:
        if not soup.find("meta", {"name": name}):
            t = soup.new_tag("meta", attrs={"name": name, "content": value})
            soup.head.append(t)
    elif property:
        if not soup.find("meta", {"property": property}):
            t = soup.new_tag("meta", attrs={"property": property, "content": value})
            soup.head.append(t)


def update_meta(soup, *, name=None, property=None, value):
    """Set or overwrite a meta tag."""
    if name:
        t = soup.find("meta", {"name": name})
        if t:
            t["content"] = value
        else:
            t = soup.new_tag("meta", attrs={"name": name, "content": value})
            soup.head.append(t)
    elif property:
        t = soup.find("meta", {"property": property})
        if t:
            t["content"] = value
        else:
            t = soup.new_tag("meta", attrs={"property": property, "content": value})
            soup.head.append(t)


def has_schema(soup):
    return bool(soup.find("script", {"type": "application/ld+json"}))


# ── Schema builders ───────────────────────────────────────────────────────────

def add_website_schema(soup):
    if has_schema(soup):
        return
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "name": SITE_NAME,
                "url": f"{BASE_URL}/",
                "description": "Expert AI articles on Gemini AI advertising, ChatGPT ads, AI automation, and AI tools.",
                "inLanguage": "en",
                "publisher": {
                    "@type": "Person",
                    "name": AUTHOR,
                    "url": f"{BASE_URL}/about.html"
                }
            },
            {
                "@type": "Person",
                "name": AUTHOR,
                "url": f"{BASE_URL}/about.html",
                "sameAs": [
                    "https://twitter.com/neuraplus_ai",
                    "https://x.com/AiNeuraplus"
                ]
            }
        ]
    }
    s = soup.new_tag("script", type="application/ld+json")
    s.string = json.dumps(schema, indent=2)
    soup.head.append(s)


def add_article_schema(soup, title, description, url):
    if has_schema(soup):
        return
    # Extract date from page body
    date_str = "2026-01-01"
    body_text = soup.get_text()
    m = re.search(r"20\d\d-\d\d-\d\d", body_text)
    if m:
        date_str = m.group(0)
    else:
        # Try "March 2, 2026" style
        months = {"January":"01","February":"02","March":"03","April":"04",
                  "May":"05","June":"06","July":"07","August":"08",
                  "September":"09","October":"10","November":"11","December":"12"}
        m2 = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d\d)", body_text)
        if m2:
            mo, day, yr = m2.group(1), m2.group(2).zfill(2), m2.group(3)
            date_str = f"{yr}-{months[mo]}-{day}"

    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": description,
        "url": url,
        "datePublished": date_str,
        "dateModified": date_str,
        "inLanguage": "en",
        "author": {
            "@type": "Person",
            "name": AUTHOR,
            "url": f"{BASE_URL}/about.html"
        },
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": f"{BASE_URL}/",
            "logo": {"@type": "ImageObject", "url": OG_IMAGE}
        },
        "image": OG_IMAGE,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url
        }
    }
    s = soup.new_tag("script", type="application/ld+json")
    s.string = json.dumps(schema, indent=2)
    soup.head.append(s)


# ── Fix broken nav ────────────────────────────────────────────────────────────

def fix_broken_nav(soup):
    """Remove empty <li></a></li> artifacts found in index.html."""
    for li in soup.find_all("li"):
        if not li.find("a") and not li.get_text(strip=True):
            li.decompose()


# ── Fix heading divs ──────────────────────────────────────────────────────────

def fix_heading_divs(soup):
    """Convert <div class="st"> to <h2 class="st"> for proper heading hierarchy."""
    changed = 0
    for div in soup.find_all("div", class_="st"):
        h2 = soup.new_tag("h2", attrs={"class": "st"})
        h2.string = div.get_text(strip=True)
        div.replace_with(h2)
        changed += 1
    return changed


# ── Better blog description ───────────────────────────────────────────────────

def make_better_description(title, body_text):
    """Build a keyword-rich description from the page body text."""
    sentences = re.split(r'(?<=[.!?])\s+', body_text.strip())
    for s in sentences:
        s = s.strip()
        # Skip short, nav-like, or generic strings
        if (len(s) > 80 and len(s) < 400
                and not s.startswith("Read '")
                and not s.startswith("Home")
                and not s.startswith("©")
                and "NeuraPulse" not in s[:20]):
            return (s[:157] + "...") if len(s) > 160 else s
    # Fallback
    desc = f"{title} — Expert AI insights on NeuraPulse by {AUTHOR}."
    return (desc[:157] + "...") if len(desc) > 160 else desc


# ── Per-file processors ───────────────────────────────────────────────────────

def fix_index(soup):
    title = "NeuraPulse — AI Insights, Advertising & Future of Intelligence"
    desc  = (get_meta(soup, name="description") or
             "NeuraPulse — 200+ expert AI articles on Gemini AI advertising, "
             "ChatGPT ads, AI automation, and tools. By Prashant Lalwani.")
    # Fill missing OG tags
    set_meta(soup, property="og:description", value=desc)
    set_meta(soup, property="og:image",       value=OG_IMAGE)
    set_meta(soup, property="og:site_name",   value=SITE_NAME)
    # Twitter Cards (absent on index)
    set_meta(soup, name="twitter:card",        value="summary_large_image")
    set_meta(soup, name="twitter:site",        value=TWITTER)
    set_meta(soup, name="twitter:title",       value=title)
    set_meta(soup, name="twitter:description", value=desc)
    set_meta(soup, name="twitter:image",       value=OG_IMAGE)
    # WebSite schema
    add_website_schema(soup)
    # Fix broken nav list item
    fix_broken_nav(soup)
    # Convert section <div class="st"> to <h2>
    n = fix_heading_divs(soup)
    if n:
        print(f"     ↳ fixed {n} div.st → h2")


def fix_about(soup):
    set_meta(soup, property="og:image",    value=OG_IMAGE)
    set_meta(soup, property="og:site_name", value=SITE_NAME)
    title = get_meta(soup, property="og:title") or "About — NeuraPulse AI Blog"
    desc  = (get_meta(soup, property="og:description") or
             "Meet the team behind NeuraPulse — making AI understandable for everyone.")
    set_meta(soup, name="twitter:card",        value="summary_large_image")
    set_meta(soup, name="twitter:site",        value=TWITTER)
    set_meta(soup, name="twitter:title",       value=title)
    set_meta(soup, name="twitter:description", value=desc)
    set_meta(soup, name="twitter:image",       value=OG_IMAGE)


def fix_generic_page(soup, filepath):
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else filepath.stem.replace("-", " ").title()
    desc  = get_meta(soup, name="description") or f"{title} — NeuraPulse."
    url   = f"{BASE_URL}/{filepath.name}"

    set_meta(soup, property="og:title",       value=title)
    set_meta(soup, property="og:description", value=desc)
    set_meta(soup, property="og:url",         value=url)
    set_meta(soup, property="og:image",       value=OG_IMAGE)
    set_meta(soup, property="og:site_name",   value=SITE_NAME)
    set_meta(soup, property="og:type",        value="website")
    set_meta(soup, name="twitter:card",        value="summary_large_image")
    set_meta(soup, name="twitter:site",        value=TWITTER)
    set_meta(soup, name="twitter:title",       value=title)
    set_meta(soup, name="twitter:description", value=desc)
    set_meta(soup, name="twitter:image",       value=OG_IMAGE)
    if not has_schema(soup):
        add_website_schema(soup)


def fix_blog_post(soup, filepath):
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""
    # Strip " – NeuraPlusAI Blog" suffix
    title = re.sub(r"\s*[–—-]\s*NeuraPlusAI Blog.*$", "", title).strip()
    title = re.sub(r"\s*[–—-]\s*NeuraPulse.*$", "", title).strip()

    url = f"{BASE_URL}/blog/{filepath.name}"

    existing_desc = get_meta(soup, name="description")
    if not existing_desc or GENERIC_DESC_PATTERN.match(existing_desc):
        body_text = soup.get_text(separator=" ", strip=True)
        new_desc = make_better_description(title, body_text)
        update_meta(soup, name="description",        value=new_desc)
        update_meta(soup, property="og:description", value=new_desc)
        update_meta(soup, name="twitter:description", value=new_desc)
        desc = new_desc
    else:
        desc = existing_desc

    set_meta(soup, property="og:image",     value=OG_IMAGE)
    set_meta(soup, property="og:site_name", value=SITE_NAME)
    set_meta(soup, property="og:type",      value="article")
    set_meta(soup, name="twitter:card",  value="summary_large_image")
    set_meta(soup, name="twitter:site",  value=TWITTER)
    set_meta(soup, name="twitter:image", value=OG_IMAGE)

    # Add BlogPosting JSON-LD — MISSING on all 250+ posts
    add_article_schema(soup, title, desc, url)


# ── Dispatcher ────────────────────────────────────────────────────────────────

def process_file(filepath: Path):
    raw  = filepath.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "lxml")
    if not soup.head:
        return

    rel = str(filepath).replace("\\", "/")
    if rel == "index.html":
        fix_index(soup)
    elif rel == "about.html":
        fix_about(soup)
    elif rel in ("blog.html", "contact.html", "privacy-policy.html"):
        fix_generic_page(soup, filepath)
    elif rel.startswith("blog/"):
        fix_blog_post(soup, filepath)

    filepath.write_text(str(soup), encoding="utf-8")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  NeuraPulse SEO Auto-Fix")
    print("=" * 55)

    write_robots()
    write_llms()

    print("\n📄  Root pages...")
    for name in ["index.html", "about.html", "blog.html",
                 "contact.html", "privacy-policy.html"]:
        p = Path(name)
        if p.exists():
            process_file(p)
            print(f"   ✅  {name}")
        else:
            print(f"   ⚠️   {name} not found")

    print("\n📝  Blog posts...")
    blog_dir = Path("blog")
    if not blog_dir.is_dir():
        print("   ⚠️   /blog directory not found!")
        return

    posts  = sorted(blog_dir.glob("*.html"))
    total  = len(posts)
    errors = 0
    for i, p in enumerate(posts, 1):
        try:
            process_file(p)
        except Exception as e:
            print(f"   ❌  {p.name}: {e}")
            errors += 1
        if i % 50 == 0 or i == total:
            print(f"   {i}/{total} done")

    print(f"\n{'=' * 55}")
    print(f"  ✅  {total - errors}/{total} blog posts fixed")
    if errors:
        print(f"  ⚠️  {errors} errors (see above)")
    print("=" * 55)


if __name__ == "__main__":
    main()
