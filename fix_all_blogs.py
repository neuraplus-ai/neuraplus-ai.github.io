#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuraPulse - Fix All 300+ HTML Pages
Only processes .html files in the current repo directory.
"""

import os
import re
import sys

SITE_URL = "https://neuraplus-ai.github.io"
OG_IMAGE = "https://neuraplus-ai.github.io/og-default.jpg"

# Only scan these folders - your repo folders
ALLOWED_ROOTS = {".", "./blog", "blog"}
SKIP_FILES = {"404.html", "sitemap.html", "googlea8e9563d4c0c037a.html"}

PAGE_META = {
    "index.html": (
        "NeuraPulse - 200+ Expert AI Articles on Gemini AI, ChatGPT Ads and LLMs",
        "NeuraPulse is your expert AI hub with 200+ research-backed articles on Gemini AI advertising, ChatGPT ads, AI automation, LLMs, and the future of intelligence. Updated weekly."
    ),
    "about.html": (
        "About NeuraPulse - Expert AI Writers and Researchers Behind 200+ Articles",
        "Meet the NeuraPulse team of ML engineers, researchers and writers making artificial intelligence understandable for marketers, developers and curious minds worldwide."
    ),
    "contact.html": (
        "Contact NeuraPulse - Guest Posts, Sponsorship and Free Newsletter",
        "Get in touch with NeuraPulse to submit a guest post, explore sponsorship, or subscribe to our free weekly AI newsletter. Trusted by 32,000+ monthly readers."
    ),
    "blog.html": (
        "NeuraPulse Blog - All 200+ AI Articles on Gemini, ChatGPT and Automation",
        "Browse all 200+ expert AI articles on NeuraPulse covering Gemini AI advertising, ChatGPT ads, AI tools, LLMs, automation, ethics and the future of artificial intelligence."
    ),
    "privacy-policy.html": (
        "Privacy Policy - NeuraPulse AI Blog",
        "Read the NeuraPulse privacy policy. Learn how we collect, use and protect your personal information when you visit our AI blog or subscribe to our newsletter."
    ),
}


def get_all_html_files():
    """Only get HTML files from root and blog/ folder."""
    found = []

    # Root level .html files
    for f in os.listdir("."):
        if f.endswith('.html') and f not in SKIP_FILES and os.path.isfile(f):
            found.append("./" + f)

    # blog/ subfolder
    if os.path.isdir("blog"):
        for f in os.listdir("blog"):
            if f.endswith('.html') and f not in SKIP_FILES and os.path.isfile("blog/" + f):
                found.append("blog/" + f)

    return found


def rel_path(filepath):
    return filepath.lstrip("./")


def canonical_url(filepath):
    rp = rel_path(filepath)
    if rp == "index.html":
        return SITE_URL + "/"
    return SITE_URL + "/" + rp


def guess_title_desc(filepath, html):
    fname = os.path.basename(filepath)
    if fname in PAGE_META:
        return PAGE_META[fname]

    t = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    existing_title = t.group(1).strip() if t else ""

    d = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    existing_desc = d.group(1).strip() if d else ""

    h = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    h1_text = re.sub(r'<[^>]+>', '', h.group(1)).strip() if h else ""

    title = existing_title if existing_title else (h1_text + " - NeuraPulse" if h1_text else "NeuraPulse AI Blog")
    if "NeuraPulse" not in title:
        title = title + " - NeuraPulse"
    if len(title) > 65:
        title = title[:62].rstrip() + "..."

    if existing_desc and len(existing_desc) >= 120:
        desc = existing_desc
    else:
        base = existing_desc if existing_desc else (h1_text if h1_text else "Expert AI article on NeuraPulse")
        desc = base + " - Expert AI insights on NeuraPulse. Join 32,000+ monthly readers for the latest on Gemini AI, ChatGPT ads, LLMs and automation."
    if len(desc) > 165:
        desc = desc[:162].rstrip() + "..."

    return title, desc


def fix_title(html, title):
    if re.search(r'<title[^>]*>.*?</title>', html, re.IGNORECASE | re.DOTALL):
        html = re.sub(r'<title[^>]*>.*?</title>', '<title>' + title + '</title>', html, flags=re.IGNORECASE | re.DOTALL)
    else:
        html = html.replace('</head>', '  <title>' + title + '</title>\n</head>', 1)
    return html


def fix_meta_description(html, desc):
    if re.search(r'<meta\s+name=["\']description["\']', html, re.IGNORECASE):
        html = re.sub(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\'](\s*/?>)',
                      '<meta name="description" content="' + desc + '"\\2', html, flags=re.IGNORECASE)
    else:
        html = html.replace('</head>', '  <meta name="description" content="' + desc + '">\n</head>', 1)
    return html


def fix_og_tags(html, title, desc, url):
    if re.search(r'<meta\s+property=["\']og:title["\']', html, re.IGNORECASE):
        html = re.sub(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\'](\s*/?>)',
                      '<meta property="og:title" content="' + title + '"\\2', html, flags=re.IGNORECASE)
    else:
        html = html.replace('</head>', '  <meta property="og:title" content="' + title + '">\n</head>', 1)

    if re.search(r'<meta\s+property=["\']og:description["\']', html, re.IGNORECASE):
        html = re.sub(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\'](\s*/?>)',
                      '<meta property="og:description" content="' + desc + '"\\2', html, flags=re.IGNORECASE)
    else:
        html = html.replace('</head>', '  <meta property="og:description" content="' + desc + '">\n</head>', 1)

    if not re.search(r'<meta\s+property=["\']og:image["\']', html, re.IGNORECASE):
        html = html.replace('</head>', '  <meta property="og:image" content="' + OG_IMAGE + '">\n</head>', 1)

    if re.search(r'<meta\s+property=["\']og:url["\']', html, re.IGNORECASE):
        html = re.sub(r'<meta\s+property=["\']og:url["\']\s+content=["\'](.*?)["\'](\s*/?>)',
                      '<meta property="og:url" content="' + url + '"\\2', html, flags=re.IGNORECASE)
    else:
        html = html.replace('</head>', '  <meta property="og:url" content="' + url + '">\n</head>', 1)

    if not re.search(r'<meta\s+property=["\']og:type["\']', html, re.IGNORECASE):
        html = html.replace('</head>', '  <meta property="og:type" content="article">\n</head>', 1)

    return html


def fix_twitter_tags(html, title, desc):
    if not re.search(r'<meta\s+(?:name|property)=["\']twitter:card["\']', html, re.IGNORECASE):
        snippet = ('  <meta name="twitter:card" content="summary_large_image">\n'
                   '  <meta name="twitter:title" content="' + title + '">\n'
                   '  <meta name="twitter:description" content="' + desc + '">\n'
                   '  <meta name="twitter:image" content="' + OG_IMAGE + '">\n</head>')
        html = html.replace('</head>', snippet, 1)
    return html


def fix_canonical(html, url):
    if not re.search(r'<link\s+rel=["\']canonical["\']', html, re.IGNORECASE):
        html = html.replace('</head>', '  <link rel="canonical" href="' + url + '">\n</head>', 1)
    return html


def fix_robots(html):
    if not re.search(r'<meta\s+name=["\']robots["\']', html, re.IGNORECASE):
        html = html.replace('</head>', '  <meta name="robots" content="index, follow">\n</head>', 1)
    return html


def fix_privacy_links(html):
    pattern = re.compile(r'<a\s+([^>]*href=["\'][^"\']*privacy[^"\']*["\'][^>]*)>', re.IGNORECASE)
    def replace_link(m):
        attrs = m.group(1)
        attrs = re.sub(r'\s*target=["\'][^"\']*["\']', '', attrs)
        attrs = re.sub(r'\s*onclick=["\'][^"\']*["\']', '', attrs)
        return ('<a ' + attrs.strip() + ' target="_blank" rel="noopener noreferrer" '
                "onclick=\"event.stopPropagation();window.open(this.href,'_blank');return false;\">")
    return pattern.sub(replace_link, html)


def fix_popup_css(html):
    if '/popup.css' not in html:
        html = html.replace('</head>', '  <link rel="stylesheet" href="/popup.css">\n</head>', 1)
    return html


def fix_popup_js(html):
    if '/popup.js' not in html:
        html = html.replace('</body>', '  <script src="/popup.js"></script>\n</body>', 1)
    return html


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
        return True
    return False


def main():
    files = get_all_html_files()
    print("Found " + str(len(files)) + " HTML files to process...")

    changed = 0
    skipped = 0
    errors = 0

    for fp in sorted(files):
        try:
            was_changed = process_file(fp)
            rp = rel_path(fp)
            if was_changed:
                print("FIXED  - " + rp)
                changed += 1
            else:
                print("SKIP   - " + rp)
                skipped += 1
        except Exception as e:
            print("ERROR  - " + fp + ": " + str(e))
            errors += 1

    print("Done! " + str(changed) + " fixed, " + str(skipped) + " skipped, " + str(errors) + " errors.")


if __name__ == "__main__":
    main()
