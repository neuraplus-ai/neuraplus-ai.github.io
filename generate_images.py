#!/usr/bin/env python3
"""
NeuraPlusAI Blog Image Generator — FINAL VERSION
==================================================
TWO MODES:
  python3 generate_images.py            → adds images ONLY to posts missing them
  python3 generate_images.py replace    → replaces ALL images (including existing)

SMART LOGIC:
  • Reads every blog/*.html file
  • "missing" mode  → skips posts that already have an image
  • "replace" mode  → regenerates every post regardless
  • Injects <img> + og:image + twitter:image into HTML
  • Auto-commits & pushes to GitHub

FILES NEEDED in same folder:
  logo.jpg    — your NeuraPlusAI N+ circular logo
  logos/      — brand logo PNGs (claude_256.png, chatgpt_256.png, etc.)
"""

import os, re, sys, math, hashlib, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ────────────────────────────────────────────────
YOUR_LOGO    = "logo.jpg"
LOGOS_DIR    = "logos"
BLOG_DIR     = "blog"
OUT_DIR      = "assets/images/blog"
SITE_URL     = "https://neuraplus-ai.github.io"
COMMIT_EVERY = 5
W, H         = 1200, 630
WEBP_QUALITY = 82

SKIP = ["index","404","about","contact","privacy",
        "sitemap","terms","search","tag","category","archive","author"]

# ── COLORS ──────────────────────────────────────
BG_TOP  = ( 4,  7, 22)
BG_BOT  = ( 8, 12, 32)
CYAN    = ( 0,220,255)
PURPLE  = (130, 40,230)
AMBER   = (255,165, 20)
GREEN   = ( 40,220,140)
WHITE   = (255,255,255)
LGRAY   = (190,205,225)
DGRAY   = ( 80, 95,120)

# ── BRAND DATABASE ──────────────────────────────
BRANDS = [
    (["claude","anthropic"],
     ("claude_256",(210,120,40),(255,175,70),"Claude AI","Anthropic")),
    (["chatgpt","gpt-4","gpt-3"],
     ("chatgpt_256",(16,163,127),(50,210,150),"ChatGPT","OpenAI")),
    (["openai","openai o"],
     ("openai_256",(20,20,20),(200,200,200),"OpenAI","openai.com")),
    (["gemini","google ai","bard"],
     ("gemini_256",(30,110,230),(100,175,255),"Google Gemini","Google")),
    (["perplexity"],
     ("perplexity_256",(10,15,50),(0,210,255),"Perplexity AI","perplexity.ai")),
    (["groq"],
     ("groq_256",(110,35,170),(195,120,255),"Groq","groq.com")),
    (["kimi","moonshot"],
     ("kimi_256",(0,100,160),(0,185,225),"Kimi AI","Moonshot AI")),
    (["deepseek"],
     ("deepseek_256",(8,10,40),(0,120,255),"DeepSeek","deepseek.com")),
    (["mistral"],
     ("mistral_256",(190,75,0),(255,125,35),"Mistral AI","mistral.ai")),
    (["meta ai","llama","meta"],
     ("meta_256",(20,115,240),(75,155,255),"Meta AI","Meta")),
]

CATS = [
    (["claude","anthropic"],           ("AI Model",   AMBER)),
    (["chatgpt","openai","gpt"],        ("AI Model",   GREEN)),
    (["gemini","google"],               ("AI Model",   (80,150,255))),
    (["groq"],                          ("AI Speed",   PURPLE)),
    (["deepseek"],                      ("Open Source LLM",(0,120,255))),
    (["perplexity"],                    ("AI Search",  CYAN)),
    (["kimi","moonshot"],               ("LLM Review", CYAN)),
    (["mistral"],                       ("AI Model",   AMBER)),
    (["prompt","prompting"],            ("Prompt Engineering",CYAN)),
    (["seo","geo","rank"],              ("AI SEO",     GREEN)),
    (["ads","advertising","marketing"], ("AI Marketing",AMBER)),
    (["automat","agent","workflow"],    ("AI Automation",CYAN)),
    (["vs","compare","versus"],         ("Comparison", PURPLE)),
    (["guide","tutorial","how to"],     ("Tutorial",   GREEN)),
    (["review","best","top"],           ("Review",     AMBER)),
    (["trading","finance"],             ("AI Finance", GREEN)),
    (["agi","future"],                  ("AI Future",  PURPLE)),
    (["code","python","dev"],           ("AI Coding",  GREEN)),
]
def get_cat(t):
    t=t.lower()
    for kws,(c,col) in CATS:
        if any(k in t for k in kws): return c,col
    return "AI Insights",CYAN

SUBS = [
    (["kimi"],             "China's Most Powerful Open-Source LLM"),
    (["claude"],           "Anthropic's Most Capable AI Assistant"),
    (["chatgpt","openai"], "OpenAI's Revolutionary AI Platform"),
    (["gemini"],           "Google's Next-Generation AI Model"),
    (["groq"],             "The World's Fastest AI Inference Engine"),
    (["deepseek"],         "Open-Source AI That Rivals the Best"),
    (["perplexity"],       "The AI-First Answer Search Engine"),
    (["mistral"],          "Europe's Best Open-Source AI"),
    (["llama","meta"],     "Meta's Open-Source AI Powerhouse"),
    (["prompt"],           "Master AI with Perfect Prompts"),
    (["seo","geo"],        "Rank Higher in the AI Search Era"),
    (["ads","marketing"],  "The Future of AI-Powered Marketing"),
    (["automat","agent"],  "Automate Everything with AI Agents"),
    (["vs","compare"],     "Honest In-Depth Comparison · 2026"),
    (["guide","tutorial"], "Complete Expert Guide · 2026"),
    (["review","best"],    "Real Review & Benchmarks · 2026"),
    (["agi","future"],     "The Next Frontier of Intelligence"),
    (["trading","finance"],"AI-Powered Financial Intelligence"),
]
def get_sub(t):
    t=t.lower()
    for kws,s in SUBS:
        if any(k in t for k in kws): return s
    return "Expert AI Insights · NeuraPlusAI · 2026"

def get_brand(title):
    t=title.lower()
    for kws,info in BRANDS:
        if any(k in t for k in kws): return info
    return None

# ── FONTS ────────────────────────────────────────
FD="/usr/share/fonts/truetype"
def fnt(size,w="bold"):
    p=(f"{FD}/google-fonts/Poppins-Bold.ttf" if w=="bold"
       else f"{FD}/google-fonts/Poppins-Medium.ttf"
       if w=="medium" else f"{FD}/google-fonts/Poppins-Regular.ttf")
    if not os.path.exists(p): p=f"{FD}/dejavu/DejaVuSans-Bold.ttf"
    try: return ImageFont.truetype(p,size)
    except: return ImageFont.load_default()

# ── DRAW HELPERS ─────────────────────────────────
_cache={}

def load_brand_logo(name,size=148):
    key=f"b_{name}_{size}"
    if key in _cache: return _cache[key]
    p=Path(LOGOS_DIR)/f"{name}.png"
    if p.exists():
        try:
            img=Image.open(p).convert("RGBA").resize((size,size),Image.LANCZOS)
            _cache[key]=img; return img
        except: pass
    return None

def load_your_logo(size=76):
    if "yl" in _cache: raw=_cache["yl"]
    elif os.path.exists(YOUR_LOGO):
        try:
            raw=Image.open(YOUR_LOGO).convert("RGBA")
            mask=Image.new("L",raw.size,0)
            ImageDraw.Draw(mask).ellipse([0,0,raw.size[0]-1,raw.size[1]-1],fill=255)
            raw.putalpha(mask); _cache["yl"]=raw
        except: return None
    else: return None
    return raw.copy().resize((size,size),Image.LANCZOS)

def glow(img,cx,cy,r,col,a=60):
    ov=Image.new("RGBA",img.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
    for i in range(r,0,-3):
        alpha=int(a*(1-i/r)**1.8)
        d.ellipse([cx-i,cy-i,cx+i,cy+i],fill=(*col,alpha))
    img.alpha_composite(ov)

def noise(img,col,n,seed,ar=(8,25)):
    rng=__import__("random").Random(seed)
    ov=Image.new("RGBA",img.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
    for _ in range(n):
        x=rng.randint(0,W); y=rng.randint(0,H)
        r=rng.uniform(.5,2); a=rng.randint(*ar)
        d.ellipse([x-r,y-r,x+r,y+r],fill=(*col,a))
    img.alpha_composite(ov)

def wt(text,maxc):
    words,lines,cur=text.split(),[],""
    for w in words:
        t=(cur+" "+w).strip()
        if len(t)<=maxc: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def grad_text(img,text,x,y,f,c1,c2,c3=None):
    tmp=Image.new("RGBA",img.size,(0,0,0,0))
    ImageDraw.Draw(tmp).text((x,y),text,font=f,fill=(255,255,255,255))
    bb=f.getbbox(text); tw=max(bb[2]-bb[0],1)
    gr=Image.new("RGBA",img.size,(0,0,0,0)); gd=ImageDraw.Draw(gr); c3=c3 or c2
    for i in range(tw):
        t2=i/tw
        if t2<.5: tt=t2/.5; col=tuple(int(c1[k]+(c2[k]-c1[k])*tt) for k in range(3))
        else: tt=(t2-.5)/.5; col=tuple(int(c2[k]+(c3[k]-c2[k])*tt) for k in range(3))
        gd.line([(x+i,y),(x+i,y+f.size+4)],fill=(*col,255))
    out=Image.new("RGBA",img.size,(0,0,0,0)); out.paste(gr,mask=tmp.split()[3])
    img.alpha_composite(out)

# ── BRAND PANEL (RIGHT) ──────────────────────────
def draw_right(img,title,brand,seed):
    rng=__import__("random").Random(seed); cx,cy=875,310
    lf,bc,ac,bn,src=(brand if brand else (None,(60,30,120),(120,60,220),"AI","2026"))
    glow(img,cx,cy,300,bc,50); glow(img,cx,cy,200,ac,25)
    glow(img,cx+80,cy+80,180,PURPLE,15)
    ov=Image.new("RGBA",img.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
    for x in range(610,W,48):
        for y in range(0,H,48): d.ellipse([x-1,y-1,x+1,y+1],fill=(*ac,10))
    img.alpha_composite(ov)
    for i in range(24):
        a=math.radians(i*15); px=int(cx+math.cos(a)*225); py=int(cy+math.sin(a)*225)
        ov2=Image.new("RGBA",img.size,(0,0,0,0))
        ImageDraw.Draw(ov2).ellipse([px-3,py-3,px+3,py+3],fill=(*ac,55+int(30*math.sin(a*3))))
        img.alpha_composite(ov2)
    for i in range(16):
        a=math.radians(i*22.5+11.25); px=int(cx+math.cos(a)*155); py=int(cy+math.sin(a)*155)
        ov3=Image.new("RGBA",img.size,(0,0,0,0))
        ImageDraw.Draw(ov3).ellipse([px-2,py-2,px+2,py+2],fill=(*bc,50))
        img.alpha_composite(ov3)
    for ang in [rng.uniform(0,6.28) for _ in range(6)]:
        r2=rng.randint(80,220); px=int(cx+math.cos(ang)*r2); py=int(cy+math.sin(ang)*r2)
        col=ac if rng.random()>.4 else WHITE
        glow(img,px,py,18,col,60)
        ov4=Image.new("RGBA",img.size,(0,0,0,0))
        ImageDraw.Draw(ov4).ellipse([px-4,py-4,px+4,py+4],fill=(*col,220))
        img.alpha_composite(ov4)
    scatter=[(rng.randint(625,1175),rng.randint(20,610)) for _ in range(28)]
    ov5=Image.new("RGBA",img.size,(0,0,0,0)); d5=ImageDraw.Draw(ov5)
    for nx,ny in scatter:
        dist=math.hypot(nx-cx,ny-cy)
        col=ac if rng.random()>.45 else PURPLE
        d5.ellipse([nx-2,ny-2,nx+2,ny+2],fill=(*col,max(int(50*(1-min(dist/320,1))),15)))
        if dist<260: d5.line([(cx,cy),(nx,ny)],fill=(*ac,max(int(25*(1-dist/260)),5)),width=1)
    img.alpha_composite(ov5)
    glass=Image.new("RGBA",(240,240),(0,0,0,0)); gd2=ImageDraw.Draw(glass)
    for i in range(120,85,-2):
        a2=int(45*(1-(120-i)/35)**2)
        gd2.ellipse([120-i,120-i,120+i,120+i],fill=(*ac,a2))
    gd2.ellipse([6,6,234,234],fill=(8,12,36,215))
    gd2.ellipse([6,6,234,234],outline=(*ac,100),width=2)
    gd2.ellipse([10,10,230,230],outline=(*ac,40),width=1)
    img.paste(glass,(cx-120,cy-120),glass)
    logo=load_brand_logo(lf,148) if lf else None
    if logo:
        img.paste(logo,(cx-74,cy-74),logo.split()[3])
        bf=fnt(19,"bold"); bd=ImageDraw.Draw(img)
        bw=int(bd.textlength(bn,font=bf))
        bd.text((cx-bw//2,cy+88),bn,font=bf,fill=(*ac,210))
        sf=fnt(14,"medium"); sw=int(bd.textlength(src,font=sf))
        bd.text((cx-sw//2,cy+110),src,font=sf,fill=(*DGRAY,180))
    else:
        glow(img,cx,cy,55,ac,90)
        ov6=Image.new("RGBA",img.size,(0,0,0,0))
        ImageDraw.Draw(ov6).ellipse([cx-18,cy-18,cx+18,cy+18],fill=(*ac,230))
        img.alpha_composite(ov6)

# ── TEXT PANEL (LEFT) ────────────────────────────
def draw_left(img,title,subtitle,cat,cat_col,brand):
    d=ImageDraw.Draw(img); ac=brand[2] if brand else CYAN
    yl=load_your_logo(76)
    if yl:
        glow(img,78,54,44,CYAN,18)
        ov=Image.new("RGBA",img.size,(0,0,0,0))
        ov.paste(yl,(40,16),yl.split()[3]); img.alpha_composite(ov)
    else:
        d.rounded_rectangle([(40,16),(116,92)],radius=10,fill=(12,18,52,230),outline=(*CYAN,140),width=2)
        d.text((48,20),"N+",font=fnt(40,"bold"),fill=CYAN)
    d.text((134,20),"NeuraPlusAI",font=fnt(20,"bold"),fill=(*CYAN,235))
    d.text((134,46),"AI Blog & Intelligence Hub",font=fnt(14,"medium"),fill=(*LGRAY,160))
    ov_u=Image.new("RGBA",img.size,(0,0,0,0))
    ImageDraw.Draw(ov_u).rectangle([(134,68),(310,70)],fill=(*CYAN,60))
    img.alpha_composite(ov_u)
    cf=fnt(15,"bold"); cw=int(d.textlength(cat,font=cf)); px,py=40,126
    d.rounded_rectangle([(px,py-4),(px+cw+20,py+22)],radius=11,fill=(*cat_col,25),outline=(*cat_col,90),width=1)
    d.text((px+10,py),cat,font=cf,fill=(*cat_col,235))
    tlen=len(title)
    fsz=62 if tlen<=18 else 52 if tlen<=28 else 44 if tlen<=38 else 38 if tlen<=50 else 33
    tf=fnt(fsz,"bold")
    lines=wt(title,19 if fsz>=52 else 23 if fsz>=44 else 27 if fsz>=38 else 31)
    ty=178
    for i,line in enumerate(lines[:3]):
        cols=[(WHITE,CYAN,PURPLE),(CYAN,PURPLE,CYAN),(PURPLE,CYAN,WHITE)]
        c1,c2,c3=cols[i%3]
        grad_text(img,line,40,ty,tf,c1,c2,c3)
        ty+=fsz+8
    ty+=12; d.text((40,ty),subtitle,font=fnt(22,"medium"),fill=(*LGRAY,195))
    ly=ty+42
    d.rectangle([(40,ly),(190,ly+3)],fill=(*ac,210))
    d.rectangle([(196,ly),(244,ly+3)],fill=(*PURPLE,160))
    d.rectangle([(250,ly),(272,ly+3)],fill=(*ac,60))
    minutes=5+int(hashlib.md5(title.encode()).hexdigest()[:2],16)%11
    rt=f"⏱ {minutes} min read"; rtf=fnt(14,"medium")
    rtw=int(d.textlength(rt,font=rtf)); rt_x,rt_y=40,ly+18
    d.rounded_rectangle([(rt_x,rt_y),(rt_x+rtw+16,rt_y+22)],radius=11,fill=(*DGRAY,40),outline=(*DGRAY,55),width=1)
    d.text((rt_x+8,rt_y+2),rt,font=rtf,fill=(*LGRAY,175))
    d.rectangle([(0,H-55),(W,H)],fill=(*BG_BOT,240))
    ov8=Image.new("RGBA",(W,3),(0,0,0,0))
    for x in range(W):
        t3=x/W; rc=int(ac[0]*(1-t3)+PURPLE[0]*t3)
        gc=int(ac[1]*(1-t3)+PURPLE[1]*t3); bc2=int(ac[2]*(1-t3)+PURPLE[2]*t3)
        ov8.putpixel((x,0),(rc,gc,bc2,140)); ov8.putpixel((x,1),(rc,gc,bc2,70))
    img.paste(ov8,(0,H-57),ov8)
    d.text((40,H-38),"neuraplus-ai.github.io",font=fnt(17,"medium"),fill=(*CYAN,165))
    yf=fnt(17,"bold"); yw=int(d.textlength("2026",font=yf))
    d.text((W-60-yw,H-38),"2026",font=yf,fill=(*LGRAY,140))
    d.text((W-55,H-38),"→",font=fnt(17,"bold"),fill=(*ac,180))
    ov9=Image.new("RGBA",img.size,(0,0,0,0))
    ImageDraw.Draw(ov9).rectangle([(0,0),(4,H)],fill=(*ac,160))
    img.alpha_composite(ov9)

def left_fade(img,width=510):
    ov=Image.new("RGBA",img.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
    for x in range(width):
        a=int(255*(1-(x/width)**1.5))
        d.line([(x,0),(x,H)],fill=(*BG_BOT,a))
    img.alpha_composite(ov)

def stars(img,seed):
    rng=__import__("random").Random(seed+7777)
    ov=Image.new("RGBA",img.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
    for _ in range(110):
        x=rng.randint(0,W); y=rng.randint(0,H); r=rng.uniform(.5,1.8); a=rng.randint(20,85)
        d.ellipse([x-r,y-r,x+r,y+r],fill=(255,255,255,a))
    img.alpha_composite(ov)

# ── MAIN GENERATOR ───────────────────────────────
def generate(slug,title):
    subtitle=get_sub(title); cat,cat_col=get_cat(title)
    brand=get_brand(title)
    seed=int(hashlib.md5(slug.encode()).hexdigest(),16)%999983
    img=Image.new("RGBA",(W,H),(0,0,0,255))
    d=ImageDraw.Draw(img)
    for y in range(H):
        t=y/H; r=int(BG_TOP[0]*(1-t)+BG_BOT[0]*t)
        g2=int(BG_TOP[1]*(1-t)+BG_BOT[1]*t); b=int(BG_TOP[2]*(1-t)+BG_BOT[2]*t)
        d.line([(0,y),(W,y)],fill=(r,g2,b,255))
    noise(img,CYAN,80,seed); noise(img,WHITE,60,seed+1)
    draw_right(img,title,brand,seed)
    left_fade(img,510)
    glow(img,40,H//2,260,CYAN,16); glow(img,200,H-40,160,PURPLE,10)
    stars(img,seed)
    draw_left(img,title,subtitle,cat,cat_col,brand)
    Path(OUT_DIR).mkdir(parents=True,exist_ok=True)
    out=Path(OUT_DIR)/f"{slug}.webp"
    final=img.convert("RGB")
    for q in [WEBP_QUALITY,75,68,60]:
        final.save(out,"WEBP",quality=q,method=6)
        if out.stat().st_size//1024<=98: break
    return out,out.stat().st_size//1024

# ── HTML HELPERS ─────────────────────────────────
def get_title(html,slug):
    m=re.search(r"<title>([^<]+)</title>",html,re.I)
    if m:
        t=re.sub(r"\s*[–—|-]\s*(NeuraPlusAI|NeuraPulse).*$","",m.group(1),flags=re.I)
        return t.strip()
    m2=re.search(r"<h1[^>]*>([^<]+)</h1>",html,re.I)
    return m2.group(1).strip() if m2 else slug.replace("-"," ").title()

def inject(fp,slug,title):
    iw=f"/{OUT_DIR}/{slug}.webp"; ia=f"{SITE_URL}{iw}"
    html=fp.read_text(encoding="utf-8",errors="ignore")
    if re.search(r'<meta\s+property="og:image"',html,re.I):
        html=re.sub(r'(<meta\s+property="og:image"\s+content=")[^"]*(")',f'\\g<1>{ia}\\g<2>',html)
    elif '</head>' in html:
        html=html.replace('</head>',f'  <meta property="og:image" content="{ia}" />\n</head>',1)
    if re.search(r'<meta\s+name="twitter:image"',html,re.I):
        html=re.sub(r'(<meta\s+name="twitter:image"\s+content=")[^"]*(")',f'\\g<1>{ia}\\g<2>',html)
    elif '</head>' in html:
        html=html.replace('</head>',f'  <meta name="twitter:image" content="{ia}" />\n</head>',1)
    if iw not in html:
        hero=(f'\n<img src="{iw}" alt="{title}" class="blog-hero-image" '
              f'width="1200" height="630" loading="lazy" decoding="async" '
              f'style="width:100%;max-width:1200px;height:auto;border-radius:12px;margin:0 auto 2rem;display:block;" />\n')
        h1=re.search(r'(<h1[^>]*>.*?</h1>)',html,re.I|re.S)
        if h1: html=html[:h1.end()]+hero+html[h1.end():]
        else:
            art=re.search(r'(<(?:article|main|section)[^>]*>)',html,re.I)
            if art: html=html[:art.end()]+hero+html[art.end():]
    fp.write_text(html,encoding="utf-8")

def has_image(slug,html):
    if f"assets/images/blog/{slug}" in html: return True
    if "blog-hero-image" in html: return True
    for ext in [".webp",".jpg",".jpeg",".png"]:
        if (Path(OUT_DIR)/f"{slug}{ext}").exists(): return True
    return False

# ── GIT ──────────────────────────────────────────
def git(cmd): subprocess.run(cmd,shell=True,check=False,capture_output=True)
def setup_git():
    git('git config user.name "NeuraPlusAI Bot"')
    git('git config user.email "github-actions[bot]@users.noreply.github.com"')
def commit(msg):
    git(f'git add "{OUT_DIR}/" "{BLOG_DIR}/"')
    r=subprocess.run("git diff --cached --quiet",shell=True)
    if r.returncode!=0:
        git(f'git commit -m "auto: {msg} [skip ci]"')
        git("git fetch origin")
        git("git rebase origin/main 2>/dev/null || git rebase origin/master 2>/dev/null || true")
        git("git push origin HEAD:main 2>/dev/null || git push origin HEAD:master 2>/dev/null || true")
        print(f"  💾 Committed: {msg}")

# ── MAIN ─────────────────────────────────────────
def main():
    setup_git()
    mode="replace" if (len(sys.argv)>1 and sys.argv[1]=="replace") else "missing"
    blog_path=Path(BLOG_DIR)
    if not blog_path.exists():
        print(f"❌ {BLOG_DIR}/ not found. Run from repo root."); return
    posts=sorted([f for f in blog_path.glob("*.html")
                  if not any(f.stem.lower().startswith(s) for s in SKIP)])
    if mode=="missing":
        todo=[(f,f.stem) for f in posts
              if not has_image(f.stem,f.read_text(encoding="utf-8",errors="ignore"))]
        skipped=len(posts)-len(todo)
    else:
        todo=[(f,f.stem) for f in posts]
        skipped=0
    print(f"\n{'═'*58}")
    print(f"  NeuraPlusAI Image Generator")
    print(f"  Mode: {'REPLACE ALL' if mode=='replace' else 'MISSING ONLY'}")
    print(f"{'═'*58}")
    print(f"  Total posts : {len(posts)}")
    if mode=="missing": print(f"  Skipping    : {skipped} (already have images)")
    print(f"  To generate : {len(todo)}")
    print(f"{'═'*58}\n")
    if not todo:
        print("  🎉 All posts already have images!\n"); return
    ok=fail=0
    for i,(fp,slug) in enumerate(todo,1):
        html=fp.read_text(encoding="utf-8",errors="ignore")
        title=get_title(html,slug)
        print(f"[{i:02d}/{len(todo)}] {slug}")
        print(f"  📝 {title}")
        try:
            out,kb=generate(slug,title); inject(fp,slug,title)
            print(f"  ✅ {kb}KB\n"); ok+=1
            if ok%COMMIT_EVERY==0: commit(f"batch {ok} images")
        except Exception as e:
            print(f"  ❌ {e}\n"); fail+=1
    if ok>0: commit(f"generated {ok} images ({mode})")
    print(f"{'═'*58}")
    print(f"  ✅ Generated: {ok}  ❌ Failed: {fail}")
    print(f"  📁 {OUT_DIR}/")
    print(f"{'═'*58}\n")

if __name__=="__main__":
    main()
