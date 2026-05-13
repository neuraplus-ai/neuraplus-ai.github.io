"""
NeuraPlusAI — Auto Logo Watermark
==================================
Draws your exact brand logo onto every image in the repo.
Runs automatically via GitHub Actions on every push.
Also works locally: python add_logo.py

Logo design (matches your brand exactly):
  ┌──────────────────────┐
  │   dark outer circle  │
  │  ┌────────────────┐  │
  │  │   N  +  badge  │  │   ← cyan glow border
  │  └────────────────┘  │
  │   NEURAPLUS          │
  │   AI BLOG            │
  └──────────────────────┘
"""

import os
import sys
import json
import hashlib
import math
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌  pip install pillow")
    sys.exit(1)

# ══════════════════════════════════════════════════════
#  CONFIG  — edit here if needed
# ══════════════════════════════════════════════════════
CFG = {
    # folders to scan (relative to repo root)
    "scan_dirs": ["images", "blog/images", "assets", "thumbnails"],

    # file types
    "exts": {".png", ".jpg", ".jpeg", ".webp"},

    # logo position:  top-left | top-right | bottom-left | bottom-right
    "position": "top-left",

    # gap from image edge in px (scales with image size)
    "padding": 16,

    # logo diameter = image_width * this fraction
    "logo_scale": 0.10,

    # min / max logo diameter in px
    "logo_min": 64,
    "logo_max": 180,

    # file that tracks which images already have the logo (never re-process)
    "state_file": ".logo_state.json",

    # ── EXACT brand colours ──────────────────────────────
    "col": {
        "circle_bg":    (10,  8,  28),      # outer dark circle fill
        "circle_ring1": (0,  210, 255),     # cyan outer glow ring
        "circle_ring2": (100, 60, 220),     # purple inner ring
        "badge_bg":     (12,  8,  30),      # rounded square fill
        "badge_border": (0,  220, 255),     # cyan badge border
        "n_white":      (245, 245, 255),    # N letter
        "plus_cyan":    (0,  230, 255),     # + sign
        "name_white":   (255, 255, 255),    # NEURAPLUS
        "sub_grey":     (140, 155, 175),    # AI BLOG
    }
}

# ══════════════════════════════════════════════════════
#  STATE  — track processed files by content hash
# ══════════════════════════════════════════════════════

def load_state(root: Path) -> dict:
    f = root / CFG["state_file"]
    if f.exists():
        try:
            return json.loads(f.read_text())
        except Exception:
            return {}
    return {}

def save_state(root: Path, state: dict):
    f = root / CFG["state_file"]
    f.write_text(json.dumps(state, indent=2))

def file_hash(path: Path) -> str:
    """MD5 of first 64 KB — fast enough, unique enough."""
    h = hashlib.md5()
    with open(path, "rb") as fh:
        h.update(fh.read(65536))
    return h.hexdigest()

# ══════════════════════════════════════════════════════
#  FONT LOADER
# ══════════════════════════════════════════════════════

def font(bold: bool, size: int):
    size = max(8, size)
    candidates = (
        ["arialbd.ttf", "Arial Bold.ttf",
         "/System/Library/Fonts/Helvetica.ttc",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]
        if bold else
        ["arial.ttf", "Arial.ttf",
         "/System/Library/Fonts/Helvetica.ttc",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSans.ttf"]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    # PIL built-in fallback
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

# ══════════════════════════════════════════════════════
#  DRAWING HELPERS
# ══════════════════════════════════════════════════════

def filled_rounded_rect(draw, x0, y0, x1, y1, r, fill):
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx, cy in [(x0+r, y0+r), (x1-r, y0+r), (x0+r, y1-r), (x1-r, y1-r)]:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill)

def outline_rounded_rect(draw, x0, y0, x1, y1, r, colour, lw):
    for i in range(lw):
        o = i
        draw.arc([x0+o, y0+o, x0+2*r-o, y0+2*r-o], 180, 270, fill=colour)
        draw.arc([x1-2*r+o, y0+o, x1-o, y0+2*r-o], 270, 360, fill=colour)
        draw.arc([x0+o, y1-2*r+o, x0+2*r-o, y1-o], 90,  180, fill=colour)
        draw.arc([x1-2*r+o, y1-2*r+o, x1-o, y1-o], 0,   90,  fill=colour)
        draw.line([x0+r, y0+o, x1-r, y0+o], fill=colour)
        draw.line([x0+r, y1-o, x1-r, y1-o], fill=colour)
        draw.line([x0+o, y0+r, x0+o, y1-r], fill=colour)
        draw.line([x1-o, y0+r, x1-o, y1-r], fill=colour)

def outline_ellipse(draw, cx, cy, r, colour, lw):
    for i in range(lw):
        o = i
        draw.ellipse([cx-r+o, cy-r+o, cx+r-o, cy+r-o],
                     outline=colour, fill=None)

# ══════════════════════════════════════════════════════
#  LOGO RENDERER
# ══════════════════════════════════════════════════════

def render_logo(draw, img_w, img_h):
    """
    Draws the NeuraPlusAI logo at the configured position.
    Everything scales automatically with image size.
    """
    col = CFG["col"]

    # ── diameter & position ───────────────────────────────────────────────
    raw_d  = int(img_w * CFG["logo_scale"])
    diam   = max(CFG["logo_min"], min(raw_d, CFG["logo_max"]))
    pad    = CFG["padding"]
    pos    = CFG["position"]

    if   pos == "top-left":     ox, oy = pad, pad
    elif pos == "top-right":    ox, oy = img_w - diam - pad, pad
    elif pos == "bottom-left":  ox, oy = pad, img_h - diam - pad
    else:                       ox, oy = img_w - diam - pad, img_h - diam - pad

    r  = diam // 2          # radius of outer circle
    cx = ox + r             # circle centre x
    cy = oy + r             # circle centre y

    # ── outer dark circle ─────────────────────────────────────────────────
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col["circle_bg"])

    # cyan outer glow ring
    lw1 = max(2, diam // 28)
    outline_ellipse(draw, cx, cy, r - 1,             col["circle_ring1"], lw1)

    # purple inner ring
    lw2 = max(1, lw1 // 2)
    outline_ellipse(draw, cx, cy, int(r * 0.87),     col["circle_ring2"], lw2)

    # ── rounded square badge (N+) ─────────────────────────────────────────
    bsize  = int(r * 1.10)          # badge half-size
    b_x0   = cx - bsize // 2
    b_y0   = cy - bsize // 2 - int(r * 0.10)   # shifted up slightly
    b_x1   = b_x0 + bsize
    b_y1   = b_y0 + bsize
    brad   = max(4, bsize // 7)
    blw    = max(1, bsize // 18)

    filled_rounded_rect(draw, b_x0, b_y0, b_x1, b_y1, brad, col["badge_bg"])
    outline_rounded_rect(draw, b_x0, b_y0, b_x1, b_y1, brad, col["badge_border"], blw)

    # ── N letter ──────────────────────────────────────────────────────────
    n_sz  = int(bsize * 0.58)
    n_fnt = font(True, n_sz)
    n_cx  = (b_x0 + b_x1) // 2
    n_cy  = (b_y0 + b_y1) // 2 + int(bsize * 0.05)

    # subtle shadow
    draw.text((n_cx+1, n_cy+1), "N", font=n_fnt,
              fill=(0, 0, 0, 100), anchor="mm")
    draw.text((n_cx,   n_cy),   "N", font=n_fnt,
              fill=col["n_white"], anchor="mm")

    # ── + sign (top-right of badge) ───────────────────────────────────────
    p_sz  = int(bsize * 0.27)
    p_fnt = font(True, p_sz)
    draw.text(
        (b_x1 - int(bsize * 0.06), b_y0 + int(bsize * 0.12)),
        "+", font=p_fnt, fill=col["plus_cyan"], anchor="rt"
    )

    # ── NEURAPLUS text ────────────────────────────────────────────────────
    txt_y  = b_y1 + int(r * 0.07)
    nm_sz  = int(bsize * 0.21)
    nm_fnt = font(True, nm_sz)
    draw.text((cx, txt_y + nm_sz // 2), "NEURAPLUS",
              font=nm_fnt, fill=col["name_white"], anchor="mm")

    # ── AI BLOG text ──────────────────────────────────────────────────────
    sub_sz  = int(bsize * 0.15)
    sub_fnt = font(False, sub_sz)
    draw.text((cx, txt_y + nm_sz + int(sub_sz * 1.3)), "AI BLOG",
              font=sub_fnt, fill=col["sub_grey"], anchor="mm")

# ══════════════════════════════════════════════════════
#  IMAGE PROCESSOR
# ══════════════════════════════════════════════════════

def process_image(path: Path) -> bool:
    """Add logo to one image. Returns True on success."""
    try:
        img  = Image.open(path).convert("RGBA")
        over = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(over)

        render_logo(draw, img.width, img.height)

        result = Image.alpha_composite(img, over)

        ext = path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            result.convert("RGB").save(path, "JPEG", quality=95, optimize=True)
        elif ext == ".webp":
            result.save(path, "WEBP", quality=92)
        else:
            result.save(path, "PNG", optimize=True)

        return True
    except Exception as e:
        print(f"     ❌  {e}")
        return False

# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════

def main():
    root  = Path(".").resolve()
    state = load_state(root)

    print()
    print("━" * 52)
    print("  NeuraPlusAI  ·  Auto Logo Watermark")
    print(f"  {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    print("━" * 52)

    # ── collect images ────────────────────────────────────────────────────
    all_images: list[Path] = []
    for d in CFG["scan_dirs"]:
        scan = root / d
        if not scan.exists():
            continue
        for ext in CFG["exts"]:
            all_images += scan.rglob(f"*{ext}")
            all_images += scan.rglob(f"*{ext.upper()}")

    # deduplicate
    all_images = list({p.resolve() for p in all_images})

    if not all_images:
        print("\n  ⚠️   No images found.")
        print(f"  Check scan_dirs in CFG: {CFG['scan_dirs']}")
        print()
        return

    print(f"\n  Found {len(all_images)} image(s) total\n")

    done = skipped = errors = 0

    for path in sorted(all_images):
        rel   = str(path.relative_to(root))
        h     = file_hash(path)
        label = f"  {rel}"

        # already processed → same hash in state
        if state.get(rel) == h:
            print(f"{label}  →  ⏭  already done")
            skipped += 1
            continue

        print(f"{label}  →  ", end="", flush=True)
        ok = process_image(path)

        if ok:
            # record NEW hash after modification
            state[rel] = file_hash(path)
            done += 1
            print("✅")
        else:
            errors += 1

    save_state(root, state)

    print()
    print("━" * 52)
    print(f"  ✅  Processed : {done}")
    print(f"  ⏭   Skipped   : {skipped}  (already had logo)")
    print(f"  ❌  Errors    : {errors}")
    print("━" * 52)

    if done > 0:
        print(f"""
  Push to GitHub:
    git add .
    git commit -m "🖼 Add NeuraPlusAI logo to {done} images"
    git push
""")


if __name__ == "__main__":
    main()
