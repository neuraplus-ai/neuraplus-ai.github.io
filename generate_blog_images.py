#!/usr/bin/env python3
"""
Auto Blog Image Generator
=========================
- Scans ALL markdown posts (_posts/ folder)
- Generates SEO-optimized images via Pollinations.ai (FREE, no API key)
- Skips posts that already have images
- Injects: Hero image (top of post) + OG/meta image in frontmatter
- Works for Jekyll, Hugo, and plain Markdown GitHub blogs
"""

import os
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
import hashlib

# ── Config ─────────────────────────────────────────────────────────────────
POSTS_DIR = "_posts"          # where your .md blog posts live
IMAGES_DIR = "assets/images/blog"  # where generated images will be saved
IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 630            # standard OG image size (rankable / shareable)
DELAY_BETWEEN = 3             # seconds between API calls (be nice to free API)
# ───────────────────────────────────────────────────────────────────────────


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown file."""
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_raw = parts[1].strip()
            body = parts[2].strip()
            for line in fm_raw.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body


def rebuild_frontmatter(meta: dict, body: str) -> str:
    """Rebuild markdown file with updated frontmatter."""
    lines = []
    for k, v in meta.items():
        # Quote values that contain colons or special chars
        if any(c in str(v) for c in [":", "#", "[", "]", "{", "}"]):
            lines.append(f'{k}: "{v}"')
        else:
            lines.append(f"{k}: {v}")
    fm = "\n".join(lines)
    return f"---\n{fm}\n---\n\n{body}"


def get_post_title(meta: dict, filename: str) -> str:
    """Get title from frontmatter or derive from filename."""
    if "title" in meta:
        return meta["title"]
    # derive from filename: 2024-01-15-my-great-post.md → My Great Post
    name = Path(filename).stem
    name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)  # strip date prefix
    return name.replace("-", " ").replace("_", " ").title()


def get_post_tags(meta: dict) -> str:
    """Extract tags/categories for image context."""
    for key in ["tags", "categories", "category", "keywords"]:
        if key in meta:
            val = meta[key]
            # Handle list format: [tag1, tag2]
            val = val.strip("[]").replace(",", " ").strip()
            if val:
                return val[:60]
    return ""


def build_image_prompt(title: str, tags: str, body_snippet: str) -> str:
    """Build a rich SEO-friendly image generation prompt."""
    # Extract key topic from body
    topic_hint = ""
    if body_snippet:
        # grab first meaningful sentence
        sentences = re.split(r"[.!?]", body_snippet[:300])
        for s in sentences:
            s = s.strip()
            s = re.sub(r"[#*`\[\]()]", "", s)
            if len(s) > 20:
                topic_hint = s[:80]
                break

    prompt_parts = [
        f"professional blog header image for article titled: {title}",
        f"topic: {topic_hint}" if topic_hint else "",
        f"keywords: {tags}" if tags else "",
        "style: modern clean editorial photography or illustration",
        "wide banner 1200x630 landscape",
        "vibrant colors high quality sharp",
        "no text no watermark no logo",
    ]
    prompt = ", ".join(p for p in prompt_parts if p)
    return prompt[:500]  # API limit


def image_already_exists(meta: dict, img_path: str) -> bool:
    """Check if post already has an image assigned."""
    has_meta = any(k in meta for k in ["image", "featured_image", "og_image", "cover"])
    file_exists = Path(img_path).exists()
    return has_meta and file_exists


def download_image(prompt: str, save_path: str) -> bool:
    """Download image from Pollinations.ai (100% free, no API key)."""
    encoded = urllib.parse.quote(prompt)
    # Use seed based on prompt for reproducibility
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 99999
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&seed={seed}&nologo=true"
    )
    print(f"   🎨 Generating: {url[:80]}...")
    try:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        headers = {"User-Agent": "BlogImageBot/1.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        if len(data) < 5000:
            print(f"   ⚠️  Image too small ({len(data)} bytes), skipping")
            return False
        with open(save_path, "wb") as f:
            f.write(data)
        print(f"   ✅ Saved ({len(data)//1024}KB) → {save_path}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def inject_image_into_post(filepath: str, img_web_path: str, title: str) -> bool:
    """
    Inject image into post:
    1. Add to frontmatter (image / og:image / featured_image)
    2. Add as first visible element in post body (hero image)
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    meta, body = extract_frontmatter(content)

    # ── 1. Update frontmatter ──────────────────────────────────────────────
    meta["image"] = img_web_path          # Jekyll/Hugo featured image
    meta["featured_image"] = img_web_path  # some themes use this
    meta["og_image"] = img_web_path        # Open Graph (Facebook/Twitter)
    meta["twitter_image"] = img_web_path   # Twitter card
    meta["image_alt"] = title              # SEO alt text

    # ── 2. Inject hero image at TOP of body (if not already there) ─────────
    hero_tag = f'![{title}]({img_web_path}){{: .blog-hero-image}}'
    hero_html = (
        f'\n<img src="{img_web_path}" alt="{title}" '
        f'class="blog-hero-image seo-image" '
        f'style="width:100%;max-width:1200px;height:auto;margin:0 auto 2rem;display:block;" />\n'
    )

    # Check if image already injected in body
    if img_web_path not in body:
        # Insert after any existing H1 heading, otherwise at very top
        h1_match = re.match(r"(#\s+.+\n)", body)
        if h1_match:
            insert_at = h1_match.end()
            body = body[:insert_at] + "\n" + hero_html + body[insert_at:]
        else:
            body = hero_html + "\n" + body

    new_content = rebuild_frontmatter(meta, body)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def process_posts(posts_dir: str, images_dir: str, retroactive: bool = True):
    """Main: scan and process all posts."""
    posts_path = Path(posts_dir)
    if not posts_path.exists():
        # Try common alternatives
        for alt in ["content/posts", "src/posts", "blog", "content"]:
            if Path(alt).exists():
                posts_path = Path(alt)
                print(f"📁 Found posts in: {alt}")
                break
        else:
            print(f"❌ Posts directory not found. Tried: {posts_dir}, content/posts, blog")
            sys.exit(1)

    md_files = sorted(posts_path.rglob("*.md")) + sorted(posts_path.rglob("*.mdx"))

    if not md_files:
        print("⚠️  No markdown files found.")
        return

    print(f"\n🔍 Found {len(md_files)} post(s) in {posts_path}\n")

    processed = 0
    skipped = 0
    failed = 0

    for filepath in md_files:
        print(f"📄 {filepath.name}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        meta, body = extract_frontmatter(content)
        title = get_post_title(meta, filepath.name)
        tags = get_post_tags(meta)

        # Derive image filename from post filename
        img_filename = filepath.stem + ".jpg"
        img_local_path = str(Path(images_dir) / img_filename)
        img_web_path = f"/{images_dir}/{img_filename}"

        # ── Skip if already has image ──────────────────────────────────────
        if image_already_exists(meta, img_local_path):
            print(f"   ⏭️  Already has image, skipping\n")
            skipped += 1
            continue

        # ── Skip new-only mode ────────────────────────────────────────────
        # In GitHub Actions: RETROACTIVE env var controls this
        is_new_file = os.environ.get("NEW_FILE", "") == filepath.name
        run_mode = os.environ.get("RUN_MODE", "all")  # "all" or "new_only"

        if run_mode == "new_only" and not is_new_file and not retroactive:
            print(f"   ⏭️  Skipping (new_only mode)\n")
            skipped += 1
            continue

        # ── Generate image ─────────────────────────────────────────────────
        prompt = build_image_prompt(title, tags, body)
        print(f"   📝 Title: {title}")
        print(f"   🏷️  Tags:  {tags or '(none)'}")

        success = download_image(prompt, img_local_path)

        if success:
            inject_image_into_post(str(filepath), img_web_path, title)
            print(f"   🖼️  Injected into post\n")
            processed += 1
        else:
            failed += 1
            print()

        time.sleep(DELAY_BETWEEN)

    print("=" * 50)
    print(f"✅ Processed : {processed}")
    print(f"⏭️  Skipped   : {skipped} (already had images)")
    print(f"❌ Failed    : {failed}")
    print("=" * 50)


if __name__ == "__main__":
    # Check if we should only process new posts or ALL (retroactive)
    run_mode = os.environ.get("RUN_MODE", "all")
    retroactive = run_mode != "new_only"

    print("🚀 Blog Auto Image Generator")
    print(f"   Mode: {'ALL posts (retroactive)' if retroactive else 'NEW posts only'}")
    print(f"   Posts dir  : {POSTS_DIR}")
    print(f"   Images dir : {IMAGES_DIR}")
    print()

    process_posts(POSTS_DIR, IMAGES_DIR, retroactive)
