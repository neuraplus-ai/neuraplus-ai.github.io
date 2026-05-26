#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  NeuraPulse — ENTERPRISE INJECTION SYSTEM v5.0 FINAL FIXED     ║
║  All bugs fixed · Safe · Idempotent · Works locally + CI       ║
╚══════════════════════════════════════════════════════════════════╝

FIXES vs previous versions:
  - No f-string inside f-string (caused SyntaxError on some Python)
  - GitHub Action uses plain git push (no ad-m action = no token issues)
  - Regex patterns use raw strings correctly
  - footer/nav regex limit raised (handles large footers)
  - All old broken workflows disabled automatically
  - Card injector runs if present
  - Safe on re-run (markers checked before every injection)

DROP IN REPO ROOT → python neurapulse_enterprise.py
"""

import os, re, json, datetime
from pathlib import Path

# ══════════════════════════════════════════════════════
# CONFIG — edit your real values here
# ══════════════════════════════════════════════════════
CFG = {
    "site":           "https://neuraplus-ai.github.io",
    "brand":          "NeuraPulse",
    "author":         "Prashant Lalwani",
    "description":    "Expert AI guides, tools, and analysis — making artificial intelligence understandable and actionable.",
    "logo":           "https://neuraplus-ai.github.io/assets/images/logo.png",
    "twitter_handle": "@AiNeuraplus",
    "social": {
        "twitter":   "https://x.com/AiNeuraplus",
        "instagram": "https://www.instagram.com/neuraplus.ai/",
        "linkedin":  "https://www.linkedin.com/in/prashant-lalwani-361010407/",
        "youtube":   "https://www.youtube.com/channel/UC0-7t4itquvY3ed2tGKLjQA",
        "facebook":  "https://www.facebook.com/profile.php?id=61589600083095",
        "pinterest": "https://pinterest.com/neuraplus_ai",
    },
    "nav": [
        ("Home",    "index.html"),
        ("Blog",    "blog.html"),
        ("Guide",   "guide.html"),
        ("About",   "about.html"),
        ("Contact", "contact.html"),
    ],
    "topics": [
        "Kimi AI","ChatGPT","Claude AI","Gemini AI","Groq AI",
        "AI Advertising","AI Automation","Prompt Engineering",
        "AI SEO","AI Tools","LLM","Perplexity AI","Ollama",
        "n8n Automation","AI Coding","Free AI Tools",
    ],
    "topic_links": {
        "Kimi AI":            "blog/kimi-ai-chatbot.html",
        "ChatGPT":            "blog/will-chatgpt-show-ads-2026.html",
        "Gemini AI":          "blog/future-of-ai-2026.html",
        "AI Automation":      "blog/best-ai-tool-email-writing.html",
        "Prompt Engineering": "guide.html",
        "AI Tools":           "blog.html",
        "AI SEO":             "guide.html",
        "LLM":                "blog.html",
    },
}

ROOT  = Path(".").resolve()
SITE  = CFG["site"]
NOW   = datetime.datetime.utcnow()
TODAY = NOW.strftime("%Y-%m-%d")
YEAR  = NOW.year

SKIP_DIRS  = {".git", "node_modules", ".github", "assets", "schema", "scripts"}
SKIP_FILES = {
    "neurapulse_enterprise.py", "neurapulse_card_injector.py",
    "master_inject.py", "seo_engine.py", "safe_footer_inject.py",
    "fix_footer_social.py", "add_guide_nav.py",
}

log_lines = []
def L(msg):
    print(msg)
    log_lines.append(str(msg))

# ── HELPERS ──────────────────────────────────────────────────
def get_files():
    out = []
    for p in sorted(ROOT.rglob("*.html")):
        parts = p.relative_to(ROOT).parts
        if any(x in SKIP_DIRS for x in parts): continue
        if p.name in SKIP_FILES: continue
        out.append(p)
    return out

def depth(p):
    return len(p.relative_to(ROOT).parts) - 1

def rp(p, href):
    if href.startswith("http"): return href
    return ("../" * depth(p)) + href.lstrip("/")

def url_of(p):
    rel = p.relative_to(ROOT).as_posix()
    return SITE + "/" + (rel if rel != "index.html" else "")

def page_title(p):
    try:
        html = p.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if m:
            t = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            return t.split('–')[0].split('—')[0].split('|')[0].strip()
    except:
        pass
    return p.stem.replace("-", " ").replace("_", " ").title()

def marked(html, marker):
    return marker in html

# ══════════════════════════════════════════════════════
# SVG ICONS (reused in nav + footer)
# ══════════════════════════════════════════════════════
ICON_X       = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'
ICON_IG      = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>'
ICON_LI      = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
ICON_YT      = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
ICON_FB      = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>'
ICON_PIN     = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/></svg>'

# ══════════════════════════════════════════════════════
# SYSTEM 1+2 — NAV + MOBILE HAMBURGER
# ══════════════════════════════════════════════════════
NAV_CSS = """\
<style id="np-nav-css">
*{box-sizing:border-box;}
#np-nav{position:sticky;top:0;z-index:500;display:flex;align-items:center;
  justify-content:space-between;padding:0 5%;height:64px;
  background:rgba(8,12,18,.95);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid rgba(0,212,255,.12);
  font-family:'DM Sans','Space Grotesk',system-ui,sans-serif;}
.np-logo{font-weight:800;font-size:1.18rem;color:#fff;display:flex;align-items:center;
  gap:8px;text-decoration:none;letter-spacing:-.02em;}
.np-logo-dot{width:8px;height:8px;background:#00d4ff;border-radius:50%;
  box-shadow:0 0 10px #00d4ff;animation:npblink 2s ease infinite;flex-shrink:0;}
@keyframes npblink{0%,100%{transform:scale(1);opacity:1;}50%{transform:scale(1.5);opacity:.7;}}
.np-links{display:flex;gap:26px;align-items:center;}
.np-links a{color:#8899aa;text-decoration:none;font-size:.84rem;letter-spacing:.07em;
  text-transform:uppercase;transition:color .2s;position:relative;}
.np-links a::after{content:'';position:absolute;bottom:-4px;left:0;right:0;height:1px;
  background:#00d4ff;transform:scaleX(0);transition:transform .25s;}
.np-links a:hover,.np-links a.np-active{color:#00d4ff;}
.np-links a:hover::after,.np-links a.np-active::after{transform:scaleX(1);}
.np-sub-btn{background:#00d4ff;color:#000!important;font-weight:700;font-size:.78rem;
  letter-spacing:.07em;text-transform:uppercase;padding:8px 18px;border-radius:5px;
  text-decoration:none;transition:box-shadow .2s,transform .2s;white-space:nowrap;}
.np-sub-btn:hover{box-shadow:0 0 22px #00d4ff;transform:translateY(-1px);}
.np-ham{display:none;flex-direction:column;gap:5px;cursor:pointer;
  padding:7px;background:transparent;border:none;margin-left:8px;}
.np-ham span{display:block;width:24px;height:2px;background:#8899aa;
  border-radius:2px;transition:all .3s;}
.np-ham.open span:nth-child(1){transform:translateY(7px) rotate(45deg);}
.np-ham.open span:nth-child(2){opacity:0;}
.np-ham.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg);}
#np-mob{display:none;position:fixed;top:64px;left:0;right:0;bottom:0;
  background:rgba(8,12,18,.98);padding:20px 5% 32px;flex-direction:column;
  gap:2px;z-index:499;overflow-y:auto;}
#np-mob.open{display:flex;}
#np-mob a{color:#8899aa;text-decoration:none;font-size:.95rem;letter-spacing:.07em;
  text-transform:uppercase;padding:14px 0;
  border-bottom:1px solid rgba(0,212,255,.07);transition:color .2s;display:block;}
#np-mob a:hover,#np-mob a.np-active{color:#00d4ff;}
.np-mob-social{display:flex;gap:10px;flex-wrap:wrap;padding:20px 0 0;border-bottom:none!important;}
.np-mob-social a{border-bottom:none!important;padding:0!important;width:40px;height:40px;
  border-radius:8px;background:#111827;border:1px solid rgba(0,212,255,.15)!important;
  display:flex!important;align-items:center;justify-content:center;color:#8899aa;transition:all .2s;}
.np-mob-social a:hover{border-color:#00d4ff!important;color:#00d4ff;}
.np-mob-social svg{width:17px;height:17px;}
.np-mob-cta{background:#00d4ff!important;color:#000!important;font-weight:700;
  text-align:center;border-radius:6px;margin-top:12px;padding:14px!important;
  border-bottom:none!important;letter-spacing:.07em;}
@media(max-width:768px){.np-links{display:none;}.np-ham{display:flex;}}
@media(min-width:769px){#np-mob{display:none!important;}}
</style>"""

def build_nav(p):
    fname = p.name
    s = CFG["social"]

    # Nav links
    links = ""
    for name, href in CFG["nav"]:
        active = ' class="np-active"' if fname == href else ""
        links += '<a href="{href}"{active}>{name}</a>\n    '.format(
            href=rp(p, href), active=active, name=name)

    # Mobile links
    mob_links = ""
    for name, href in CFG["nav"]:
        active = ' class="np-active"' if fname == href else ""
        mob_links += '  <a href="{href}"{active}>{name}</a>\n'.format(
            href=rp(p, href), active=active, name=name)

    # Mobile social icons
    mob_social = (
        '<div class="np-mob-social">'
        '<a href="{tw}" target="_blank" rel="noopener" aria-label="X">{ix}</a>'
        '<a href="{ig}" target="_blank" rel="noopener" aria-label="Instagram">{ii}</a>'
        '<a href="{yt}" target="_blank" rel="noopener" aria-label="YouTube">{iy}</a>'
        '<a href="{li}" target="_blank" rel="noopener" aria-label="LinkedIn">{il}</a>'
        '<a href="{fb}" target="_blank" rel="noopener" aria-label="Facebook">{if_}</a>'
        '<a href="{pi}" target="_blank" rel="noopener" aria-label="Pinterest">{ip}</a>'
        '</div>'
    ).format(
        tw=s["twitter"], ig=s["instagram"], yt=s["youtube"],
        li=s["linkedin"], fb=s["facebook"], pi=s["pinterest"],
        ix=ICON_X, ii=ICON_IG, iy=ICON_YT, il=ICON_LI, if_=ICON_FB, ip=ICON_PIN,
    )

    # JS for hamburger
    nav_js = (
        "<script>\n"
        "function npMenu(btn){\n"
        "  btn.classList.toggle('open');\n"
        "  btn.setAttribute('aria-expanded', btn.classList.contains('open'));\n"
        "  document.getElementById('np-mob').classList.toggle('open');\n"
        "  document.body.style.overflow = btn.classList.contains('open') ? 'hidden' : '';\n"
        "}\n"
        "document.addEventListener('keydown', function(e){\n"
        "  if(e.key==='Escape'){\n"
        "    var b=document.getElementById('np-ham-btn');\n"
        "    if(b && b.classList.contains('open')) npMenu(b);\n"
        "  }\n"
        "});\n"
        "document.addEventListener('click', function(e){\n"
        "  var b=document.getElementById('np-ham-btn'), m=document.getElementById('np-mob');\n"
        "  if(b && m && b.classList.contains('open') && !b.contains(e.target) && !m.contains(e.target)) npMenu(b);\n"
        "});\n"
        "</script>"
    )

    return (
        "<!-- NP:NAV -->\n"
        + NAV_CSS + "\n"
        + '<nav id="np-nav" role="navigation" aria-label="Main navigation">\n'
        + '  <a href="{logo_href}" class="np-logo" aria-label="{brand} Home">\n'.format(
            logo_href=rp(p, "index.html"), brand=CFG["brand"])
        + '    <span class="np-logo-dot" aria-hidden="true"></span>{brand}\n  </a>\n'.format(brand=CFG["brand"])
        + '  <div class="np-links">\n    '
        + links
        + '<a href="{contact}" class="np-sub-btn">Subscribe</a>\n  </div>\n'.format(contact=rp(p, "contact.html"))
        + '  <button class="np-ham" id="np-ham-btn" aria-label="Open menu" aria-expanded="false" aria-controls="np-mob" onclick="npMenu(this)">'
        + '<span></span><span></span><span></span></button>\n</nav>\n'
        + '<div id="np-mob" role="dialog" aria-label="Mobile navigation">\n'
        + mob_links
        + "  " + mob_social + "\n"
        + '  <a href="{contact}" class="np-mob-cta">Subscribe Free &rarr;</a>\n</div>\n'.format(contact=rp(p, "contact.html"))
        + nav_js + "\n"
        + "<!-- /NP:NAV -->"
    )

# ══════════════════════════════════════════════════════
# SYSTEM 3+4 — FOOTER + SOCIAL (6 icons)
# ══════════════════════════════════════════════════════
FOOTER_CSS = """\
<style id="np-footer-css">
#np-footer{position:relative;z-index:1;background:#0d1117;
  border-top:1px solid rgba(0,212,255,.12);padding:64px 5% 0;
  font-family:'DM Sans','Space Grotesk',system-ui,sans-serif;}
#np-footer::before{content:'';position:absolute;inset:0;
  background-image:linear-gradient(rgba(0,212,255,.012) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,212,255,.012) 1px,transparent 1px);
  background-size:54px 54px;pointer-events:none;}
.np-fg{max-width:1100px;margin:0 auto;display:grid;
  grid-template-columns:2fr 1fr 1fr 1fr;gap:44px;padding-bottom:48px;
  border-bottom:1px solid rgba(0,212,255,.1);position:relative;z-index:1;}
.np-fb-logo{font-weight:800;font-size:1.12rem;color:#fff;display:inline-flex;
  align-items:center;gap:8px;text-decoration:none;margin-bottom:14px;}
.np-fb-dot{width:8px;height:8px;background:#00d4ff;border-radius:50%;
  box-shadow:0 0 10px #00d4ff;animation:npblink 2s ease infinite;flex-shrink:0;}
.np-fb-desc{color:#8899aa;font-size:.85rem;line-height:1.75;
  max-width:260px;margin-bottom:22px;}
.np-soc{display:flex;gap:9px;flex-wrap:wrap;}
.np-si{width:40px;height:40px;border-radius:8px;
  border:1px solid rgba(0,212,255,.13);display:flex;align-items:center;
  justify-content:center;color:#8899aa;text-decoration:none;
  transition:all .25s;background:#111827;}
.np-si:hover{border-color:#00d4ff;color:#00d4ff;
  transform:translateY(-3px);box-shadow:0 0 14px rgba(0,212,255,.25);}
.np-si.ig:hover{border-color:#e1306c;color:#e1306c;}
.np-si.fb:hover{border-color:#1877f2;color:#1877f2;}
.np-si.pin:hover{border-color:#e60023;color:#e60023;}
.np-si svg{width:17px;height:17px;}
.np-fcol h4{font-size:.8rem;font-weight:700;color:#fff;letter-spacing:.09em;
  text-transform:uppercase;margin-bottom:16px;}
.np-fcol ul{list-style:none;padding:0;margin:0;}
.np-fcol ul li{margin-bottom:10px;}
.np-fcol ul li a{color:#8899aa;text-decoration:none;font-size:.86rem;
  transition:color .2s,padding-left .18s;display:inline-block;}
.np-fcol ul li a:hover{color:#00d4ff;padding-left:5px;}
.np-fbot{max-width:1100px;margin:0 auto;padding:22px 0 28px;
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:12px;position:relative;z-index:1;}
.np-fcopy{color:#556677;font-size:.78rem;}
.np-flinks{display:flex;gap:20px;flex-wrap:wrap;}
.np-flinks a{color:#556677;font-size:.78rem;text-decoration:none;transition:color .2s;}
.np-flinks a:hover{color:#00d4ff;}
.np-fbadge{display:inline-flex;align-items:center;gap:6px;
  background:rgba(0,212,255,.07);border:1px solid rgba(0,212,255,.15);
  border-radius:20px;padding:4px 13px;font-size:.7rem;color:#00d4ff;}
.np-fbadge::before{content:'';width:5px;height:5px;background:#00ffb3;
  border-radius:50%;animation:npblink 2s ease infinite;}
@media(max-width:900px){.np-fg{grid-template-columns:1fr 1fr;}}
@media(max-width:540px){.np-fg{grid-template-columns:1fr;}
  .np-fbot{flex-direction:column;text-align:center;}}
</style>"""

def build_footer(p):
    s = CFG["social"]
    def l(h): return rp(p, h)

    social_icons = (
        '<div class="np-soc">'
        '<a href="{tw}" target="_blank" rel="noopener" class="np-si" aria-label="X/Twitter">{ix}</a>'
        '<a href="{ig}" target="_blank" rel="noopener" class="np-si ig" aria-label="Instagram">{ii}</a>'
        '<a href="{li}" target="_blank" rel="noopener" class="np-si" aria-label="LinkedIn">{il}</a>'
        '<a href="{yt}" target="_blank" rel="noopener" class="np-si" aria-label="YouTube">{iy}</a>'
        '<a href="{fb}" target="_blank" rel="noopener" class="np-si fb" aria-label="Facebook">{if_}</a>'
        '<a href="{pi}" target="_blank" rel="noopener" class="np-si pin" aria-label="Pinterest">{ip}</a>'
        '</div>'
    ).format(
        tw=s["twitter"], ig=s["instagram"], li=s["linkedin"],
        yt=s["youtube"], fb=s["facebook"], pi=s["pinterest"],
        ix=ICON_X, ii=ICON_IG, il=ICON_LI, iy=ICON_YT, if_=ICON_FB, ip=ICON_PIN,
    )

    brand_block = (
        '<div>\n'
        '<a href="{home}" class="np-fb-logo">'
        '<span class="np-fb-dot"></span>{brand}</a>\n'
        '<p class="np-fb-desc">{desc}</p>\n'
        '{social}\n</div>\n'
    ).format(home=l("index.html"), brand=CFG["brand"],
             desc=CFG["description"], social=social_icons)

    col_guides = (
        '<div class="np-fcol"><h4>Guides &amp; Topics</h4><ul>'
        '<li><a href="{g}">AI Guides Hub</a></li>'
        '<li><a href="{b}">AI SEO &amp; GEO</a></li>'
        '<li><a href="{b}">AI Advertising</a></li>'
        '<li><a href="{b}">AI Automation</a></li>'
        '<li><a href="{b}">Prompt Engineering</a></li>'
        '<li><a href="{b}">AI Marketing</a></li>'
        '</ul></div>\n'
    ).format(g=l("guide.html"), b=l("blog.html"))

    col_company = (
        '<div class="np-fcol"><h4>Company</h4><ul>'
        '<li><a href="{a}">About NeuraPulse</a></li>'
        '<li><a href="{c}">Contact</a></li>'
        '<li><a href="{c}">Write for Us</a></li>'
        '<li><a href="{c}">Privacy Policy</a></li>'
        '<li><a href="{c}">Terms</a></li>'
        '<li><a href="{sm}">Sitemap</a></li>'
        '</ul></div>\n'
    ).format(a=l("about.html"), c=l("contact.html"), sm=l("sitemap.html"))

    col_news = (
        '<div class="np-fcol"><h4>Newsletter</h4><ul>'
        '<li><a href="{c}">Subscribe Free &rarr;</a></li>'
        '<li><a href="{c}">Weekly AI Updates</a></li>'
        '<li><a href="{b}">Latest Articles</a></li>'
        '<li><a href="{g}">Free Guides</a></li>'
        '<li><a href="{b}">AI Tool Reviews</a></li>'
        '</ul>'
        '<div style="margin-top:16px;padding:14px;background:rgba(0,212,255,.05);'
        'border:1px solid rgba(0,212,255,.15);border-radius:8px;">'
        '<p style="color:#8899aa;font-size:.78rem;margin-bottom:10px;">Join 4,200+ AI readers</p>'
        '<a href="{c}" style="display:block;background:#00d4ff;color:#000;text-align:center;'
        'padding:9px;border-radius:5px;font-size:.78rem;font-weight:700;text-decoration:none;'
        'letter-spacing:.06em;text-transform:uppercase;">Subscribe Free</a>'
        '</div></div>\n'
    ).format(c=l("contact.html"), b=l("blog.html"), g=l("guide.html"))

    bottom = (
        '<div class="np-fbot">'
        '<p class="np-fcopy">&copy; {yr} {brand} &middot; {author} &middot; All rights reserved</p>'
        '<div class="np-flinks">'
        '<a href="{sm}">Sitemap</a>'
        '<a href="{c}">Privacy</a>'
        '<a href="{c}">Terms</a>'
        '<a href="{c}">Cookie Policy</a>'
        '</div>'
        '<div class="np-fbadge">Live &middot; AI-Powered &middot; {today}</div>'
        '</div>\n'
    ).format(yr=YEAR, brand=CFG["brand"], author=CFG["author"],
             sm=l("sitemap.html"), c=l("contact.html"), today=TODAY)

    return (
        "<!-- NP:FOOTER -->\n"
        + FOOTER_CSS + "\n"
        + '<footer id="np-footer">\n'
        + '  <div class="np-fg">\n'
        + brand_block
        + col_guides + col_company + col_news
        + '  </div>\n'
        + bottom
        + '</footer>\n'
        + "<!-- /NP:FOOTER -->"
    )

# ══════════════════════════════════════════════════════
# SYSTEM 5 — BROKEN LINK REPAIR
# ══════════════════════════════════════════════════════
def fix_links(html, p):
    orig = html
    # Fix logo href="#"
    html = re.sub(
        r'(class="[^"]*(?:nav-logo|np-logo)[^"]*"[^>]*)href="#"',
        lambda m: m.group(0).replace('href="#"', 'href="{}"'.format(rp(p, "index.html"))),
        html
    )
    # Fix empty href
    html = re.sub(r'\bhref=""\b', 'href="#"', html)
    # Fix missing .html
    html = re.sub(r'href="(about|contact|blog|guide|index)"(?![./])', r'href="\1.html"', html)
    return html, html != orig

# ══════════════════════════════════════════════════════
# SYSTEM 6 — INTERNAL LINKING
# ══════════════════════════════════════════════════════
def inject_internal_links(html, p):
    if marked(html, "np-ilink"): return html, False
    body_m = re.search(r'<(?:article|main)[^>]*>[\s\S]*?</(?:article|main)>', html, re.IGNORECASE)
    if not body_m: return html, False
    body = body_m.group(0)
    new_body = body
    for topic, href in CFG["topic_links"].items():
        target = rp(p, href)
        if target in html: continue
        pat = r'(<p[^>]*>(?:(?!</?a[ >]).)*?)\b(' + re.escape(topic) + r')\b'
        rep = r'\1<a href="' + target + r'" class="np-ilink" title="' + topic + r' - NeuraPulse">\2</a>'
        result = re.sub(pat, rep, new_body, count=1, flags=re.IGNORECASE | re.DOTALL)
        if result != new_body:
            new_body = result
    if new_body != body:
        html = html.replace(body, new_body, 1)
        return html, True
    return html, False

# ══════════════════════════════════════════════════════
# SYSTEM 7 — READING PROGRESS BAR + REVEAL
# ══════════════════════════════════════════════════════
ENGAGE_HTML = (
    "<!-- NP:ENGAGE -->\n"
    "<style>#np-rbar{position:fixed;top:0;left:0;right:0;height:3px;z-index:9999;"
    "background:rgba(0,212,255,.15);}"
    "#np-rfill{height:100%;width:0;background:linear-gradient(90deg,#00d4ff,#00ffb3,#00d4ff);"
    "background-size:200%;animation:npShimmer 2s linear infinite;transition:width .1s;}"
    "@keyframes npShimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}"
    "</style>\n"
    "<div id=\"np-rbar\"><div id=\"np-rfill\"></div></div>\n"
    "<script>(function(){\n"
    "  window.addEventListener('scroll',function(){\n"
    "    var h=document.body.scrollHeight-window.innerHeight;\n"
    "    var el=document.getElementById('np-rfill');\n"
    "    if(el)el.style.width=(h>0?Math.min(window.scrollY/h*100,100):0)+'%';\n"
    "  });\n"
    "  var obs=new IntersectionObserver(function(e){e.forEach(function(x){\n"
    "    if(x.isIntersecting){x.target.style.opacity='1';x.target.style.transform='translateY(0)';}\n"
    "  });},{threshold:.08});\n"
    "  document.querySelectorAll('.np-reveal').forEach(function(el){\n"
    "    el.style.opacity='0';el.style.transform='translateY(22px)';\n"
    "    el.style.transition='opacity .6s ease,transform .6s ease';obs.observe(el);\n"
    "  });\n"
    "})();</script>\n"
    "<!-- /NP:ENGAGE -->"
)

# ══════════════════════════════════════════════════════
# SYSTEM 8 — META / SCHEMA / OG INJECTION
# ══════════════════════════════════════════════════════
def inject_meta(html, p):
    if marked(html, "np:meta"): return html, False
    title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else page_title(p)
    desc_m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', html, re.IGNORECASE)
    desc = desc_m.group(1) if desc_m else CFG["description"]
    url = url_of(p)
    mod = datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
    is_blog = "blog" in str(p.relative_to(ROOT))

    schema = json.dumps([
        {"@context": "https://schema.org", "@type": "Organization",
         "@id": SITE + "/#organization", "name": CFG["brand"], "url": SITE,
         "sameAs": list(CFG["social"].values())},
        {"@context": "https://schema.org",
         "@type": "Article" if is_blog else "WebPage",
         "@id": url + "#article", "url": url, "headline": title,
         "description": desc, "dateModified": mod, "datePublished": mod,
         "author": {"@type": "Person", "name": CFG["author"]},
         "publisher": {"@id": SITE + "/#organization"}, "inLanguage": "en"},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
             {"@type": "ListItem", "position": 2, "name": title, "item": url}
         ]}
    ], separators=(',', ':'))

    safe_title = title.replace('"', '&quot;')
    safe_desc  = desc.replace('"', '&quot;')[:155]

    block = (
        "<!-- np:meta -->\n"
        '<link rel="canonical" href="{url}"/>\n'
        '<meta property="og:title" content="{title}"/>\n'
        '<meta property="og:description" content="{desc}"/>\n'
        '<meta property="og:url" content="{url}"/>\n'
        '<meta property="og:type" content="{otype}"/>\n'
        '<meta property="og:site_name" content="{brand}"/>\n'
        '<meta property="og:image" content="{logo}"/>\n'
        '<meta name="twitter:card" content="summary_large_image"/>\n'
        '<meta name="twitter:site" content="{tw}"/>\n'
        '<meta name="twitter:title" content="{title}"/>\n'
        '<meta name="twitter:description" content="{desc}"/>\n'
        '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"/>\n'
        '<meta name="author" content="{author}"/>\n'
        '<link rel="alternate" type="application/rss+xml" title="{brand} RSS" href="{site}/rss.xml"/>\n'
        '<script type="application/ld+json">{schema}</script>\n'
        "<!-- /np:meta -->"
    ).format(
        url=url, title=safe_title, desc=safe_desc,
        otype="article" if is_blog else "website",
        brand=CFG["brand"], logo=CFG["logo"], tw=CFG["twitter_handle"],
        author=CFG["author"], site=SITE, schema=schema
    )

    if "</head>" in html:
        html = html.replace("</head>", block + "\n</head>", 1)
        return html, True
    return html, False

# ══════════════════════════════════════════════════════
# SYSTEM 9 — GEO / AI VISIBILITY TAGS
# ══════════════════════════════════════════════════════
GEO_BLOCK = (
    "<!-- NP:GEO -->\n"
    '<meta name="category" content="Artificial Intelligence, Technology, AI Tools"/>\n'
    '<meta name="classification" content="AI Technology"/>\n'
    '<meta name="subject" content="Artificial Intelligence, AI Tools, Machine Learning"/>\n'
    '<meta name="coverage" content="Worldwide"/>\n'
    '<meta name="revisit-after" content="7 days"/>\n'
    '<meta name="language" content="English"/>\n'
    "<!-- /NP:GEO -->"
)

# ══════════════════════════════════════════════════════
# SYSTEM 10 — ANALYTICS
# ══════════════════════════════════════════════════════
ANALYTICS_BLOCK = (
    "<!-- NP:ANALYTICS -->\n<script>\n"
    "(function(){\n"
    "  var d=[25,50,75,90,100],f={};\n"
    "  window.addEventListener('scroll',function(){\n"
    "    var p=Math.round((window.scrollY/(document.body.scrollHeight-window.innerHeight))*100);\n"
    "    d.forEach(function(x){if(p>=x&&!f[x]){f[x]=true;\n"
    "      if(window.gtag)gtag('event','scroll_depth',{event_category:'engagement',value:x});}});\n"
    "  });\n"
    "  var s=Date.now();\n"
    "  window.addEventListener('beforeunload',function(){\n"
    "    var t=Math.round((Date.now()-s)/1000);\n"
    "    if(window.gtag)gtag('event','time_on_page',{event_category:'engagement',value:t});\n"
    "  });\n"
    "})();\n</script>\n<!-- /NP:ANALYTICS -->"
)

# ══════════════════════════════════════════════════════
# SYSTEM 13 — SEO FILES
# ══════════════════════════════════════════════════════
def generate_seo_files(files):
    # robots.txt
    robots = (
        "User-agent: *\nAllow: /\nDisallow: /*.py$\n\n"
        "User-agent: GPTBot\nAllow: /\n\n"
        "User-agent: Google-Extended\nAllow: /\n\n"
        "User-agent: ClaudeBot\nAllow: /\n\n"
        "User-agent: PerplexityBot\nAllow: /\n\n"
        "User-agent: anthropic-ai\nAllow: /\n\n"
        "Sitemap: {site}/sitemap.xml\n"
    ).format(site=SITE)
    (ROOT / "robots.txt").write_text(robots)

    # sitemap.xml
    items = []
    for f in files:
        u = url_of(f)
        mod = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        d = depth(f)
        pri = "1.0" if f.name == "index.html" and d == 0 else ("0.9" if d == 0 else "0.8")
        frq = "daily" if d == 0 else "weekly"
        items.append("  <url><loc>{u}</loc><lastmod>{mod}</lastmod>"
                     "<changefreq>{frq}</changefreq><priority>{pri}</priority></url>".format(
                         u=u, mod=mod, frq=frq, pri=pri))
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(items) + "\n</urlset>")
    (ROOT / "sitemap.xml").write_text(sitemap)

    # llms.txt
    topics  = "\n".join("- " + t for t in CFG["topics"])
    socials = "\n".join("- {k}: {v}".format(k=k.title(), v=v) for k, v in CFG["social"].items())
    llms = (
        "# {brand} - LLMs.txt\n"
        "> AI-focused media platform publishing expert guides and analysis.\n\n"
        "## About\n- Website: {site}\n- Author: {author}\n- Updated: {today}\n\n"
        "## Topics\n{topics}\n\n"
        "## Permissions\nai-indexing: allowed\nai-training: allowed\nai-citations: allowed\n\n"
        "## Social\n{socials}\n\n"
        "## Sitemap\n{site}/sitemap.xml\n"
    ).format(brand=CFG["brand"], site=SITE, author=CFG["author"],
             today=TODAY, topics=topics, socials=socials)
    (ROOT / "llms.txt").write_text(llms)

    # ai.txt
    (ROOT / "ai.txt").write_text(
        "ai-indexing: allowed\nai-training: allowed\nai-citations: allowed\n"
        "cite-as: {brand}\ncite-url: {site}\nlast-updated: {today}\n".format(
            brand=CFG["brand"], site=SITE, today=TODAY)
    )

    # rss.xml
    rss_items = ""
    for f in files[:40]:
        u = url_of(f)
        t = page_title(f)
        mod = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%a, %d %b %Y 00:00:00 +0000")
        rss_items += (
            "  <item><title><![CDATA[{t}]]></title>"
            "<link>{u}</link><guid isPermaLink=\"true\">{u}</guid>"
            "<pubDate>{mod}</pubDate></item>\n"
        ).format(t=t, u=u, mod=mod)
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n'
        '  <title>{brand}</title>\n  <link>{site}</link>\n  <description>{desc}</description>\n'
        '{items}</channel>\n</rss>'
    ).format(brand=CFG["brand"], site=SITE, desc=CFG["description"], items=rss_items)
    (ROOT / "rss.xml").write_text(rss)

    L("  OK  robots.txt + sitemap.xml + llms.txt + ai.txt + rss.xml")

# ══════════════════════════════════════════════════════
# SYSTEM 12 — GITHUB ACTIONS (FULLY FIXED)
# ══════════════════════════════════════════════════════
def generate_github_action():
    gha_dir = ROOT / ".github" / "workflows"
    gha_dir.mkdir(parents=True, exist_ok=True)

    # Disable any old broken workflows that reference deleted scripts
    broken_scripts = ["seo_engine.py", "master_inject.py", "safe_footer_inject.py",
                      "fix_footer_social.py", "add_guide_nav.py"]
    for wf in gha_dir.glob("*.yml"):
        if wf.name == "neurapulse-enterprise.yml":
            continue
        try:
            content = wf.read_text()
            if any(s in content for s in broken_scripts):
                wf.rename(wf.with_suffix(".yml.disabled"))
                L("  DISABLED broken workflow: " + wf.name)
        except:
            pass

    # Write the correct workflow
    # NOTE: no f-strings here to avoid confusion, plain .format()
    yml = (
        "# NeuraPulse Enterprise SEO — auto-runs on every push\n"
        "name: NeuraPulse Enterprise SEO\n\n"
        "on:\n"
        "  push:\n"
        "    branches: [ main, master ]\n"
        "  schedule:\n"
        "    - cron: '0 2 * * 0'\n"
        "  workflow_dispatch:\n\n"
        "permissions:\n"
        "  contents: write\n\n"
        "jobs:\n"
        "  inject:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n\n"
        "      - name: Checkout\n"
        "        uses: actions/checkout@v4\n"
        "        with:\n"
        "          fetch-depth: 0\n"
        "          token: ${{ secrets.GITHUB_TOKEN }}\n\n"
        "      - name: Setup Python\n"
        "        uses: actions/setup-python@v5\n"
        "        with:\n"
        "          python-version: '3.11'\n\n"
        "      - name: Run Enterprise Injection\n"
        "        run: python neurapulse_enterprise.py\n\n"
        "      - name: Run Card Injector (if present)\n"
        "        run: |\n"
        "          if [ -f neurapulse_card_injector.py ]; then\n"
        "            python neurapulse_card_injector.py\n"
        "          fi\n\n"
        "      - name: Commit and Push Changes\n"
        "        run: |\n"
        "          git config user.email \"bot@neurapulse.ai\"\n"
        "          git config user.name \"NeuraPulse SEO Bot\"\n"
        "          git add -A\n"
        "          git diff --staged --quiet && echo 'Nothing to commit' || "
        "git commit -m '[bot] Enterprise: nav+footer+seo+social [skip ci]'\n"
        "          git push origin HEAD\n"
    )
    (gha_dir / "neurapulse-enterprise.yml").write_text(yml)
    L("  OK  .github/workflows/neurapulse-enterprise.yml written")

# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
def main():
    files = get_files()
    L("\n" + "=" * 58)
    L("  NeuraPulse Enterprise System v5.0 FINAL FIXED")
    L("  {} HTML files found".format(len(files)))
    L("=" * 58 + "\n")

    c = dict(nav=0, footer=0, meta=0, links=0,
             engage=0, geo=0, broken=0, analytics=0, skip=0)

    for f in files:
        try:
            html = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            L("  ERROR reading {}: {}".format(f.name, e))
            continue

        changed = False

        # 5. Fix broken links first
        html, lc = fix_links(html, f)
        if lc: c["broken"] += 1; changed = True

        # 8. Meta / schema
        if not marked(html, "np:meta"):
            html, mc = inject_meta(html, f)
            if mc: c["meta"] += 1; changed = True

        # 9. GEO tags
        if "NP:GEO" not in html and "<head>" in html:
            html = html.replace("<head>", "<head>\n" + GEO_BLOCK, 1)
            c["geo"] += 1; changed = True

        # 7. Engagement bar
        if "NP:ENGAGE" not in html and "</body>" in html:
            html = html.replace("</body>", ENGAGE_HTML + "\n</body>", 1)
            c["engage"] += 1; changed = True

        # 10. Analytics
        if "NP:ANALYTICS" not in html and "</body>" in html:
            html = html.replace("</body>", ANALYTICS_BLOCK + "\n</body>", 1)
            c["analytics"] += 1; changed = True

        # 1+2. Nav + mobile hamburger
        if "NP:NAV" not in html:
            nav_html = build_nav(f)
            nav_pat = re.compile(r'<nav[\s\S]{0,3000}?</nav>', re.IGNORECASE)
            if nav_pat.search(html):
                html = nav_pat.sub(nav_html, html, count=1)
            elif re.search(r'<body[^>]*>', html, re.IGNORECASE):
                html = re.sub(r'(<body[^>]*>)', r'\1\n' + nav_html, html, count=1, flags=re.IGNORECASE)
            c["nav"] += 1; changed = True

        # 3+4. Footer + social (6 icons)
        if "NP:FOOTER" not in html:
            foot_html = build_footer(f)
            foot_pat = re.compile(r'<footer[\s\S]{0,8000}?</footer>', re.IGNORECASE)
            if foot_pat.search(html):
                html = foot_pat.sub(foot_html, html, count=1)
            elif "</body>" in html:
                html = html.replace("</body>", foot_html + "\n</body>", 1)
            else:
                html += foot_html
            c["footer"] += 1; changed = True

        # 6. Internal links
        html, ic = inject_internal_links(html, f)
        if ic: c["links"] += 1; changed = True

        if changed:
            try:
                f.write_text(html, encoding="utf-8")
            except Exception as e:
                L("  ERROR writing {}: {}".format(f.name, e))
        else:
            c["skip"] += 1

    # SEO files
    L("\n  Generating SEO files...")
    generate_seo_files(files)

    # GitHub Action
    L("\n  Writing GitHub Action workflow...")
    generate_github_action()

    # Save log
    try:
        (ROOT / "enterprise-run-log.txt").write_text("\n".join(log_lines))
    except:
        pass

    L("\n" + "=" * 58)
    L("  DONE — Summary")
    L("  NAV injected          : {}".format(c["nav"]))
    L("  FOOTER injected       : {}".format(c["footer"]))
    L("  META/SCHEMA injected  : {}".format(c["meta"]))
    L("  GEO tags injected     : {}".format(c["geo"]))
    L("  ENGAGEMENT injected   : {}".format(c["engage"]))
    L("  ANALYTICS injected    : {}".format(c["analytics"]))
    L("  INTERNAL LINKS added  : {}".format(c["links"]))
    L("  BROKEN LINKS fixed    : {}".format(c["broken"]))
    L("  ALREADY UP TO DATE    : {}".format(c["skip"]))
    L("  Total HTML files      : {}".format(len(files)))
    L("=" * 58)
    L("\n  NEXT:\n  git add .\n  git commit -m 'Enterprise v5 final'\n  git push\n")

if __name__ == "__main__":
    main()
