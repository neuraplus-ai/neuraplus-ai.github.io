#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║      NeuraPulse — SEO Engine v2.1                               ║
║      Fixes black pages · Nav · Footer · Schema · Sitemap HTML   ║
╚══════════════════════════════════════════════════════════════════╝
DROP IN REPO ROOT AND RUN:  python seo_engine.py
"""

import os, re, json, datetime
from pathlib import Path
from html.parser import HTMLParser

# ══════════════════════════════════════════════════════
# CONFIG
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
    "skip_dirs":  {".git", "node_modules", ".github", "assets", "schema", "scripts", "_cleanup_backup"},
    "skip_files": {"seo_engine.py", "neurapulse_cleanup.py", "neurapulse_enterprise.py",
                   "neurapulse_card_injector.py", "master_inject.py", "np-restore.py"},
    "topics": [
        "Kimi AI", "ChatGPT", "Claude AI", "Gemini AI", "Groq AI",
        "AI Advertising", "AI Automation", "Prompt Engineering",
        "AI SEO", "AI Tools", "LLM", "Perplexity AI", "Ollama",
        "n8n Automation", "AI Coding", "Free AI Tools",
    ],
}

SITE  = CFG["site"]
ROOT  = Path(".").resolve()
NOW   = datetime.datetime.utcnow()
TODAY = NOW.strftime("%Y-%m-%d")
TS    = NOW.strftime("%Y-%m-%dT%H:%M:%SZ")
YEAR  = NOW.year

logs = []
def log(msg, tag="INFO"):
    line = f"[{tag}] {msg}"
    print(line)
    logs.append(line)

# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════
def get_files():
    out = []
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if any(x in CFG["skip_dirs"] for x in rel.parts): continue
        if p.name in CFG["skip_files"]: continue
        out.append(p)
    return out

def url_for(path):
    rel = path.relative_to(ROOT).as_posix()
    return SITE + "/" + rel if rel != "index.html" else SITE + "/"

def depth(path):
    return len(path.relative_to(ROOT).parts) - 1

def rp(path, target):
    if target.startswith("http"): return target
    d = depth(path)
    return ("../" * d) + target.lstrip("/")

def page_title(path):
    """Extract clean title from filename for sitemap display."""
    name = path.stem.replace("-", " ").replace("_", " ").title()
    parts = path.relative_to(ROOT).parts
    if len(parts) > 1:
        section = parts[0].replace("-", " ").replace("_", " ").title()
        return f"{name} — {section}"
    return name

def get_category(path):
    """Determine page category from path."""
    parts = path.relative_to(ROOT).parts
    if len(parts) == 1:
        name = path.stem.lower()
        if name == "index": return "Home"
        if name == "blog": return "Blog"
        if name == "guide": return "Guide"
        if name == "about": return "About"
        if name == "contact": return "Contact"
        return "Page"
    folder = parts[0].lower()
    if folder == "blog": return "Blog Article"
    if folder == "guide": return "Guide Article"
    return folder.title()

# ══════════════════════════════════════════════════════
# SOCIAL ICONS
# ══════════════════════════════════════════════════════
ICON_X   = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'
ICON_IG  = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>'
ICON_LI  = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
ICON_YT  = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
ICON_FB  = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>'
ICON_PIN = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/></svg>'

# ══════════════════════════════════════════════════════
# NAV
# ══════════════════════════════════════════════════════
NAV_CSS = """\
<style id="np-nav-css">
*{box-sizing:border-box;}
#np-nav{position:sticky;top:0;z-index:500;display:flex;align-items:center;
  justify-content:space-between;padding:0 5%;height:64px;
  background:rgba(8,12,18,.97);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
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
.np-mob-cta{background:#00d4ff!important;color:#000!important;font-weight:700;
  text-align:center;border-radius:6px;margin-top:12px;padding:14px!important;
  border-bottom:none!important;letter-spacing:.07em;}
@media(max-width:768px){.np-links{display:none;}.np-ham{display:flex;}}
@media(min-width:769px){#np-mob{display:none!important;}}
</style>"""

def build_nav(path):
    fname = path.name
    links = ""
    mob_links = ""
    for name, href in CFG["nav"]:
        active = ' class="np-active"' if fname == href else ""
        links     += f'<a href="{rp(path, href)}"{active}>{name}</a>\n    '
        mob_links += f'  <a href="{rp(path, href)}"{active}>{name}</a>\n'

    nav_js = (
        "<script>\n"
        "function npMenu(btn){\n"
        "  btn.classList.toggle('open');\n"
        "  btn.setAttribute('aria-expanded',btn.classList.contains('open'));\n"
        "  document.getElementById('np-mob').classList.toggle('open');\n"
        "  document.body.style.overflow=btn.classList.contains('open')?'hidden':'';\n"
        "}\n"
        "document.addEventListener('keydown',function(e){\n"
        "  if(e.key==='Escape'){var b=document.getElementById('np-ham-btn');\n"
        "  if(b&&b.classList.contains('open'))npMenu(b);}\n"
        "});\n"
        "document.addEventListener('click',function(e){\n"
        "  var b=document.getElementById('np-ham-btn'),m=document.getElementById('np-mob');\n"
        "  if(b&&m&&b.classList.contains('open')&&!b.contains(e.target)&&!m.contains(e.target))npMenu(b);\n"
        "});\n"
        "</script>"
    )

    return (
        "<!-- NP:NAV -->\n"
        + NAV_CSS + "\n"
        + '<nav id="np-nav" role="navigation" aria-label="Main navigation">\n'
        + f'  <a href="{rp(path,"index.html")}" class="np-logo" aria-label="{CFG["brand"]} Home">\n'
        + f'    <span class="np-logo-dot" aria-hidden="true"></span>{CFG["brand"]}\n  </a>\n'
        + '  <div class="np-links">\n    '
        + links
        + f'<a href="{rp(path,"contact.html")}" class="np-sub-btn">Subscribe</a>\n  </div>\n'
        + '  <button class="np-ham" id="np-ham-btn" aria-label="Open menu" aria-expanded="false" '
        + 'aria-controls="np-mob" onclick="npMenu(this)">'
        + '<span></span><span></span><span></span></button>\n</nav>\n'
        + '<div id="np-mob" role="dialog" aria-label="Mobile navigation">\n'
        + mob_links
        + f'  <a href="{rp(path,"contact.html")}" class="np-mob-cta">Subscribe Free &rarr;</a>\n</div>\n'
        + nav_js + "\n"
        + "<!-- /NP:NAV -->"
    )

# ══════════════════════════════════════════════════════
# FOOTER
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
.np-fb-desc{color:#8899aa;font-size:.85rem;line-height:1.75;max-width:260px;margin-bottom:22px;}
.np-soc{display:flex;gap:9px;flex-wrap:wrap;}
.np-si{width:40px;height:40px;border-radius:8px;border:1px solid rgba(0,212,255,.13);
  display:flex;align-items:center;justify-content:center;color:#8899aa;
  text-decoration:none;transition:all .25s;background:#111827;}
.np-si:hover{border-color:#00d4ff;color:#00d4ff;transform:translateY(-3px);}
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

def build_footer(path):
    s = CFG["social"]
    social_icons = (
        '<div class="np-soc">'
        f'<a href="{s["twitter"]}" target="_blank" rel="noopener" class="np-si" aria-label="X">{ICON_X}</a>'
        f'<a href="{s["instagram"]}" target="_blank" rel="noopener" class="np-si ig" aria-label="Instagram">{ICON_IG}</a>'
        f'<a href="{s["linkedin"]}" target="_blank" rel="noopener" class="np-si" aria-label="LinkedIn">{ICON_LI}</a>'
        f'<a href="{s["youtube"]}" target="_blank" rel="noopener" class="np-si" aria-label="YouTube">{ICON_YT}</a>'
        f'<a href="{s["facebook"]}" target="_blank" rel="noopener" class="np-si fb" aria-label="Facebook">{ICON_FB}</a>'
        f'<a href="{s["pinterest"]}" target="_blank" rel="noopener" class="np-si pin" aria-label="Pinterest">{ICON_PIN}</a>'
        '</div>'
    )
    brand_block = (
        '<div>\n'
        f'<a href="{rp(path,"index.html")}" class="np-fb-logo"><span class="np-fb-dot"></span>{CFG["brand"]}</a>\n'
        f'<p class="np-fb-desc">{CFG["description"]}</p>\n'
        f'{social_icons}\n</div>\n'
    )
    col_guides = (
        '<div class="np-fcol"><h4>Guides &amp; Topics</h4><ul>'
        f'<li><a href="{rp(path,"guide.html")}">AI Guides Hub</a></li>'
        f'<li><a href="{rp(path,"blog.html")}">AI SEO &amp; GEO</a></li>'
        f'<li><a href="{rp(path,"blog.html")}">AI Advertising</a></li>'
        f'<li><a href="{rp(path,"blog.html")}">AI Automation</a></li>'
        f'<li><a href="{rp(path,"blog.html")}">Prompt Engineering</a></li>'
        f'<li><a href="{rp(path,"blog.html")}">AI Marketing</a></li>'
        '</ul></div>\n'
    )
    col_company = (
        '<div class="np-fcol"><h4>Company</h4><ul>'
        f'<li><a href="{rp(path,"about.html")}">About NeuraPulse</a></li>'
        f'<li><a href="{rp(path,"contact.html")}">Contact</a></li>'
        f'<li><a href="{rp(path,"contact.html")}">Write for Us</a></li>'
        f'<li><a href="{rp(path,"contact.html")}">Privacy Policy</a></li>'
        f'<li><a href="{rp(path,"contact.html")}">Terms</a></li>'
        f'<li><a href="{rp(path,"sitemap.html")}">Sitemap</a></li>'
        '</ul></div>\n'
    )
    col_news = (
        '<div class="np-fcol"><h4>Newsletter</h4><ul>'
        f'<li><a href="{rp(path,"contact.html")}">Subscribe Free &rarr;</a></li>'
        f'<li><a href="{rp(path,"contact.html")}">Weekly AI Updates</a></li>'
        f'<li><a href="{rp(path,"blog.html")}">Latest Articles</a></li>'
        f'<li><a href="{rp(path,"guide.html")}">Free Guides</a></li>'
        f'<li><a href="{rp(path,"blog.html")}">AI Tool Reviews</a></li>'
        '</ul>'
        '<div style="margin-top:16px;padding:14px;background:rgba(0,212,255,.05);'
        'border:1px solid rgba(0,212,255,.15);border-radius:8px;">'
        '<p style="color:#8899aa;font-size:.78rem;margin-bottom:10px;">Join 4,200+ AI readers</p>'
        f'<a href="{rp(path,"contact.html")}" style="display:block;background:#00d4ff;color:#000;'
        'text-align:center;padding:9px;border-radius:5px;font-size:.78rem;font-weight:700;'
        'text-decoration:none;letter-spacing:.06em;text-transform:uppercase;">Subscribe Free</a>'
        '</div></div>\n'
    )
    bottom = (
        '<div class="np-fbot">'
        f'<p class="np-fcopy">&copy; {YEAR} {CFG["brand"]} &middot; {CFG["author"]} &middot; All rights reserved</p>'
        '<div class="np-flinks">'
        f'<a href="{rp(path,"sitemap.html")}">Sitemap</a>'
        f'<a href="{rp(path,"contact.html")}">Privacy</a>'
        f'<a href="{rp(path,"contact.html")}">Terms</a>'
        f'<a href="{rp(path,"contact.html")}">Cookie Policy</a>'
        '</div>'
        f'<div class="np-fbadge">Live &middot; AI-Powered &middot; {TODAY}</div>'
        '</div>\n'
    )
    return (
        "<!-- NP:FOOTER -->\n"
        + FOOTER_CSS + "\n"
        + '<footer id="np-footer">\n'
        + '  <div class="np-fg">\n'
        + brand_block + col_guides + col_company + col_news
        + '  </div>\n'
        + bottom
        + '</footer>\n'
        + "<!-- /NP:FOOTER -->"
    )

# ══════════════════════════════════════════════════════
# META PARSER
# ══════════════════════════════════════════════════════
class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title=""; self.desc=""; self.canon=""
        self.og_title=""; self.og_image=""; self.schema=False
        self.h1s=[]; self._in_title=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="title": self._in_title=True
        if tag=="meta":
            n=a.get("name","").lower(); pr=a.get("property","").lower()
            if n=="description": self.desc=a.get("content","")
            if pr=="og:title": self.og_title=a.get("content","")
            if pr=="og:image": self.og_image=a.get("content","")
        if tag=="link" and a.get("rel")=="canonical": self.canon=a.get("href","")
        if tag=="script" and a.get("type")=="application/ld+json": self.schema=True
        if tag=="h1": self.h1s.append("")
    def handle_endtag(self, tag):
        if tag=="title": self._in_title=False
    def handle_data(self, data):
        if self._in_title: self.title+=data

# FADE FIX
FADE_FIX = """<style>.fade,.fade.vis{opacity:1!important;transform:translateY(0)!important;}</style>"""

# ══════════════════════════════════════════════════════
# PHASE 1 — NAV + FOOTER + FADE FIX
# ══════════════════════════════════════════════════════
def phase1_nav_footer(files):
    log("="*55, "")
    log("PHASE 1 — NAV + FOOTER + FADE FIX", "PHASE")
    log("="*55, "")
    nav_added=nav_skip=footer_added=footer_skip=fade_fixed=0

    for f in files:
        try: html=f.read_text(encoding="utf-8",errors="ignore")
        except: continue
        changed=False

        if 'class="fade"' in html or "class='fade'" in html:
            if 'opacity:1!important;transform:translateY(0)!important' not in html:
                if "</head>" in html:
                    html=html.replace("</head>", FADE_FIX+"\n</head>",1)
                    changed=True; fade_fixed+=1

        has_real_nav=bool(re.search(r'<nav\b[^>]*>',html,re.IGNORECASE))
        if not has_real_nav:
            nav_html=build_nav(f)
            body_match=re.search(r'<body[^>]*>',html,re.IGNORECASE)
            if body_match:
                pos=body_match.end()
                html=html[:pos]+"\n"+nav_html+"\n"+html[pos:]
            elif "</head>" in html:
                html=html.replace("</head>","</head>\n"+nav_html,1)
            changed=True; nav_added+=1
        else:
            nav_skip+=1

        has_np_footer='id="np-footer"' in html
        has_orig_footer=bool(re.search(r'<footer\b',html,re.IGNORECASE))
        if has_np_footer:
            footer_skip+=1
        elif has_orig_footer:
            footer_skip+=1
        else:
            footer_html=build_footer(f)
            if "</body>" in html:
                html=html.replace("</body>",footer_html+"\n</body>",1)
            else:
                html+="\n"+footer_html
            changed=True; footer_added+=1

        if changed:
            f.write_text(html,encoding="utf-8")

    log(f"Fade fix    : {fade_fixed} pages")
    log(f"Nav added   : {nav_added} · skipped: {nav_skip}")
    log(f"Footer added: {footer_added} · skipped: {footer_skip}")

# ══════════════════════════════════════════════════════
# PHASE 2 — SEO META + SCHEMA
# ══════════════════════════════════════════════════════
ORG_SCHEMA = {
    "@context":"https://schema.org","@type":"Organization",
    "@id":SITE+"/#organization","name":CFG["brand"],"url":SITE,
    "logo":{"@type":"ImageObject","url":CFG["logo"],"width":200,"height":60},
    "description":CFG["description"],"foundingDate":"2025",
    "founder":{"@type":"Person","name":CFG["author"],"url":SITE+"/about.html"},
    "sameAs":list(CFG["social"].values()),"knowsAbout":CFG["topics"]
}
WEBSITE_SCHEMA = {
    "@context":"https://schema.org","@type":"WebSite",
    "@id":SITE+"/#website","url":SITE,"name":CFG["brand"],
    "description":CFG["description"],"publisher":{"@id":SITE+"/#organization"},
    "inLanguage":"en","potentialAction":{
        "@type":"SearchAction",
        "target":{"@type":"EntryPoint","urlTemplate":SITE+"/blog.html?q={search_term_string}"},
        "query-input":"required name=search_term_string"
    }
}

def phase2_seo_meta(files):
    log("="*55,"")
    log("PHASE 2 — SEO META + SCHEMA","PHASE")
    log("="*55,"")
    updated=0
    for f in files:
        try: html=f.read_text(encoding="utf-8",errors="ignore")
        except: continue
        p=MetaParser()
        try: p.feed(html)
        except: pass
        title=p.title.strip() or (f.stem.replace("-"," ").replace("_"," ").title()+" – "+CFG["brand"])
        desc=p.desc or CFG["description"]
        url=url_for(f)
        inject=[]
        if not p.canon:
            inject.append(f'<link rel="canonical" href="{url}"/>')
        if not p.og_title:
            inject+=[
                f'<meta property="og:title" content="{title}"/>',
                f'<meta property="og:description" content="{desc}"/>',
                f'<meta property="og:url" content="{url}"/>',
                f'<meta property="og:type" content="article"/>',
                f'<meta property="og:site_name" content="{CFG["brand"]}"/>',
                f'<meta property="og:image" content="{CFG["logo"]}"/>',
                f'<meta name="twitter:card" content="summary_large_image"/>',
                f'<meta name="twitter:site" content="{CFG["twitter_handle"]}"/>',
                f'<meta name="twitter:title" content="{title}"/>',
                f'<meta name="twitter:description" content="{desc}"/>',
                f'<meta name="twitter:image" content="{CFG["logo"]}"/>',
            ]
        if not p.schema:
            rel=str(f.relative_to(ROOT))
            mod=datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
            slug=f.stem.replace("-"," ").replace("_"," ").title()
            is_blog="blog" in rel.lower()
            schema_list=[ORG_SCHEMA,WEBSITE_SCHEMA,{
                "@context":"https://schema.org",
                "@type":"Article" if is_blog else "WebPage",
                "@id":url+"#article","url":url,
                "headline":title or slug,"description":desc,
                "dateModified":mod,"datePublished":mod,
                "author":{"@type":"Person","name":CFG["author"],"url":SITE+"/about.html"},
                "publisher":{"@id":SITE+"/#organization"},
                "mainEntityOfPage":{"@type":"WebPage","@id":url},
                "inLanguage":"en","image":{"@type":"ImageObject","url":CFG["logo"]}
            }]
            inject.append(f'<script type="application/ld+json">\n{json.dumps(schema_list,indent=2)}\n</script>')
        if inject and "</head>" in html:
            html=html.replace("</head>","\n".join(inject)+"\n</head>",1)
            f.write_text(html,encoding="utf-8"); updated+=1
    log(f"SEO meta/schema injected: {updated} pages")

# ══════════════════════════════════════════════════════
# PHASE 3 — GEO/AEO TAGS
# ══════════════════════════════════════════════════════
def phase3_geo(files):
    log("="*55,""); log("PHASE 3 — GEO/AEO TAGS","PHASE"); log("="*55,"")
    updated=0
    geo_block=f"""<!-- NP:GEO -->
<meta name="author" content="{CFG["author"]}"/>
<meta name="publisher" content="{CFG["brand"]}"/>
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"/>
<meta name="googlebot" content="index, follow"/>
<meta name="bingbot" content="index, follow"/>
<meta name="rating" content="general"/>
<meta name="revisit-after" content="7 days"/>
<meta name="language" content="English"/>
<meta name="category" content="Artificial Intelligence, Technology, AI Tools"/>
<meta name="classification" content="AI Technology Blog"/>
<meta name="coverage" content="Worldwide"/>
<meta name="distribution" content="Global"/>
<meta name="target" content="all"/>
<link rel="alternate" type="application/rss+xml" title="{CFG["brand"]} RSS" href="{SITE}/rss.xml"/>
<!-- /NP:GEO -->"""
    for f in files:
        try: html=f.read_text(encoding="utf-8",errors="ignore")
        except: continue
        if "NP:GEO" in html: continue
        if "<head>" in html:
            html=html.replace("<head>","<head>\n"+geo_block,1)
            f.write_text(html,encoding="utf-8"); updated+=1
    log(f"GEO/AEO tags injected: {updated} pages")

# ══════════════════════════════════════════════════════
# PHASE 4 — TECHNICAL FILES
# ══════════════════════════════════════════════════════
def phase4_technical(files):
    log("="*55,""); log("PHASE 4 — TECHNICAL SEO FILES","PHASE"); log("="*55,"")

    (ROOT/"robots.txt").write_text(
        f"User-agent: *\nAllow: /\nDisallow: /seo-audit-report.json\nDisallow: /*.py$\n"
        f"User-agent: GPTBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\n"
        f"User-agent: Google-Extended\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\n"
        f"User-agent: anthropic-ai\nAllow: /\nSitemap: {SITE}/sitemap.xml\n"
    )

    xml_urls=[]
    for f in files:
        u=url_for(f)
        mod=datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        is_home=f.name=="index.html" and depth(f)==0
        priority="1.0" if is_home else ("0.9" if depth(f)==0 else "0.8")
        freq="daily" if is_home else ("weekly" if depth(f)==0 else "monthly")
        xml_urls.append(f"  <url><loc>{u}</loc><lastmod>{mod}</lastmod><changefreq>{freq}</changefreq><priority>{priority}</priority></url>")
    (ROOT/"sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        +"\n".join(xml_urls)+"\n</urlset>",encoding="utf-8")
    log(f"sitemap.xml — {len(files)} URLs")

    items=""
    for f in list(files)[:50]:
        u=url_for(f)
        mod=datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%a, %d %b %Y %H:%M:%S +0000")
        title=f.stem.replace("-"," ").replace("_"," ").title()
        items+=f'  <item><title>{title}</title><link>{u}</link><guid isPermaLink="true">{u}</guid><pubDate>{mod}</pubDate></item>\n'
    (ROOT/"rss.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        f'<channel>\n  <title>{CFG["brand"]}</title>\n  <link>{SITE}</link>\n'
        f'  <description>{CFG["description"]}</description>\n  <language>en</language>\n'
        f'  <atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/>\n'
        +items+"</channel>\n</rss>",encoding="utf-8")

    topics="\n".join(f"- {t}" for t in CFG["topics"])
    (ROOT/"llms.txt").write_text(
        f"# {CFG['brand']} — LLMs.txt\n> Founded by {CFG['author']} in 2025.\n"
        f"## About\n- Website: {SITE}\n- Author: {CFG['author']}\n- Updated: {TODAY}\n"
        f"## Topics\n{topics}\n## Permissions\n- AI training: allowed\n- AI indexing: allowed\n",
        encoding="utf-8")
    (ROOT/"ai.txt").write_text(
        f"# ai.txt\nai-indexing: allowed\nai-training: allowed\nai-citations: allowed\n"
        f"cite-as: {CFG['brand']}\ncite-author: {CFG['author']}\ncite-url: {SITE}\nlast-updated: {TODAY}\n",
        encoding="utf-8")
    log("robots.txt · sitemap.xml · rss.xml · llms.txt · ai.txt — done")

# ══════════════════════════════════════════════════════
# PHASE 5 — HTML SITEMAP (NEW — fully automated)
# ══════════════════════════════════════════════════════
def phase5_html_sitemap(files):
    log("="*55,""); log("PHASE 5 — HTML SITEMAP (AUTO)","PHASE"); log("="*55,"")

    # Group pages by category
    categories = {}
    for f in files:
        cat = get_category(f)
        if cat not in categories:
            categories[cat] = []
        u   = url_for(f)
        mod = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        title = page_title(f)
        categories[cat].append((title, u, mod))

    # Sort categories — Home first, then alphabetical
    order = ["Home", "Blog", "Guide", "About", "Contact", "Page"]
    sorted_cats = sorted(categories.keys(), key=lambda x: (order.index(x) if x in order else 99, x))

    # Build category sections
    sections = ""
    total = 0
    for cat in sorted_cats:
        pages = sorted(categories[cat], key=lambda x: x[0])
        total += len(pages)
        rows = ""
        for title, url, mod in pages:
            rows += f"""
            <tr>
              <td><a href="{url}" target="_blank">{title}</a></td>
              <td><span class="cat-badge">{cat}</span></td>
              <td>{mod}</td>
              <td><a href="{url}" target="_blank" class="visit-btn">Visit →</a></td>
            </tr>"""
        sections += f"""
        <div class="cat-section">
          <div class="cat-header">
            <h2>{cat}</h2>
            <span class="cat-count">{len(pages)} pages</span>
          </div>
          <table class="sitemap-table">
            <thead><tr><th>Page</th><th>Category</th><th>Last Updated</th><th></th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>"""

    html_sitemap = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Sitemap — {CFG["brand"]}</title>
<meta name="description" content="Complete HTML sitemap for {CFG["brand"]} — {total} pages indexed."/>
<meta name="robots" content="index,follow"/>
<link rel="canonical" href="{SITE}/sitemap.html"/>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Space+Mono:wght@400;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500&display=swap" rel="stylesheet"/>
<style>
:root{{--bg:#050810;--surface:#0c1120;--surface2:#111827;--border:#1e2d45;
  --accent:#00e5ff;--accent2:#7c3aed;--text:#e2e8f0;--text-dim:#64748b;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;
  font-size:15px;line-height:1.6;overflow-x:hidden;}}
::-webkit-scrollbar{{width:4px;}}
::-webkit-scrollbar-thumb{{background:var(--accent2);border-radius:2px;}}

/* NAV */
nav{{position:sticky;top:0;z-index:100;display:flex;align-items:center;
  justify-content:space-between;padding:0 5%;height:64px;
  background:rgba(5,8,16,.97);backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);}}
.nav-logo{{font-family:'Syne',sans-serif;font-weight:800;font-size:1.3rem;
  color:var(--text);text-decoration:none;display:flex;align-items:center;gap:8px;}}
.nav-dot{{width:8px;height:8px;border-radius:50%;background:var(--accent);
  box-shadow:0 0 8px var(--accent);animation:blink 2s ease infinite;}}
@keyframes blink{{0%,100%{{opacity:1;}}50%{{opacity:.4;}}}}
.nav-links{{display:flex;gap:1.5rem;}}
.nav-links a{{font-family:'Space Mono',monospace;font-size:.72rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--text-dim);text-decoration:none;transition:color .2s;}}
.nav-links a:hover{{color:var(--accent);}}

/* HERO */
.hero{{padding:5rem 5% 3rem;border-bottom:1px solid var(--border);}}
.hero-tag{{font-family:'Space Mono',monospace;font-size:.7rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--accent);margin-bottom:1rem;
  display:flex;align-items:center;gap:.75rem;}}
.hero-tag::before{{content:'';display:block;width:20px;height:1px;background:var(--accent);}}
.hero h1{{font-family:'Syne',sans-serif;font-weight:800;font-size:clamp(2rem,4vw,3rem);
  letter-spacing:-.03em;margin-bottom:.75rem;}}
.hero p{{color:var(--text-dim);max-width:500px;font-size:1rem;}}

/* STATS */
.stats-bar{{display:flex;gap:2rem;padding:2rem 5%;border-bottom:1px solid var(--border);
  flex-wrap:wrap;background:var(--surface);}}
.stat{{display:flex;flex-direction:column;gap:4px;}}
.stat-num{{font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;
  color:var(--accent);line-height:1;}}
.stat-label{{font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--text-dim);}}

/* SEARCH */
.search-wrap{{padding:2rem 5% 1rem;}}
.search-box{{display:flex;gap:.75rem;max-width:600px;}}
.search-input{{flex:1;background:var(--surface);border:1px solid var(--border);
  border-radius:8px;padding:.75rem 1.2rem;color:var(--text);font-family:'DM Sans',sans-serif;
  font-size:.9rem;outline:none;transition:border-color .2s;}}
.search-input:focus{{border-color:var(--accent);}}
.search-input::placeholder{{color:var(--text-dim);}}
.search-btn{{background:var(--accent);color:#000;font-family:'Space Mono',monospace;
  font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;padding:.75rem 1.5rem;
  border:none;border-radius:8px;cursor:pointer;font-weight:700;transition:box-shadow .2s;}}
.search-btn:hover{{box-shadow:0 0 20px rgba(0,229,255,.4);}}

/* CONTENT */
.content{{padding:1.5rem 5% 4rem;}}
.cat-section{{margin-bottom:3rem;}}
.cat-header{{display:flex;align-items:center;gap:1rem;margin-bottom:1rem;
  padding-bottom:.75rem;border-bottom:1px solid var(--border);}}
.cat-header h2{{font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;color:var(--text);}}
.cat-count{{font-family:'Space Mono',monospace;font-size:.65rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--accent);background:rgba(0,229,255,.08);
  border:1px solid rgba(0,229,255,.2);padding:.25rem .75rem;border-radius:100px;}}

/* TABLE */
.sitemap-table{{width:100%;border-collapse:collapse;font-size:.88rem;}}
.sitemap-table th{{font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--text-dim);padding:.65rem 1rem;
  border-bottom:2px solid var(--border);text-align:left;}}
.sitemap-table td{{padding:.75rem 1rem;border-bottom:1px solid var(--border);
  color:var(--text-dim);vertical-align:middle;}}
.sitemap-table tr:hover td{{background:var(--surface2);}}
.sitemap-table td:first-child a{{color:var(--text);text-decoration:none;
  transition:color .2s;font-weight:500;}}
.sitemap-table td:first-child a:hover{{color:var(--accent);}}
.cat-badge{{font-family:'Space Mono',monospace;font-size:.6rem;letter-spacing:.08em;
  text-transform:uppercase;padding:.2rem .6rem;border-radius:4px;
  background:rgba(0,229,255,.08);color:var(--accent);border:1px solid rgba(0,229,255,.15);
  white-space:nowrap;}}
.visit-btn{{font-family:'Space Mono',monospace;font-size:.65rem;letter-spacing:.06em;
  text-transform:uppercase;color:var(--accent);text-decoration:none;
  padding:.3rem .75rem;border:1px solid rgba(0,229,255,.25);border-radius:4px;
  transition:all .2s;white-space:nowrap;}}
.visit-btn:hover{{background:rgba(0,229,255,.1);border-color:var(--accent);}}

/* FOOTER */
.page-footer{{border-top:1px solid var(--border);padding:2rem 5%;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;}}
.page-footer span{{font-family:'Space Mono',monospace;font-size:.65rem;color:var(--text-dim);}}
.page-footer a{{color:var(--accent);text-decoration:none;}}

/* RESPONSIVE */
@media(max-width:768px){{
  .nav-links{{display:none;}}
  .stats-bar{{gap:1.5rem;}}
  .sitemap-table th:nth-child(2),.sitemap-table td:nth-child(2),
  .sitemap-table th:nth-child(3),.sitemap-table td:nth-child(3){{display:none;}}
}}
</style>
</head>
<body>

<nav>
  <a href="{SITE}/" class="nav-logo"><span class="nav-dot"></span>{CFG["brand"]}</a>
  <div class="nav-links">
    <a href="{SITE}/">Home</a>
    <a href="{SITE}/blog.html">Blog</a>
    <a href="{SITE}/guide.html">Guide</a>
    <a href="{SITE}/about.html">About</a>
    <a href="{SITE}/contact.html">Contact</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-tag">Complete Site Index</div>
  <h1>{CFG["brand"]} — HTML Sitemap</h1>
  <p>Every page on {CFG["brand"]} — updated automatically. {total} pages indexed as of {TODAY}.</p>
</div>

<div class="stats-bar">
  <div class="stat"><span class="stat-num">{total}</span><span class="stat-label">Total Pages</span></div>
  <div class="stat"><span class="stat-num">{len(categories)}</span><span class="stat-label">Categories</span></div>
  <div class="stat"><span class="stat-num">{TODAY}</span><span class="stat-label">Last Updated</span></div>
  <div class="stat"><span class="stat-num">Auto</span><span class="stat-label">Updated On Push</span></div>
</div>

<div class="search-wrap">
  <div class="search-box">
    <input type="text" class="search-input" id="siteSearch" placeholder="Search pages..." oninput="filterRows(this.value)"/>
    <button class="search-btn" onclick="filterRows(document.getElementById('siteSearch').value)">Search</button>
  </div>
</div>

<div class="content" id="sitemapContent">
  {sections}
</div>

<div class="page-footer">
  <span>&copy; {YEAR} {CFG["brand"]} &middot; {CFG["author"]}</span>
  <span>XML Sitemap: <a href="{SITE}/sitemap.xml">{SITE}/sitemap.xml</a></span>
  <span>Last updated: {TODAY}</span>
</div>

<script>
function filterRows(query) {{
  var q = query.toLowerCase().trim();
  var rows = document.querySelectorAll('.sitemap-table tbody tr');
  var sections = document.querySelectorAll('.cat-section');
  rows.forEach(function(row) {{
    var text = row.textContent.toLowerCase();
    row.style.display = (!q || text.includes(q)) ? '' : 'none';
  }});
  // Hide empty sections
  sections.forEach(function(sec) {{
    var visible = sec.querySelectorAll('tbody tr:not([style*="none"])').length;
    sec.style.display = visible > 0 ? '' : 'none';
  }});
}}
</script>

</body>
</html>"""

    (ROOT / "sitemap.html").write_text(html_sitemap, encoding="utf-8")
    log(f"sitemap.html generated — {total} pages across {len(categories)} categories")

# ══════════════════════════════════════════════════════
# PHASE 6 — ENTITY SCHEMA FILES
# ══════════════════════════════════════════════════════
def phase6_entity():
    log("="*55,""); log("PHASE 6 — ENTITY SCHEMA FILES","PHASE"); log("="*55,"")
    schema_dir=ROOT/"schema"
    schema_dir.mkdir(exist_ok=True)
    (schema_dir/"organization.json").write_text(json.dumps(ORG_SCHEMA,indent=2))
    (schema_dir/"website.json").write_text(json.dumps(WEBSITE_SCHEMA,indent=2))
    log("schema/organization.json + schema/website.json saved")

# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n"+"═"*58)
    print("  NeuraPulse SEO Engine v2.1")
    print(f"  Root : {ROOT}")
    print(f"  Time : {TS}")
    print("═"*58+"\n")

    files = get_files()
    log(f"Found {len(files)} HTML files")

    phase1_nav_footer(files)
    phase2_seo_meta(files)
    phase3_geo(files)
    phase4_technical(files)
    phase5_html_sitemap(files)
    phase6_entity()

    (ROOT/"seo-run-log.txt").write_text("\n".join(logs),encoding="utf-8")

    print("\n"+"═"*58)
    print("  ✅  ALL PHASES COMPLETE")
    print(f"  Pages processed: {len(files)}")
    print("═"*58)
    print("\n  FILES GENERATED:")
    print("  robots.txt · sitemap.xml · sitemap.html · rss.xml")
    print("  llms.txt · ai.txt · schema/*.json · seo-run-log.txt\n")
