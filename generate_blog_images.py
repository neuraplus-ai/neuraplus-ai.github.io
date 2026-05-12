#!/usr/bin/env python3
"""
NeuraPlusAI Branded Blog Image Generator
==========================================
Generates images EXACTLY matching your brand style:
- Dark navy background (#0a0f1e)
- NeuraPlusAI logo top-left
- Large gradient title text (white → cyan → purple)
- Subtitle text below
- AI visual from Pollinations on right side
- Cyan accent line at bottom
- 1200x630px SEO optimized
"""

import os, re, time, urllib.request, urllib.parse, hashlib, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io

BLOG_DIR    = "blog"
IMAGES_DIR  = "assets/images/blog"
SITE_URL    = "https://neuraplus-ai.github.io"
DELAY       = 3
COMMIT_EVERY = 5

# Brand colors
BG_COLOR       = (8, 13, 35)       # dark navy
TITLE_WHITE    = (255, 255, 255)
TITLE_CYAN     = (0, 210, 255)
TITLE_PURPLE   = (147, 51, 234)
SUBTITLE_COLOR = (180, 190, 210)
ACCENT_COLOR   = (0, 210, 255)
LOGO_BG        = (15, 20, 45)

SKIP = ["index","404","about","contact","privacy","sitemap","terms","search"]


def git(cmd):
    subprocess.run(cmd, shell=True, check=False)


def setup_git():
    git('git config user.name "github-actions[bot]"')
    git('git config user.email "github-actions[bot]@users.noreply.github.com"')


def commit_now(msg="progress"):
    git(f"git add {IMAGES_DIR}/ {BLOG_DIR}/")
    r = subprocess.run("git diff --staged --quiet", shell=True)
    if r.returncode != 0:
        git(f'git commit -m "🖼️ {msg} [skip ci]"')
        git("git fetch origin")
        git("git rebase origin/main || git rebase origin/master")
        git("git push origin HEAD:main || git push origin HEAD:master")
        print(f"   💾 Committed: {msg}")


def get_posts():
    p = Path(BLOG_DIR)
    if not p.exists():
        return []
    return [f for f in sorted(p.glob("*.html"))
            if not any(f.stem.lower().startswith(s) for s in SKIP)]


def image_done(slug):
    for ext in [".jpg",".jpeg",".png",".webp"]:
        p = Path(IMAGES_DIR) / f"{slug}{ext}"
        if p.exists() and p.stat().st_size > 5000:
            return True
    return False


def get_title(html, slug):
    m = re.search(r"<title>([^<]+)</title>", html, re.I)
    if m:
        t = m.group(1)
        t = re.sub(r"\s*[–—|-]\s*(NeuraPlusAI|NeuraPulse).*$","",t,flags=re.I)
        return t.strip()
    return slug.replace("-"," ").title()


def get_subtitle(title):
    """Generate a short SEO subtitle from the title."""
    kw_map = [
        (["claude","anthropic","prompt"],    "AI-Powered Writing & Automation"),
        (["groq","lpu","gpu","chip"],        "Speed. Performance. Intelligence."),
        (["ai","artificial","machine","llm"],"Smarter Tools. Better Results."),
        (["seo","google","rank","search"],   "Rank Higher. Grow Faster."),
        (["automat","workflow","n8n","zapier"],"Automate Everything. Work Smarter."),
        (["python","code","developer","api"],"Build Faster with AI."),
        (["business","startup","growth"],    "Smarter Processes. Stronger Business."),
        (["tutorial","guide","how to"],      "Step-by-Step. Easy to Follow."),
        (["voice","audio","elevenlabs"],     "AI Voice. Human Touch."),
        (["local","ollama","private"],       "Private. Fast. Yours."),
    ]
    t = title.lower()
    for kws, sub in kw_map:
        if any(k in t for k in kws):
            return sub
    return "Powered by AI. Built for You."


def build_visual_prompt(title):
    """Build prompt for the right-side AI visual."""
    t = title.lower()
    topics = [
        (["claude","prompt","gpt","llm","anthropic"],
         "glowing AI brain with text prompts floating, dark blue background, cyberpunk style, no text"),
        (["groq","chip","lpu","hardware","fast"],
         "glowing semiconductor chip with light beams, dark background, blue neon, no text"),
        (["seo","ranking","google","search","traffic"],
         "glowing search bar with upward chart, digital marketing concept, dark blue, no text"),
        (["automat","workflow","n8n","zapier","pipeline"],
         "glowing connected nodes workflow diagram, automation concept, dark blue neon, no text"),
        (["python","code","developer","programming","api"],
         "glowing code on dark screen, programming concept, blue terminal, no text"),
        (["ai","machine learning","neural","deep learning"],
         "glowing neural network brain with circuit connections, dark blue background, no text"),
        (["business","startup","growth","strategy"],
         "businessman touching glowing AI hologram tablet, dark blue, professional, no text"),
        (["voice","audio","speech","podcast"],
         "glowing audio waveform with AI nodes, sound visualization, dark blue, no text"),
        (["cloud","server","deploy","coreweave"],
         "glowing server rack with data streams, cloud computing, dark blue, no text"),
        (["translate","language","deepl"],
         "glowing globe with language symbols floating, translation concept, dark blue, no text"),
    ]
    for kws, prompt in topics:
        if any(k in t for k in kws):
            return prompt
    return "glowing AI holographic display with data visualization, dark blue background, futuristic, no text"


def download_visual(prompt, width=580, height=630):
    """Download AI visual for right side of image."""
    encoded = urllib.parse.quote(prompt)
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8],16) % 99999
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&seed={seed}&nologo=true&model=flux"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"NeuraPlusAI/6.0"})
        with urllib.request.urlopen(req, timeout=90) as r:
            return Image.open(io.BytesIO(r.read())).convert("RGBA")
    except:
        return None


def draw_logo(draw, img, x, y, size=80):
    """Draw NeuraPlusAI N+ logo box."""
    # Logo background box
    box = [(x, y), (x+size, y+size)]
    draw.rounded_rectangle(box, radius=12,
                           fill=(15, 22, 55),
                           outline=(0, 180, 220), width=2)

    # N letter
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((x+16, y+10), "N", font=font_large, fill=(255,255,255))
    draw.text((x+46, y+8), "+", font=font_large, fill=(0,210,255))

    # NEURAPLUS text
    draw.text((x+6, y+56), "NEURAPLUS", font=font_small, fill=(0,210,255))
    draw.text((x+18, y+70), "AI BLOG", font=font_small, fill=(150,160,180))


def wrap_text(text, max_chars_per_line):
    """Simple word wrap."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars_per_line:
            current = current + " " + word if current else word
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_gradient_text(img, draw, text, x, y, font, color1, color2, color3=None):
    """Draw text with horizontal gradient (white → cyan → purple)."""
    # Create text mask
    txt_img = Image.new("RGBA", img.size, (0,0,0,0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((x, y), text, font=font, fill=(255,255,255,255))

    # Get text bbox
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]

    # Create gradient
    grad = Image.new("RGBA", img.size, (0,0,0,0))
    grad_draw = ImageDraw.Draw(grad)

    for i in range(w):
        ratio = i / max(w, 1)
        if ratio < 0.4:
            # white → cyan
            r2 = ratio / 0.4
            c = (
                int(color1[0] + (color2[0]-color1[0]) * r2),
                int(color1[1] + (color2[1]-color1[1]) * r2),
                int(color1[2] + (color2[2]-color1[2]) * r2),
                255
            )
        else:
            # cyan → purple
            r2 = (ratio - 0.4) / 0.6
            c = (
                int(color2[0] + (color3[0]-color2[0]) * r2),
                int(color2[1] + (color3[1]-color2[1]) * r2),
                int(color2[2] + (color3[2]-color2[2]) * r2),
                255
            )
        grad_draw.line([(x+i, y), (x+i, y+80)], fill=c)

    # Composite
    result = Image.new("RGBA", img.size, (0,0,0,0))
    result.paste(grad, mask=txt_img.split()[3])
    img.alpha_composite(result)


def generate_branded_image(title, subtitle, slug):
    """Generate a branded 1200x630 image matching NeuraPlusAI style."""
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img)

    # ── Dark gradient overlay left side ──────────────────────────────────────
    for i in range(W//2 + 100):
        alpha = max(0, 255 - int(i * 0.4))
        draw.line([(i,0),(i,H)], fill=(*BG_COLOR, alpha))

    # ── Download & place AI visual (right side) ───────────────────────────────
    visual_prompt = build_visual_prompt(title)
    visual = download_visual(visual_prompt, 580, 630)
    if visual:
        # Darken edges of visual for blending
        visual_rgb = visual.convert("RGBA")
        # Blend left edge of visual
        blend = Image.new("RGBA", visual_rgb.size, (0,0,0,0))
        bd = ImageDraw.Draw(blend)
        for i in range(200):
            alpha = int(255 * (1 - i/200))
            bd.line([(i,0),(i,H)], fill=(0,0,0,alpha))
        visual_rgb.alpha_composite(blend)
        img.paste(visual_rgb.convert("RGB"), (620, 0), visual_rgb.split()[3])

    # ── Re-draw dark left overlay after visual ────────────────────────────────
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    for i in range(700):
        alpha = max(0, int(220 * (1 - i/700)))
        od.line([(i,0),(i,H)], fill=(*BG_COLOR, alpha))
    img.alpha_composite(overlay)

    draw = ImageDraw.Draw(img)

    # ── Load fonts ────────────────────────────────────────────────────────────
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/"
        f_title_huge  = ImageFont.truetype(font_path+"DejaVuSans-Bold.ttf", 72)
        f_title_large = ImageFont.truetype(font_path+"DejaVuSans-Bold.ttf", 58)
        f_title_med   = ImageFont.truetype(font_path+"DejaVuSans-Bold.ttf", 48)
        f_subtitle    = ImageFont.truetype(font_path+"DejaVuSans.ttf", 26)
        f_logo        = ImageFont.truetype(font_path+"DejaVuSans-Bold.ttf", 36)
    except:
        f_title_huge = f_title_large = f_title_med = ImageFont.load_default()
        f_subtitle = ImageFont.load_default()

    # ── Logo top-left ─────────────────────────────────────────────────────────
    draw_logo(draw, img, 40, 30, size=90)

    # ── Title text ────────────────────────────────────────────────────────────
    # Choose font size based on title length
    max_w = 580
    if len(title) <= 25:
        font = f_title_huge
        max_chars = 14
    elif len(title) <= 40:
        font = f_title_large
        max_chars = 18
    else:
        font = f_title_med
        max_chars = 22

    lines = wrap_text(title, max_chars)

    # Start title below logo
    ty = 160
    for i, line in enumerate(lines[:4]):
        # First line white, rest gradient
        if i == 0:
            draw.text((40, ty), line, font=font, fill=TITLE_WHITE)
        elif i == 1:
            draw.text((40, ty), line, font=font, fill=TITLE_CYAN)
        else:
            draw.text((40, ty), line, font=font, fill=TITLE_PURPLE)
        ty += font.size + 8

    # ── Subtitle ──────────────────────────────────────────────────────────────
    ty += 20
    draw.text((40, ty), subtitle, font=f_subtitle, fill=SUBTITLE_COLOR)

    # ── Accent line ───────────────────────────────────────────────────────────
    line_y = ty + 50
    draw.rectangle([(40, line_y), (200, line_y+3)], fill=ACCENT_COLOR)

    # ── Convert and save ──────────────────────────────────────────────────────
    final = img.convert("RGB")
    save_path = Path(IMAGES_DIR) / f"{slug}.jpg"
    Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    final.save(save_path, "JPEG", quality=92, optimize=True)
    size_kb = save_path.stat().st_size // 1024
    print(f"   ✅ {size_kb}KB → {save_path}")
    return True


def inject(filepath, slug, title):
    img_web = f"/{IMAGES_DIR}/{slug}.jpg"
    img_abs = f"{SITE_URL}{img_web}"
    html = filepath.read_text(encoding="utf-8", errors="ignore")

    if "meta-og:image" in html:
        html = re.sub(r"(meta-og:image:\s*).*", f"\\1{img_abs}", html)
    if "meta-twitter:image" in html:
        html = re.sub(r"(meta-twitter:image:\s*).*", f"\\1{img_abs}", html)

    if img_web not in html:
        hero = (
            f'\n<img src="{img_web}" alt="{title}" title="{title}" '
            f'class="blog-hero-image" width="1200" height="630" loading="lazy" '
            f'style="width:100%;max-width:1200px;height:auto;'
            f'border-radius:8px;margin:0 auto 2rem;display:block;" />\n'
        )
        h1 = re.search(r"(<h1[^>]*>.*?</h1>)", html, re.I|re.S)
        if h1:
            html = html[:h1.end()] + hero + html[h1.end():]
        else:
            art = re.search(r"(<(?:article|main|body)[^>]*>)", html, re.I)
            if art:
                html = html[:art.end()] + hero + html[art.end():]

    filepath.write_text(html, encoding="utf-8")


def main():
    setup_git()
    posts = get_posts()
    if not posts:
        print("❌ No posts found in blog/ folder")
        return

    run_mode = os.environ.get("RUN_MODE", "remaining")
    todo = [p for p in posts if not image_done(p.stem)] if run_mode == "remaining" else posts

    print(f"📊 Total  : {len(posts)} posts")
    print(f"✅ Done   : {len(posts)-len(todo)} already have images")
    print(f"⏳ To do  : {len(todo)} remaining")
    print(f"🎨 Style  : NeuraPlusAI branded (dark + logo + gradient title)\n")

    if not todo:
        print("🎉 All posts already have images!")
        return

    ok = fail = 0

    for i, filepath in enumerate(todo, 1):
        slug = filepath.stem
        html = filepath.read_text(encoding="utf-8", errors="ignore")

        # Get title
        m = re.search(r"<title>([^<]+)</title>", html, re.I)
        title = m.group(1) if m else slug.replace("-"," ").title()
        title = re.sub(r"\s*[–—|-]\s*(NeuraPlusAI|NeuraPulse).*$","",title,flags=re.I).strip()
        subtitle = get_subtitle(title)

        print(f"[{i}/{len(todo)}] {slug}")
        print(f"   📝 {title}")
        print(f"   💬 {subtitle}")

        try:
            success = generate_branded_image(title, subtitle, slug)
            if success:
                inject(filepath, slug, title)
                ok += 1
                if ok % COMMIT_EVERY == 0:
                    commit_now(f"saved {ok} branded images")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            fail += 1

        time.sleep(DELAY)

    commit_now(f"complete — {ok} branded images generated")

    print(f"\n{'='*50}")
    print(f"✅ Generated : {ok} branded images")
    print(f"❌ Failed    : {fail}")
    print("="*50)


if __name__ == "__main__":
    main()
