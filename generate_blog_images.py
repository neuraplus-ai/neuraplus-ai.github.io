#!/usr/bin/env python3
"""
Blog Image Generator v3
========================
Fixed for neuraplus-ai.github.io repo structure:
- Posts are in /blog/ folder (not _posts/)
- Files are .html not .md in some cases
- Skips README, index, about, contact pages
"""

import os
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
import hashlib

# ── Config ───────────────────────────────────────────────────────────────────
# Searches ALL these folders — whichever exists in your repo
POSSIBLE_POST_DIRS = ["_posts", "blog", "content/posts", "posts"]
IMAGES_DIR   = "assets/images/blog"
IMAGE_WIDTH  = 1200
IMAGE_HEIGHT = 630
DELAY_BETWEEN = 4
# ─────────────────────────────────────────────────────────────────────────────

# Files to always skip
SKIP_NAMES = [
    "readme", "index", "about", "contact", "404",
    "home", "privacy", "terms", "sitemap", "feed"
]


def find_posts_dir() -> Path:
    """Auto-detect which folder contains blog posts."""
    for d in POSSIBLE_POST_DIRS:
        p = Path(d)
        if p.exists() and p.is_dir():
            print(f"📁 Found posts directory: {d}/")
            return p
    print("❌ Could not find posts folder. Tried:", POSSIBLE_POST_DIRS)
    sys.exit(1)


def is_valid_post(filepath: Path) -> bool:
    name = filepath.stem.lower()
    if any(name.startswith(s) for s in SKIP_NAMES):
        return False
    return True


def extract_meta_from_html(content: str) -> dict:
    """Extract title, description, og:image from HTML files."""
    meta = {}
    title_match = re.search(r"<title>([^<]+)</title>", content, re.I)
    if title_match:
        meta["title"] = title_match.group(1).split("–")[0].split("|")[0].strip()

    og_image = re.search(r'meta-og:image:\s*(.+)', content)
    if og_image:
        meta["og_image"] = og_image.group(1).strip()

    return meta


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown."""
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            body = parts[2].strip()
    return meta, body


def rebuild_frontmatter(meta: dict, body: str) -> str:
    lines = []
    for k, v in meta.items():
        if any(c in str(v) for c in [":", "#", "[", "]", "{", "}"]):
            lines.append(f'{k}: "{v}"')
        else:
            lines.append(f"{k}: {v}")
    return "---\n" + "\n".join(lines) + "\n---\n\n" + body


def get_title(meta: dict, filepath: Path) -> str:
    if "title" in meta:
        t = meta["title"]
        # Clean up common suffixes
        t = re.sub(r"\s*[–—-]\s*(NeuraPlusAI|NeuraPlus|NeuraPulse).*$", "", t, flags=re.I)
        return t.strip()
    name = filepath.stem
    name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
    return name.replace("-", " ").replace("_", " ").title()


def build_prompt(title: str, tags: str, snippet: str) -> str:
    text = (title + " " + tags + " " + snippet).lower()

    style_map = [
        (["python", "javascript", "typescript", "code", "programming",
          "developer", "software", "api", "function", "prompt", "claude", "gpt"],
         "professional developer workspace, laptop with code on screen, dark IDE, programming concept, tech aesthetic"),

        (["ai", "artificial intelligence", "machine learning", "neural",
          "deep learning", "llm", "anthropic", "openai", "groq"],
         "abstract AI neural network concept, glowing data streams, futuristic technology, blue purple gradient"),

        (["seo", "google", "search engine", "ranking", "keyword",
          "traffic", "blog", "content marketing"],
         "digital marketing dashboard with analytics charts, SEO concept, search ranking visualization"),

        (["automation", "workflow", "github", "actions", "devops",
          "pipeline", "ci cd", "deploy"],
         "automated workflow diagram, connected gears and processes, DevOps concept, modern tech illustration"),

        (["startup", "business", "entrepreneur", "marketing",
          "growth", "strategy", "saas"],
         "modern startup office concept, growth chart, professional business environment"),

        (["tutorial", "guide", "learn", "how to", "beginner", "course", "step by step"],
         "clean educational concept, learning path visualization, open laptop with tutorial content"),

        (["security", "cybersecurity", "privacy", "vpn", "encrypt", "hack"],
         "cybersecurity shield and lock concept, digital protection, secure network visualization"),

        (["finance", "money", "invest", "crypto", "bitcoin", "budget"],
         "financial technology concept, charts and graphs, modern fintech visualization"),
    ]

    visual = "professional blog header, modern editorial photography, clean design"
    for keywords, style in style_map:
        if any(kw in text for kw in keywords):
            visual = style
            break

    prompt = (
        f"{visual}, "
        f"topic: {title[:80]}, "
        f"wide 1200x630 banner format, "
        f"high quality sharp professional image, "
        f"vibrant colors, "
        f"absolutely no text, no watermark, no logo, no people holding papers or documents"
    )
    return prompt[:500]


def image_exists(meta: dict, img_path: str) -> bool:
    file_ok = Path(img_path).exists() and Path(img_path).stat().st_size > 5000
    # For HTML files, check og_image in meta
    meta_ok = any(k in meta for k in ["image", "featured_image", "og_image"])
    return file_ok and meta_ok


def download_image(prompt: str, save_path: str) -> bool:
    encoded = urllib.parse.quote(prompt)
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 99999
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}"
        f"&seed={seed}&nologo=true&enhance=true&model=flux"
    )
    print(f"   🎨 Prompt : {prompt[:90]}...")
    try:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "NeuraPlusAI-ImageBot/3.0"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = resp.read()
        if len(data) < 8000:
            print(f"   ⚠️  Image too small ({len(data)}B) — API may have failed")
            return False
        with open(save_path, "wb") as f:
            f.write(data)
        print(f"   ✅ Saved {len(data)//1024}KB → {save_path}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def inject_into_md(filepath: str, img_web: str, title: str):
    """Inject image into markdown post frontmatter + body."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    meta, body = extract_frontmatter(content)
    meta["image"]          = img_web
    meta["featured_image"] = img_web
    meta["og_image"]       = img_web
    meta["twitter_image"]  = img_web
    meta["image_alt"]      = title

    hero = (
        f'\n<img src="{img_web}" alt="{title}" '
        f'class="blog-hero-image" '
        f'style="width:100%;max-width:1200px;height:auto;'
        f'border-radius:8px;margin:0 auto 2rem;display:block;" />\n'
    )
    if img_web not in body:
        h1 = re.match(r"(#\s+.+\n)", body)
        body = body[:h1.end()] + hero + body[h1.end():] if h1 else hero + body

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(rebuild_frontmatter(meta, body))


def inject_into_html(filepath: str, img_web: str, title: str):
    """Inject og:image into HTML post meta tags."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    abs_url = f"https://neuraplus-ai.github.io{img_web}"

    # Update existing og:image meta tag
    if 'meta-og:image' in content:
        content = re.sub(
            r'(meta-og:image:\s*).*',
            f'meta-og:image: {abs_url}',
            content
        )
    if 'meta-twitter:image' in content:
        content = re.sub(
            r'(meta-twitter:image:\s*).*',
            f'meta-twitter:image: {abs_url}',
            content
        )

    # Also inject hero image after <h1> if not present
    if img_web not in content:
        hero = (
            f'\n<img src="{img_web}" alt="{title}" '
            f'class="blog-hero-image" '
            f'style="width:100%;max-width:1200px;height:auto;'
            f'border-radius:8px;margin:0 auto 2rem;display:block;" />\n'
        )
        h1_match = re.search(r'(<h1[^>]*>.*?</h1>)', content, re.I | re.S)
        if h1_match:
            insert_at = h1_match.end()
            content = content[:insert_at] + hero + content[insert_at:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def run():
    posts_path = find_posts_dir()
    run_mode = os.environ.get("RUN_MODE", "all")
    new_file  = os.environ.get("NEW_FILE", "")

    # Collect all post files (md, mdx, html)
    all_files = []
    for ext in ["*.md", "*.mdx", "*.html"]:
        all_files.extend(posts_path.rglob(ext))

    valid = [f for f in all_files if is_valid_post(f)]

    if not valid:
        print(f"⚠️  No blog posts found in {posts_path}/")
        print(f"    Files found: {[f.name for f in all_files[:10]]}")
        return

    print(f"🔍 {len(all_files)} files found → {len(valid)} valid posts")
    print(f"🎯 Mode: {run_mode}\n")

    ok = skip = fail = 0

    for filepath in sorted(valid):
        print(f"📄 {filepath.name}")

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        is_html = filepath.suffix == ".html"

        if is_html:
            meta = extract_meta_from_html(content)
            body_snippet = re.sub(r"<[^>]+>", " ", content)[:600]
        else:
            meta, body = extract_frontmatter(content)
            body_snippet = body[:600]

        title = get_title(meta, filepath)
        tags  = meta.get("tags", meta.get("categories", meta.get("keywords", "")))

        img_file  = filepath.stem + ".jpg"
        img_local = str(Path(IMAGES_DIR) / img_file)
        img_web   = f"/{IMAGES_DIR}/{img_file}"

        if image_exists(meta, img_local):
            print(f"   ⏭️  Has image already, skipping\n")
            skip += 1
            continue

        if run_mode == "new_only" and new_file and filepath.name not in new_file:
            print(f"   ⏭️  Not the new post\n")
            skip += 1
            continue

        print(f"   📝 Title: {title}")

        prompt  = build_prompt(title, str(tags), body_snippet)
        success = download_image(prompt, img_local)

        if success:
            if is_html:
                inject_into_html(str(filepath), img_web, title)
            else:
                inject_into_md(str(filepath), img_web, title)
            print(f"   🖼️  Injected into post\n")
            ok += 1
        else:
            fail += 1
            print()

        time.sleep(DELAY_BETWEEN)

    print("=" * 50)
    print(f"✅ Generated : {ok}")
    print(f"⏭️  Skipped   : {skip}")
    print(f"❌ Failed    : {fail}")
    print("=" * 50)


if __name__ == "__main__":
    print("🚀 NeuraPlusAI Blog Image Generator v3")
    print()
    run()
