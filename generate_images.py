#!/usr/bin/env python3
"""
NeuraPulse Blog Image Generator
================================
USAGE:
  python3 generate_images.py           → only missing images
  python3 generate_images.py replace   → regenerate all
  
PLACE IN REPO ROOT. FILES NEEDED:
  logo.png  (or logo.jpg) — your N+ logo
  blog/     — HTML blog posts
  logos/    — optional brand logos (claude_256.png etc)
"""

import os, re, sys, math, hashlib, random, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

# ─── CONFIG ──────────────────────────────────────────────────────────────────
BLOG_DIR     = "blog"
OUT_DIR      = "assets/images/blog"
SITE_URL     = "https://neuraplus-ai.github.io"
LOGOS_DIR    = "logos"
COMMIT_EVERY = 5
W, H         = 1200, 630
WEBP_Q       = 85

SKIP = ["index","404","about","contact","privacy","sitemap",
        "terms","search","tag","category","archive","author"]

# ─── BRAND COLORS ────────────────────────────────────────────────────────────
BG1    = (4,   7,  22)
BG2    = (8,  12,  36)
CYAN   = (0,  220, 255)
PURPLE = (130, 40, 230)
AMBER  = (255, 165, 20)
GREEN  = (40,  220, 140)
WHITE  = (255, 255, 255)
LGRAY  = (180, 200, 220)
DGRAY  = (70,  90, 115)

# ─── TOPIC INTELLIGENCE ──────────────────────────────────────────────────────
TOPIC_MAP = [
    (["claude","anthropic"],
     "Anthropic's Most Capable AI",    "AI Model",    AMBER,
     (210,120,40),(255,175,70),         "claude_256"),
    (["chatgpt","gpt-4","gpt-3"],
     "OpenAI's Revolutionary Platform", "AI Model",    GREEN,
     (16,163,127),(50,210,150),         "chatgpt_256"),
    (["openai"],
     "OpenAI — Leading AI Research",   "AI Research", (180,180,180),
     (20,20,20),(200,200,200),          "openai_256"),
    (["gemini","google ai","bard"],
     "Google's Next-Gen AI Model",     "AI Model",    (80,150,255),
     (30,110,230),(100,175,255),        "gemini_256"),
    (["perplexity"],
     "The AI-First Answer Engine",     "AI Search",   CYAN,
     (10,15,50),(0,210,255),           "perplexity_256"),
    (["groq"],
     "World's Fastest AI Inference",   "AI Speed",    PURPLE,
     (110,35,170),(195,120,255),        "groq_256"),
    (["kimi","moonshot"],
     "China's Most Powerful LLM",      "LLM Review",  CYAN,
     (0,100,160),(0,185,225),          "kimi_256"),
    (["deepseek"],
     "Open-Source AI Rivals the Best", "Open Source", (0,120,255),
     (8,10,40),(0,120,255),            "deepseek_256"),
    (["mistral"],
     "Europe's Best Open-Source AI",   "AI Model",    AMBER,
     (190,75,0),(255,125,35),          "mistral_256"),
    (["llama","meta ai"],
     "Meta's Open AI Powerhouse",      "AI Model",    (80,120,255),
     (20,115,240),(75,155,255),        "meta_256"),
    (["prompt","prompting"],
     "Master AI with Perfect Prompts", "Prompt Eng",  CYAN,
     (0,150,200),(0,220,255),          None),
    (["seo","geo","aeo","rank","search engine"],
     "Rank Higher in the AI Era",      "AI SEO",      GREEN,
     (20,180,100),(40,240,150),        None),
    (["ads","advertising","marketing"],
     "The Future of AI Marketing",     "AI Marketing",AMBER,
     (200,120,0),(255,175,50),         None),
    (["automat","agent","workflow","langchain","crewai"],
     "Automate Everything with AI",    "AI Agents",   CYAN,
     (0,160,200),(0,220,255),          None),
    (["vs","compar","versus","better"],
     "Honest In-Depth Comparison",     "Comparison",  PURPLE,
     (100,30,200),(160,80,255),        None),
    (["guide","tutorial","how to","beginner"],
     "Complete Expert Guide · 2026",   "Tutorial",    GREEN,
     (20,180,100),(60,240,160),        None),
    (["review","best","top"],
     "Real Reviews & Benchmarks",      "Review",      AMBER,
     (200,130,0),(255,180,60),         None),
    (["trading","finance","invest"],
     "AI-Powered Financial Edge",      "AI Finance",  GREEN,
     (20,180,80),(60,230,120),         None),
    (["agi","future","2027"],
     "The Next Frontier of AI",        "AI Future",   PURPLE,
     (100,30,200),(180,90,255),        None),
    (["code","python","developer","api","build"],
     "Build Smarter with AI Code",     "AI Coding",   GREEN,
     (20,180,120),(50,230,160),        None),
    (["small business","india","startup","entrepreneur"],
     "AI Tools for Your Business",     "Business AI", AMBER,
     (200,130,20),(255,180,80),        None),
    (["productivity","automat","workflow"],
     "10x Your Output with AI",        "Productivity",CYAN,
     (0,160,200),(0,220,255),          None),
]

def get_meta(title):
    t = title.lower()
    for row in TOPIC_MAP:
        kws = row[0]
        if any(k in t for k in kws):
            _, sub, cat, cat_col, c1, c2, logo = row
            return sub, cat, cat_col, c1, c2, logo
    return ("Expert AI Insights · 2026", "AI Blog", CYAN,
            (0,160,200),(0,220,255), None)

# ─── FONT LOADER ─────────────────────────────────────────────────────────────
FONT_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_REG_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

_font_cache = {}
def fnt(size, bold=True):
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    paths = FONT_PATHS if bold else FONT_REG_PATHS
    for p in paths:
        if os.path.exists(p):
            try:
                f = ImageFont.truetype(p, size)
                _font_cache[key] = f
                return f
            except: pass
    f = ImageFont.load_default()
    _font_cache[key] = f
    return f

# ─── DRAWING PRIMITIVES ───────────────────────────────────────────────────────
def glow_blob(img, cx, cy, radius, color, max_alpha=55):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    d  = ImageDraw.Draw(ov)
    for r in range(radius, 0, -3):
        a = int(max_alpha * (1 - r/radius) ** 1.6)
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*color, a))
    img.alpha_composite(ov)

def scatter_dots(img, seed, count=90, area=None, color=WHITE, min_a=15, max_a=70):
    rng = random.Random(seed)
    x0, y0, x1, y1 = area or (0, 0, W, H)
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    d  = ImageDraw.Draw(ov)
    for _ in range(count):
        x = rng.randint(x0, x1)
        y = rng.randint(y0, y1)
        r = rng.uniform(0.5, 2.0)
        a = rng.randint(min_a, max_a)
        d.ellipse([x-r, y-r, x+r, y+r], fill=(*color, a))
    img.alpha_composite(ov)

def hex_grid(img, cx, cy, radius, color, alpha=18):
    """Draw subtle hexagon grid ring."""
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    d  = ImageDraw.Draw(ov)
    pts = []
    for i in range(6):
        a = math.radians(60*i - 30)
        pts.append((cx + radius*math.cos(a), cy + radius*math.sin(a)))
    d.polygon(pts, outline=(*color, alpha), fill=None)
    img.alpha_composite(ov)

def orbit_dots(img, cx, cy, orbit_r, count, color, dot_r=3, alpha=60, seed=0):
    rng  = random.Random(seed)
    ov   = Image.new("RGBA", img.size, (0,0,0,0))
    d    = ImageDraw.Draw(ov)
    step = 360 / count
    for i in range(count):
        a   = math.radians(step*i + rng.uniform(-8, 8))
        px  = int(cx + orbit_r*math.cos(a))
        py  = int(cy + orbit_r*math.sin(a))
        a2  = int(alpha * (0.5 + 0.5*math.sin(a*2.3)))
        d.ellipse([px-dot_r, py-dot_r, px+dot_r, py+dot_r], fill=(*color, a2))
    img.alpha_composite(ov)

def connection_lines(img, cx, cy, points, color, max_alpha=22):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    d  = ImageDraw.Draw(ov)
    for px, py in points:
        dist = math.hypot(px-cx, py-cy)
        a = int(max_alpha * (1 - min(dist/320, 1)))
        if a > 3:
            d.line([(cx,cy),(px,py)], fill=(*color, a), width=1)
    img.alpha_composite(ov)

def glass_circle(img, cx, cy, r, border_color, fill=(8,12,36), fill_a=215):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    d  = ImageDraw.Draw(ov)
    # subtle rim glow
    for i in range(4, 0, -1):
        d.ellipse([cx-r-i, cy-r-i, cx+r+i, cy+r+i],
                  outline=(*border_color, 20*i), width=2)
    # fill
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*fill, fill_a))
    # border
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(*border_color, 110), width=2)
    d.ellipse([cx-r+4, cy-r+4, cx+r-4, cy+r-4], outline=(*border_color, 35), width=1)
    img.alpha_composite(ov)

def grad_text_line(img, text, x, y, font, colors):
    """Draw gradient-colored text."""
    bb  = font.getbbox(text)
    tw  = max(bb[2]-bb[0], 1)
    th  = bb[3]-bb[1]+6
    tmp = Image.new("RGBA", (tw+4, th+10), (0,0,0,0))
    ImageDraw.Draw(tmp).text((0,0), text, font=font, fill=(255,255,255,255))
    gr  = Image.new("RGBA", (tw+4, th+10), (0,0,0,0))
    n   = len(colors) - 1
    for px in range(tw+4):
        seg = px / max(tw+3,1) * n
        i   = int(seg); t2 = seg - i
        c   = colors[-1] if i >= n else tuple(
              int(colors[i][j]+(colors[i+1][j]-colors[i][j])*t2) for j in range(3))
        ImageDraw.Draw(gr).line([(px,0),(px,th+10)], fill=(*c,255))
    out = Image.new("RGBA", (tw+4, th+10), (0,0,0,0))
    out.paste(gr, mask=tmp.split()[3])
    img.alpha_composite(out, (x, y))

def text_w(text, font, draw=None):
    bb = font.getbbox(text)
    return bb[2]-bb[0]

def wrap(text, font, max_px):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if text_w(test, font) <= max_px:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ─── RIGHT PANEL: glowing brand sphere ───────────────────────────────────────
def draw_right_panel(img, title, c1, c2, logo_name, seed):
    rng = random.Random(seed)
    cx, cy = 878, 312

    # Background glow blobs
    glow_blob(img, cx,    cy,    310, c1, 45)
    glow_blob(img, cx,    cy,    200, c2, 25)
    glow_blob(img, cx+90, cy+90, 180, PURPLE, 15)
    glow_blob(img, cx-70, cy-80, 150, (*c1,), 12)

    # Hex grid rings (decorative)
    for hr in [260, 200, 145]:
        hex_grid(img, cx, cy, hr, c2, alpha=12)

    # Outer orbit dots
    orbit_dots(img, cx, cy, 240, 24, c2, dot_r=3, alpha=55, seed=seed)
    orbit_dots(img, cx, cy, 165, 16, c1, dot_r=2, alpha=45, seed=seed+1)

    # Random scatter with connection lines
    scatter_pts = [(rng.randint(630,1170), rng.randint(20,610)) for _ in range(30)]
    connection_lines(img, cx, cy, scatter_pts, c2, max_alpha=20)
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    d  = ImageDraw.Draw(ov)
    for px, py in scatter_pts:
        dist = math.hypot(px-cx, py-cy)
        col  = c2 if rng.random() > 0.45 else PURPLE
        a    = max(int(50*(1-min(dist/320,1))), 12)
        d.ellipse([px-2, py-2, px+2, py+2], fill=(*col, a))
    img.alpha_composite(ov)

    # Floating highlight dots (bright)
    for _ in range(7):
        ang = rng.uniform(0, 6.28)
        r2  = rng.randint(75, 225)
        px, py = int(cx+math.cos(ang)*r2), int(cy+math.sin(ang)*r2)
        col = c2 if rng.random() > 0.4 else WHITE
        glow_blob(img, px, py, 18, col, 65)
        ov2 = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(ov2).ellipse([px-4,py-4,px+4,py+4], fill=(*col, 220))
        img.alpha_composite(ov2)

    # Glass sphere
    glass_circle(img, cx, cy, 122, c2)

    # Brand logo inside sphere
    logo_img = None
    if logo_name:
        lpath = Path(LOGOS_DIR)/f"{logo_name}.png"
        if lpath.exists():
            try:
                raw = Image.open(lpath).convert("RGBA").resize((148,148), Image.LANCZOS)
                logo_img = raw
            except: pass

    if logo_img:
        img.paste(logo_img, (cx-74, cy-74), logo_img.split()[3])
    else:
        # Draw letter(s) as fallback inside sphere
        letter = title[0].upper()
        fl = fnt(70, True)
        d2 = ImageDraw.Draw(img)
        lw = text_w(letter, fl, d2)
        lbb = fl.getbbox(letter)
        lh  = lbb[3]-lbb[1]
        d2.text((cx - lw//2, cy - lh//2 - 4), letter, font=fl, fill=(*c2, 220))

    # Subtle scan line across sphere
    ov3 = Image.new("RGBA", img.size, (0,0,0,0))
    d3  = ImageDraw.Draw(ov3)
    for sx in range(cx-118, cx+119):
        d3.line([(sx, cy-1),(sx, cy+1)], fill=(*c2, 8))
    img.alpha_composite(ov3)

    # Dot grid on right panel
    scatter_dots(img, seed+99, count=60, area=(620,0,W,H), color=c2, min_a=8, max_a=25)

# ─── LEFT PANEL: text content ────────────────────────────────────────────────
def draw_left_panel(img, title, subtitle, cat, cat_col, accent_c, logo_path, seed):
    d = ImageDraw.Draw(img)

    # ── Logo + brand name ──────────────────────────────────────────────────
    logo_placed = False
    for lp in [logo_path, "logo.png", "logo.jpg"]:
        if lp and os.path.exists(lp):
            try:
                raw = Image.open(lp).convert("RGBA")
                # make circular
                mask = Image.new("L", raw.size, 0)
                ImageDraw.Draw(mask).ellipse([0,0,raw.size[0]-1,raw.size[1]-1], fill=255)
                raw.putalpha(mask)
                logo_sz = 74
                raw = raw.resize((logo_sz, logo_sz), Image.LANCZOS)
                # glow behind logo
                glow_blob(img, 40+logo_sz//2, 22+logo_sz//2, 48, CYAN, 20)
                ov = Image.new("RGBA", img.size, (0,0,0,0))
                ov.paste(raw, (40, 22), raw.split()[3])
                img.alpha_composite(ov)
                logo_placed = True
                break
            except: pass

    if not logo_placed:
        d.rounded_rectangle([(40,20),(118,94)], radius=10,
                             fill=(12,18,52,230), outline=(*CYAN,140), width=2)
        d.text((48,24), "N+", font=fnt(38,True), fill=CYAN)

    d = ImageDraw.Draw(img)
    d.text((124, 24), "NeuraPulse",           font=fnt(20,True),  fill=(*WHITE, 235))
    d.text((124, 49), "AI Blog & Research Hub",font=fnt(13,False), fill=(*LGRAY, 155))
    # underline
    ov_u = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(ov_u).rectangle([(124,68),(310,70)], fill=(*CYAN, 55))
    img.alpha_composite(ov_u)

    # ── Category chip ──────────────────────────────────────────────────────
    d = ImageDraw.Draw(img)
    cf = fnt(14, True)
    cw = text_w(cat, cf, d) + 24
    chip = Image.new("RGBA", (cw, 30), (0,0,0,0))
    cd   = ImageDraw.Draw(chip)
    cd.rounded_rectangle([(0,0),(cw,30)], radius=12,
                          fill=(*cat_col,22), outline=(*cat_col,90), width=1)
    cd.text((12, 6), cat, font=cf, fill=(*cat_col, 235))
    img.alpha_composite(chip, (40, 122))

    # ── Title ──────────────────────────────────────────────────────────────
    tlen = len(title)
    if   tlen <= 18: fsz = 64
    elif tlen <= 26: fsz = 56
    elif tlen <= 36: fsz = 48
    elif tlen <= 48: fsz = 40
    elif tlen <= 62: fsz = 34
    else:            fsz = 29

    tf    = fnt(fsz, True)
    lines = wrap(title, tf, 565)
    ty    = 174

    color_sets = [
        [WHITE, WHITE, CYAN],
        [WHITE, CYAN, PURPLE],
        [CYAN, PURPLE, CYAN],
        [PURPLE, CYAN, WHITE],
    ]
    for li, line in enumerate(lines[:4]):
        cols = color_sets[li % len(color_sets)]
        grad_text_line(img, line, 40, ty, tf, cols)
        bb  = tf.getbbox(line)
        ty += (bb[3]-bb[1]) + 9

    # ── Subtitle ───────────────────────────────────────────────────────────
    ty += 14
    d = ImageDraw.Draw(img)
    d.text((40, ty), subtitle, font=fnt(21, False), fill=(*LGRAY, 195))

    # ── Accent bar trio ────────────────────────────────────────────────────
    ay = ty + 48
    d.rectangle([(40, ay),     (195, ay+3)], fill=(*accent_c, 220))
    d.rectangle([(40, ay+1),   (195, ay+5)], fill=(*accent_c, 50))  # glow
    d.rectangle([(200, ay),    (248, ay+3)], fill=(*PURPLE, 160))
    d.rectangle([(254, ay),    (278, ay+3)], fill=(*accent_c, 55))

    # ── Read time badge ────────────────────────────────────────────────────
    minutes = 5 + int(hashlib.md5(title.encode()).hexdigest()[:2], 16) % 11
    rt  = f"⏱  {minutes} min read"
    rtf = fnt(14, False)
    rtw = text_w(rt, rtf, d) + 20
    rt_x, rt_y = 40, ay + 18
    badge = Image.new("RGBA", (rtw, 26), (0,0,0,0))
    bd    = ImageDraw.Draw(badge)
    bd.rounded_rectangle([(0,0),(rtw,26)], radius=12,
                          fill=(*DGRAY,38), outline=(*DGRAY,52), width=1)
    bd.text((10, 4), rt, font=rtf, fill=(*LGRAY, 170))
    img.alpha_composite(badge, (rt_x, rt_y))

    # Three decorative dots
    for di, dc in enumerate([accent_c, PURPLE, DGRAY]):
        ddx = rt_x + rtw + 16 + di*22
        ddy = rt_y + 9
        ov2 = Image.new("RGBA", img.size, (0,0,0,0))
        dd  = ImageDraw.Draw(ov2)
        dd.ellipse([ddx-6, ddy-6, ddx+6, ddy+6], fill=(*dc, 180))
        dd.ellipse([ddx-9, ddy-9, ddx+9, ddy+9], outline=(*dc, 50), width=1)
        img.alpha_composite(ov2)

    # ── Bottom bar ─────────────────────────────────────────────────────────
    d = ImageDraw.Draw(img)
    d.rectangle([(0, H-52),(W, H)], fill=(*BG2, 245))
    # gradient line
    for x in range(W):
        t2 = x/W
        rc = int(accent_c[0]*(1-t2) + PURPLE[0]*t2)
        gc = int(accent_c[1]*(1-t2) + PURPLE[1]*t2)
        bc = int(accent_c[2]*(1-t2) + PURPLE[2]*t2)
        for ly2 in [H-54, H-53, H-52]:
            a = 150 if ly2 == H-53 else 60
            d.point((x, ly2), fill=(rc,gc,bc,a))

    d.text((40, H-36), "neuraplus-ai.github.io",
           font=fnt(16, False), fill=(*CYAN, 160))
    yr_txt = "2026 →"
    yw  = text_w(yr_txt, fnt(16,True), d)
    d.text((W-yw-30, H-36), yr_txt, font=fnt(16,True), fill=(*accent_c, 155))

    # Left edge accent bar
    ov3 = Image.new("RGBA", img.size, (0,0,0,0))
    d3  = ImageDraw.Draw(ov3)
    d3.rectangle([(0,0),(4,H)], fill=(*accent_c, 165))
    d3.rectangle([(0,0),(2,H)], fill=(*CYAN, 200))
    img.alpha_composite(ov3)

# ─── DIVIDER between panels ──────────────────────────────────────────────────
def draw_divider(img, accent_c):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    d  = ImageDraw.Draw(ov)
    for x in range(590, 640):
        # right-to-left fade
        ratio = (x - 590) / 50
        a     = int(100 * (1 - ratio))
        d.line([(x,0),(x,H)], fill=(*BG2, a))
    img.alpha_composite(ov)
    # subtle vertical line
    ov2 = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(ov2).line([(593,60),(593,H-60)], fill=(*accent_c, 18), width=1)
    img.alpha_composite(ov2)

# ─── BACKGROUND ──────────────────────────────────────────────────────────────
def build_background(seed):
    img = Image.new("RGBA", (W,H), (*BG1, 255))
    d   = ImageDraw.Draw(img)
    # vertical gradient
    for y in range(H):
        t2 = y/H
        r  = int(BG1[0]*(1-t2) + BG2[0]*t2)
        g2 = int(BG1[1]*(1-t2) + BG2[1]*t2)
        b  = int(BG1[2]*(1-t2) + BG2[2]*t2)
        d.line([(0,y),(W,y)], fill=(r,g2,b,255))
    # very subtle dot grid
    for gy in range(0, H, 42):
        for gx in range(0, W, 42):
            d.ellipse([gx-0.8,gy-0.8,gx+0.8,gy+0.8], fill=(*CYAN, 12))
    # star-field
    scatter_dots(img, seed+3, count=120, color=WHITE, min_a=12, max_a=65)
    scatter_dots(img, seed+4, count=50,  color=CYAN,  min_a=8,  max_a=30)
    return img

# ─── MAIN GENERATOR ──────────────────────────────────────────────────────────
def generate(slug, title):
    sub, cat, cat_col, c1, c2, logo_name = get_meta(title)
    seed   = int(hashlib.md5(slug.encode()).hexdigest(), 16) % 999983
    accent = c2  # dominant accent

    img = build_background(seed)

    # Ambient glow left panel
    glow_blob(img, 45, H//2, 270, CYAN,   16)
    glow_blob(img, 220, H-50, 170, PURPLE, 12)

    # Right panel (brand sphere)
    draw_right_panel(img, title, c1, c2, logo_name, seed)

    # Left→right fade overlay
    draw_divider(img, accent)

    # Left text panel
    draw_left_panel(img, title, sub, cat, cat_col, accent, None, seed)

    # Save
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    out = Path(OUT_DIR)/f"{slug}.webp"
    final = img.convert("RGB")
    # auto-reduce quality to stay ≤98KB
    for q in [WEBP_Q, 78, 70, 62, 55]:
        final.save(str(out), "WEBP", quality=q, method=6)
        if out.stat().st_size // 1024 <= 98:
            break
    return out, out.stat().st_size//1024

# ─── HTML INJECTION ───────────────────────────────────────────────────────────
def get_title(html, slug):
    m = re.search(r"<title>([^<]+)</title>", html, re.I)
    if m:
        t = re.sub(r"\s*[–—|-]\s*(NeuraPlusAI|NeuraPulse).*$","",m.group(1),flags=re.I)
        return t.strip()
    m2 = re.search(r"<h1[^>]*>([^<]+)</h1>", html, re.I)
    return m2.group(1).strip() if m2 else slug.replace("-"," ").title()

def inject(fp, slug, title):
    iw   = f"/{OUT_DIR}/{slug}.webp"
    ia   = f"{SITE_URL}{iw}"
    html = fp.read_text(encoding="utf-8", errors="ignore")
    # update og:image
    if re.search(r'property="og:image"', html, re.I):
        html = re.sub(r'(<meta\s+property="og:image"\s+content=")[^"]*(")',
                      f'\\g<1>{ia}\\g<2>', html)
    elif '</head>' in html:
        html = html.replace('</head>',
               f'  <meta property="og:image" content="{ia}" />\n</head>', 1)
    # update twitter:image
    if re.search(r'name="twitter:image"', html, re.I):
        html = re.sub(r'(<meta\s+name="twitter:image"\s+content=")[^"]*(")',
                      f'\\g<1>{ia}\\g<2>', html)
    elif '</head>' in html:
        html = html.replace('</head>',
               f'  <meta name="twitter:image" content="{ia}" />\n</head>', 1)
    # inject hero image after h1
    if iw not in html:
        hero = (f'\n<img src="{iw}" alt="{title}" class="blog-hero-image"'
                f' width="1200" height="630" loading="lazy" decoding="async"'
                f' style="width:100%;max-width:1200px;height:auto;'
                f'border-radius:12px;margin:0 auto 2rem;display:block;" />\n')
        h1 = re.search(r'(<h1[^>]*>.*?</h1>)', html, re.I|re.S)
        if h1:
            html = html[:h1.end()] + hero + html[h1.end():]
        else:
            art = re.search(r'(<(?:article|main|section)[^>]*>)', html, re.I)
            if art:
                html = html[:art.end()] + hero + html[art.end():]
    fp.write_text(html, encoding="utf-8")

def has_image(slug, html):
    if f"assets/images/blog/{slug}" in html: return True
    if "blog-hero-image" in html:             return True
    for ext in [".webp",".jpg",".jpeg",".png"]:
        if (Path(OUT_DIR)/f"{slug}{ext}").exists(): return True
    return False

# ─── GIT ─────────────────────────────────────────────────────────────────────
def git(cmd): subprocess.run(cmd, shell=True, check=False, capture_output=True)
def setup_git():
    git('git config user.name  "NeuraPulse Bot"')
    git('git config user.email "github-actions[bot]@users.noreply.github.com"')
def commit(msg):
    git(f'git add "{OUT_DIR}/" "{BLOG_DIR}/"')
    if subprocess.run("git diff --cached --quiet", shell=True).returncode != 0:
        git(f'git commit -m "auto: {msg} [skip ci]"')
        git("git fetch origin")
        git("git rebase origin/main 2>/dev/null || git rebase origin/master 2>/dev/null || true")
        git("git push origin HEAD:main 2>/dev/null || git push origin HEAD:master 2>/dev/null || true")
        print(f"  💾 Committed: {msg}")

# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
def main():
    setup_git()
    mode = "replace" if (len(sys.argv)>1 and sys.argv[1]=="replace") else "missing"
    bp   = Path(BLOG_DIR)
    if not bp.exists():
        print(f"❌  {BLOG_DIR}/ not found — run from repo root."); return

    posts = sorted([f for f in bp.glob("*.html")
                    if not any(f.stem.lower().startswith(s) for s in SKIP)])

    if mode == "missing":
        todo    = [(f,f.stem) for f in posts
                   if not has_image(f.stem,
                                    f.read_text(encoding="utf-8",errors="ignore"))]
        skipped = len(posts)-len(todo)
    else:
        todo    = [(f,f.stem) for f in posts]
        skipped = 0

    print(f"\n{'═'*56}")
    print(f"  NeuraPulse Image Generator")
    print(f"  Mode : {'REPLACE ALL' if mode=='replace' else 'MISSING ONLY'}")
    print(f"{'═'*56}")
    print(f"  Total posts   : {len(posts)}")
    if mode=="missing":
        print(f"  Already done  : {skipped}  (skipped)")
    print(f"  To generate   : {len(todo)}")
    print(f"  Output format : WebP  ≤ 98KB")
    print(f"{'═'*56}\n")

    if not todo:
        print("  🎉  All posts already have images.\n"); return

    ok = fail = 0
    for i, (fp, slug) in enumerate(todo, 1):
        html  = fp.read_text(encoding="utf-8", errors="ignore")
        title = get_title(html, slug)
        print(f"[{i:02d}/{len(todo)}] {slug}")
        print(f"  📝  {title}")
        try:
            out, kb = generate(slug, title)
            inject(fp, slug, title)
            print(f"  ✅  {kb}KB  →  {out}\n")
            ok += 1
            if ok % COMMIT_EVERY == 0:
                commit(f"batch {ok} images")
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"  ❌  {e}\n"); fail += 1

    if ok > 0:
        commit(f"generated {ok} images ({mode})")

    print(f"{'═'*56}")
    print(f"  ✅  Generated : {ok}")
    print(f"  ❌  Failed    : {fail}")
    print(f"{'═'*56}\n")

if __name__ == "__main__":
    main()
