"""
NeuraPlusAI — Logo Watermark Script
Adds your exact brand logo to every image in the repo.
Usage:  python add_logo.py
"""
import os, sys, json, hashlib
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌  Run:  pip install pillow"); sys.exit(1)

# ══════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════
CFG = {
    "scan_dirs": [
        "images", "blog/images", "assets", "assets/images",
        "thumbnails", "static", "img", "media", "blog", ".",
    ],
    "exts":       {".png", ".jpg", ".jpeg", ".webp"},
    "position":   "top-left",
    "padding":    16,
    "logo_scale": 0.10,
    "logo_min":   60,
    "logo_max":   170,
    "state_file": ".logo_state.json",
    "only_names_containing": [],
    "skip_names_containing": ["favicon", "icon-", "apple-touch", "logo", "avatar"],
}

COL = {
    "circle_bg":    (10,   8,  28),
    "ring_cyan":    (0,  210, 255),
    "ring_purple":  (100,  60, 220),
    "badge_bg":     (12,   8,  30),
    "badge_border": (0,  220, 255),
    "n_white":      (245, 245, 255),
    "plus_cyan":    (0,  230, 255),
    "name_white":   (255, 255, 255),
    "sub_grey":     (140, 155, 175),
}

def load_state(root):
    f = root / CFG["state_file"]
    try:    return json.loads(f.read_text()) if f.exists() else {}
    except: return {}

def save_state(root, state):
    (root / CFG["state_file"]).write_text(json.dumps(state, indent=2))

def fhash(path):
    h = hashlib.md5()
    with open(path,"rb") as fh: h.update(fh.read(65536))
    return h.hexdigest()

def get_font(bold, size):
    size = max(8, size)
    paths = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
         "arialbd.ttf"]
        if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
         "arial.ttf"]
    )
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except: pass
    try:    return ImageFont.load_default(size=size)
    except: return ImageFont.load_default()

def filled_rr(d, x0,y0,x1,y1,r,fill):
    d.rectangle([x0+r,y0,x1-r,y1], fill=fill)
    d.rectangle([x0,y0+r,x1,y1-r], fill=fill)
    for cx,cy in [(x0+r,y0+r),(x1-r,y0+r),(x0+r,y1-r),(x1-r,y1-r)]:
        d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=fill)

def outline_rr(d, x0,y0,x1,y1,r,col,lw):
    for i in range(max(1,lw)):
        o=i
        d.arc([x0+o,y0+o,x0+2*r-o,y0+2*r-o],180,270,fill=col)
        d.arc([x1-2*r+o,y0+o,x1-o,y0+2*r-o],270,360,fill=col)
        d.arc([x0+o,y1-2*r+o,x0+2*r-o,y1-o],90,180,fill=col)
        d.arc([x1-2*r+o,y1-2*r+o,x1-o,y1-o],0,90,fill=col)
        d.line([x0+r,y0+o,x1-r,y0+o],fill=col)
        d.line([x0+r,y1-o,x1-r,y1-o],fill=col)
        d.line([x0+o,y0+r,x0+o,y1-r],fill=col)
        d.line([x1-o,y0+r,x1-o,y1-r],fill=col)

def draw_logo(draw, img_w, img_h):
    raw_d = int(img_w * CFG["logo_scale"])
    diam  = max(CFG["logo_min"], min(raw_d, CFG["logo_max"]))
    pad   = CFG["padding"]
    pos   = CFG["position"]

    if   pos == "top-left":     ox,oy = pad, pad
    elif pos == "top-right":    ox,oy = img_w-diam-pad, pad
    elif pos == "bottom-left":  ox,oy = pad, img_h-diam-pad
    else:                       ox,oy = img_w-diam-pad, img_h-diam-pad

    r=diam//2; cx=ox+r; cy=oy+r

    draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=COL["circle_bg"])
    lw1=max(2,diam//28)
    for i,a in enumerate([200,130,60]):
        draw.ellipse([cx-r+i,cy-r+i,cx+r-i,cy+r-i], outline=(*COL["ring_cyan"],a), width=1)
    ir=int(r*0.87)
    draw.ellipse([cx-ir,cy-ir,cx+ir,cy+ir], outline=(*COL["ring_purple"],160), width=max(1,lw1//2))

    bsize=int(r*1.10); bx0=cx-bsize//2; by0=cy-bsize//2-int(r*0.10)
    bx1=bx0+bsize; by1=by0+bsize; brad=max(4,bsize//7); blw=max(1,bsize//18)
    filled_rr(draw,bx0,by0,bx1,by1,brad,COL["badge_bg"])
    outline_rr(draw,bx0,by0,bx1,by1,brad,COL["badge_border"],blw)

    n_fnt=get_font(True,int(bsize*0.60))
    ncx=(bx0+bx1)//2; ncy=(by0+by1)//2+int(bsize*0.05)
    draw.text((ncx+1,ncy+1),"N",font=n_fnt,fill=(0,0,0,100),anchor="mm")
    draw.text((ncx,ncy),"N",font=n_fnt,fill=COL["n_white"],anchor="mm")

    p_fnt=get_font(True,int(bsize*0.28))
    draw.text((bx1-int(bsize*0.06),by0+int(bsize*0.12)),"+",font=p_fnt,fill=COL["plus_cyan"],anchor="rt")

    nm_sz=int(bsize*0.22); nm_fnt=get_font(True,nm_sz); txt_y=by1+int(r*0.07)
    draw.text((cx,txt_y+nm_sz//2),"NEURAPLUS",font=nm_fnt,fill=COL["name_white"],anchor="mm")

    sub_sz=int(bsize*0.15); sub_fnt=get_font(False,sub_sz)
    draw.text((cx,txt_y+nm_sz+int(sub_sz*1.4)),"AI BLOG",font=sub_fnt,fill=COL["sub_grey"],anchor="mm")

def process_image(path):
    try:
        img=Image.open(path).convert("RGBA")
        over=Image.new("RGBA",img.size,(0,0,0,0))
        draw=ImageDraw.Draw(over)
        draw_logo(draw,img.width,img.height)
        result=Image.alpha_composite(img,over)
        ext=path.suffix.lower()
        if ext in (".jpg",".jpeg"):
            result.convert("RGB").save(path,"JPEG",quality=95,optimize=True)
        elif ext==".webp":
            result.save(path,"WEBP",quality=92)
        else:
            result.save(path,"PNG",optimize=True)
        return True
    except Exception as e:
        print(f"    ❌ {e}"); return False

def main():
    root=Path(".").resolve()
    state=load_state(root)
    print(); print("━"*55)
    print("  NeuraPlusAI · Auto Logo Watermark")
    print(f"  {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    print("━"*55)

    all_images=set()
    for d in CFG["scan_dirs"]:
        scan=root/d
        if not scan.exists(): continue
        for ext in CFG["exts"]:
            all_images.update(scan.rglob(f"*{ext}"))
            all_images.update(scan.rglob(f"*{ext.upper()}"))

    filtered=[]
    for p in sorted(all_images):
        name=p.name.lower()
        if any(part.startswith('.') for part in p.parts): continue
        if any(s in name for s in CFG["skip_names_containing"]): continue
        if CFG["only_names_containing"]:
            if not any(s in name for s in CFG["only_names_containing"]): continue
        filtered.append(p)

    if not filtered:
        print("\n  ⚠️  No images found.\n"); return

    print(f"\n  Found {len(filtered)} image(s)\n")
    done=skipped=errors=0

    for path in filtered:
        rel=str(path.relative_to(root))
        h=fhash(path)
        print(f"  {rel:<55}", end="", flush=True)
        if state.get(rel)==h:
            print("⏭  done"); skipped+=1; continue
        ok=process_image(path)
        if ok:
            state[rel]=fhash(path); done+=1; print("✅")
        else:
            errors+=1

    save_state(root,state)
    print(); print("━"*55)
    print(f"  ✅  Processed : {done}")
    print(f"  ⏭   Skipped   : {skipped}  (already done)")
    print(f"  ❌  Errors    : {errors}")
    print("━"*55)
    if done>0:
        print(f"\n  git add . && git commit -m '🖼 Logo on {done} images' && git push\n")

if __name__=="__main__":
    main()
