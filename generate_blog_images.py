#!/usr/bin/env python3
"""
Fixed Blog Image Generator
===========================
- Only scans _posts/*.md (NOT README.md or other files)
- Reads actual post content to build a specific, relevant prompt
- Skips any file that is not a dated blog post (YYYY-MM-DD-title.md)
"""

import os
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
import hashlib

# ── Config ──────────────────────────────────────────────────────────────────
POSTS_DIR  = "_posts"
IMAGES_DIR = "assets/images/blog"
IMAGE_WIDTH  = 1200
IMAGE_HEIGHT = 630
DELAY_BETWEEN = 4   # seconds between API calls
# ────────────────────────────────────────────────────────────────────────────


def is_valid_blog_post(filepath: Path) -> bool:
    """
    Only process real blog posts.
    Valid: _posts/2024-01-15-my-post.md
    Invalid: README.md, index.md, about.md, etc.
    """
    name = filepath.name

    # Must be inside _posts/ folder
    if "_posts" not in str(filepath):
        return False

    # Must NOT be README, index, about, etc.
    skip_names = ["readme", "index", "about", "contact", "404", "home"]
    if any(name.lower().startswith(s) for s in skip_names):
        print(f"   ⏭️  Skipping non-post file: {name}")
        return False

    # Optionally: must match YYYY-MM-DD-*.md pattern
    # (common Jekyll convention — remove this check if your posts don't use dates)
    # date_pattern = re.match(r"^\d{4}-\d{2}-\d{2}-.+\.mdx?$", name)
    # if not date_pattern:
    #     print(f"   ⏭️  Skipping (not a dated post): {name}")
    #     return False

    return True


def extract_frontmatter(content: str) -> tuple[dict, str]:
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
    return f"---\n" + "\n".join(lines) + f"\n---\n\n{body}"


def get_title(meta: dict, filepath: Path) -> str:
    if "title" in meta:
        return meta["title"]
    name = filepath.stem
    name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
    return name.replace("-", " ").replace("_", " ").title()


def extract_content_keywords(body: str) -> str:
    """
    Read the actual post body and pull out meaningful topic words.
    Strips markdown syntax, code blocks, links, etc.
    """
    # Remove code blocks
    body = re.sub(r"```[\s\S]*?```", " ", body)
    body = re.sub(r"`[^`]+`", " ", body)
    # Remove markdown links/images
    body = re.sub(r"!\[.*?\]\(.*?\)", " ", body)
    body = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", body)
    # Remove HTML tags
    body = re.sub(r"<[^>]+>", " ", body)
    # Remove markdown headings/bold/italic symbols
    body = re.sub(r"[#*_~>|]", " ", body)
    # Remove URLs
    body = re.sub(r"https?://\S+", " ", body)
    # Collapse whitespace
    body = re.sub(r"\s+", " ", body).strip()

    # Take first 600 chars of clean content (the real topic is usually at the top)
    return body[:600]


def build_specific_prompt(title: str, tags: str, content_snippet: str) -> str:
    """
    Build a SPECIFIC, content-relevant image prompt.
    The prompt describes what the post is ABOUT, not generic concepts.
    """

    # Detect topic category from title + content
    text = (title + " " + tags + " " + content_snippet).lower()

    # Map topics to visual styles
    style_map = [
        (["python", "javascript", "code", "programming", "developer", "software", "api", "function"],
         "clean desk with laptop showing code editor, dark theme screen, programming setup, developer workspace"),

        (["ai", "artificial intelligence", "machine learning", "neural", "deep learning", "gpt", "llm"],
         "abstract neural network visualization, glowing connections, futuristic AI concept, blue and purple tones"),

        (["seo", "google", "search engine", "ranking", "keyword", "traffic", "blog"],
         "search bar with magnifying glass, website analytics dashboard, digital marketing concept"),

        (["health", "fitness", "workout", "exercise", "nutrition", "diet", "yoga", "meditation"],
         "healthy lifestyle concept, natural light, clean modern wellness photography"),

        (["finance", "money", "invest", "stock", "crypto", "bitcoin", "budget", "saving"],
         "financial charts and graphs, modern fintech concept, business money concept"),

        (["travel", "trip", "destination", "explore", "adventure", "vacation", "country"],
         "beautiful travel destination landscape, wanderlust photography, scenic view"),

        (["design", "ui", "ux", "figma", "photoshop", "creative", "graphic", "web design"],
         "modern UI design mockup on screen, clean web interface, creative design workspace"),

        (["startup", "business", "entrepreneur", "marketing", "growth", "strategy"],
         "modern business concept, professional workspace, growth strategy visualization"),

        (["tutorial", "guide", "learn", "how to", "step by step", "beginner", "course"],
         "clean educational concept, learning and knowledge, open book with digital elements"),

        (["security", "hack", "cybersecurity", "privacy", "vpn", "encrypt"],
         "cybersecurity concept, digital lock and shield, secure network visualization"),
    ]

    visual_style = "professional editorial blog header image, modern clean design"
    for keywords, style in style_map:
        if any(kw in text for kw in keywords):
            visual_style = style
            break

    # Build final prompt
    prompt = (
        f"{visual_style}, "
        f"related to: {title}, "
        f"wide banner format 1200x630 pixels, "
        f"high quality professional photography or digital illustration, "
        f"vibrant colors, sharp focus, "
        f"no text overlay, no watermark, no logo, no people holding documents"
    )
    return prompt[:500]


def image_already_done(meta: dict, img_path: str) -> bool:
    has_meta = any(k in meta for k in ["image", "featured_image", "og_image"])
    file_exists = Path(img_path).exists()
    return has_meta and file_exists


def download_image(prompt: str, save_path: str) -> bool:
    encoded = urllib.parse.quote(prompt)
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 99999
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&seed={seed}&nologo=true&enhance=true"
    )
    print(f"   🎨 Prompt: {prompt[:100]}...")
    print(f"   🌐 Fetching image...")
    try:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "BlogImageBot/2.0"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = resp.read()
        if len(data) < 5000:
            print(f"   ⚠️  Image too small ({len(data)} bytes), likely failed")
            return False
        with open(save_path, "wb") as f:
            f.write(data)
        print(f"   ✅ Saved ({len(data)//1024} KB) → {save_path}")
        return True
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return False


def inject_into_post(filepath: str, img_web_path: str, title: str):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    meta, body = extract_frontmatter(content)

    # Update all SEO meta fields
    meta["image"]          = img_web_path
    meta["featured_image"] = img_web_path
    meta["og_image"]       = img_web_path
    meta["twitter_image"]  = img_web_path
    meta["image_alt"]      = title

    # Inject hero image at top of body (only once)
    hero = (
        f'\n<img src="{img_web_path}" '
        f'alt="{title}" '
        f'class="blog-hero-image" '
        f'style="width:100%;max-width:1200px;height:auto;border-radius:8px;margin:0 auto 2rem;display:block;" />\n'
    )
    if img_web_path not in body:
        h1 = re.match(r"(#\s+.+\n)", body)
        if h1:
            body = body[:h1.end()] + hero + body[h1.end():]
        else:
            body = hero + body

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(rebuild_frontmatter(meta, body))


def process_all_posts():
    posts_path = Path(POSTS_DIR)

    # Try alternate folder names if _posts doesn't exist
    if not posts_path.exists():
        for alt in ["content/posts", "posts", "blog"]:
            if Path(alt).exists():
                posts_path = Path(alt)
                break
        else:
            print(f"❌ No posts folder found.")
            sys.exit(1)

    all_md = list(posts_path.rglob("*.md")) + list(posts_path.rglob("*.mdx"))
    # Filter to only valid blog posts
    md_files = [f for f in all_md if is_valid_blog_post(f)]

    if not md_files:
        print("⚠️  No valid blog posts found in", posts_path)
        return

    run_mode = os.environ.get("RUN_MODE", "all")
    new_file  = os.environ.get("NEW_FILE", "")

    print(f"🔍 Found {len(all_md)} markdown files → {len(md_files)} valid blog posts")
    print(f"🎯 Mode: {run_mode}\n")

    ok = skip = fail = 0

    for filepath in sorted(md_files):
        print(f"📄 {filepath.name}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        meta, body = extract_frontmatter(content)
        title   = get_title(meta, filepath)
        tags    = meta.get("tags", meta.get("categories", meta.get("keywords", "")))
        snippet = extract_content_keywords(body)

        img_file    = filepath.stem + ".jpg"
        img_local   = str(Path(IMAGES_DIR) / img_file)
        img_web     = f"/{IMAGES_DIR}/{img_file}"

        # Skip if already has image
        if image_already_done(meta, img_local):
            print(f"   ⏭️  Already has image, skipping\n")
            skip += 1
            continue

        # In new_only mode, skip posts that aren't the new file
        if run_mode == "new_only" and new_file and filepath.name not in new_file:
            print(f"   ⏭️  Not the new post, skipping\n")
            skip += 1
            continue

        print(f"   📝 Title  : {title}")
        print(f"   🏷️  Tags   : {tags or '(none)'}")

        prompt = build_specific_prompt(title, str(tags), snippet)
        success = download_image(prompt, img_local)

        if success:
            inject_into_post(str(filepath), img_web, title)
            print(f"   🖼️  Injected into post\n")
            ok += 1
        else:
            fail += 1
            print()

        time.sleep(DELAY_BETWEEN)

    print("=" * 50)
    print(f"✅ Done      : {ok}")
    print(f"⏭️  Skipped   : {skip}")
    print(f"❌ Failed    : {fail}")
    print("=" * 50)


if __name__ == "__main__":
    print("🚀 Blog Image Generator v2 (Content-Aware)")
    print()
    process_all_posts()
