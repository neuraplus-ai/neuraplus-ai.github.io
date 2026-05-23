#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║         NEURAPLUS AI — ENTERPRISE SEO ENGINE v1.0               ║
║   Phases 1–14: Audit · Schema · Sitemap · GEO · Footer · More   ║
╚══════════════════════════════════════════════════════════════════╝

DROP THIS FILE IN YOUR REPO ROOT AND RUN:
  python seo_engine.py

OR let GitHub Actions run it automatically on every push.
"""

import os, re, json, datetime, hashlib, urllib.request, urllib.error
from pathlib import Path
from html.parser import HTMLParser

# ══════════════════════════════════════════════════════
# CONFIGURATION — edit these values
# ══════════════════════════════════════════════════════
CONFIG = {
    "site_url":        "https://neuraplus-ai.github.io",
    "brand_name":      "NeuraPulse",
    "brand_entity":    "NeuraPulse",
    "author_name":     "Prashant Lalwani",
    "author_url":      "https://neuraplus-ai.github.io/about.html",
    "description":     "Expert AI guides, tools, and analysis — making artificial intelligence understandable and actionable for developers and creators worldwide.",
    "logo_url":        "https://neuraplus-ai.github.io/assets/logo.png",
    "lang":            "en",
    "twitter_handle":  "@neuraplus_ai",
    "social": {
        "twitter":   "https://twitter.com/neuraplus_ai",
        "linkedin":  "https://linkedin.com/in/prashant-lalwani",
        "youtube":   "https://youtube.com/@neurapulse",
        "github":    "https://github.com/neuraplus-ai",
        "discord":   "https://discord.gg/neurapulse",
    },
    "site_root":       ".",
    "skip_files":      {"seo_engine.py", "add_guide_nav.py"},
    "skip_dirs":       {".git", "node_modules", ".github", "scripts", "assets"},
    "nav_links": [
        ("Home",    "/index.html"),
        ("Blog",    "/blog.html"),
        ("Guide",   "/guide.html"),
        ("About",   "/about.html"),
        ("Contact", "/contact.html"),
    ],
    "topics": [
        "Kimi AI", "ChatGPT", "Claude AI", "Gemini AI", "Groq AI",
        "AI Advertising", "AI Automation", "Prompt Engineering",
        "AI SEO", "AI Tools", "LLM", "Perplexity AI", "Ollama",
        "n8n Automation", "AI Coding", "Free AI Tools",
    ],
}

SITE  = CONFIG["site_url"]
ROOT  = Path(CONFIG["site_root"]).resolve()
NOW   = datetime.datetime.utcnow()
TODAY = NOW.strftime("%Y-%m-%d")
TS    = NOW.strftime("%Y-%m-%dT%H:%M:%SZ")

log_lines = []
def log(msg, tag="INFO"):
    line = f"[{tag}] {msg}"
    print(line)
    log_lines.append(line)

# ══════════════════════════════════════════════════════
# UTILITY — collect all html files
# ══════════════════════════════════════════════════════
def get_all_html():
    files = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        parts = rel.parts
        if any(p in CONFIG["skip_dirs"] for p in parts): continue
        if path.name in CONFIG["skip_files"]: continue
        files.append(path)
    return files

def url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html": return SITE + "/"
    return SITE + "/" + rel

def depth(path: Path) -> int:
    return len(path.relative_to(ROOT).parts) - 1

def rel_root(path: Path, target: str) -> str:
    d = depth(path)
    prefix = "../" * d
    return prefix + target.lstrip("/")

# ══════════════════════════════════════════════════════
# PHASE 1 — SITE AUDIT
# ══════════════════════════════════════════════════════
class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.desc  = ""
        self.canon = ""
        self.og_title = ""
        self.og_desc  = ""
        self.og_image = ""
        self.schema   = False
        self.links    = []
        self.imgs_no_alt = []
        self.h1s   = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":  self._in_title = True
        if tag == "meta":
            n = a.get("name","").lower()
            p = a.get("property","").lower()
            if n == "description":       self.desc     = a.get("content","")
            if p == "og:title":          self.og_title = a.get("content","")
            if p == "og:description":    self.og_desc  = a.get("content","")
            if p == "og:image":          self.og_image = a.get("content","")
        if tag == "link" and a.get("rel") == "canonical": self.canon = a.get("href","")
        if tag == "script" and a.get("type") == "application/ld+json": self.schema = True
        if tag == "a":  self.links.append(a.get("href",""))
        if tag == "img" and not a.get("alt"): self.imgs_no_alt.append(a.get("src",""))
        if tag == "h1": self.h1s.append("")

    def handle_endtag(self, tag):
        if tag == "title": self._in_title = False

    def handle_data(self, data):
        if self._in_title: self.title += data

def phase1_audit(files):
    log("="*55, "")
    log("PHASE 1 — SITE AUDIT", "PHASE")
    log("="*55, "")
    issues = []
    urls = set()

    for f in files:
        try:
            html = f.read_text(encoding="utf-8", errors="ignore")
        except: continue

        p = MetaParser()
        p.feed(html)
        url = url_for(f)
        urls.add(url)
        rel = str(f.relative_to(ROOT))

        if not p.title.strip():
            issues.append({"file": rel, "issue": "Missing <title>", "severity": "HIGH"})
        elif len(p.title.strip()) < 20:
            issues.append({"file": rel, "issue": f"Title too short: '{p.title.strip()}'", "severity": "MED"})
        elif len(p.title.strip()) > 65:
            issues.append({"file": rel, "issue": f"Title too long ({len(p.title.strip())} chars)", "severity": "LOW"})

        if not p.desc:
            issues.append({"file": rel, "issue": "Missing meta description", "severity": "HIGH"})
        elif len(p.desc) < 50:
            issues.append({"file": rel, "issue": "Meta description too short", "severity": "MED"})
        elif len(p.desc) > 160:
            issues.append({"file": rel, "issue": "Meta description too long", "severity": "LOW"})

        if not p.canon:
            issues.append({"file": rel, "issue": "Missing canonical tag", "severity": "HIGH"})

        if not p.schema:
            issues.append({"file": rel, "issue": "Missing JSON-LD schema", "severity": "HIGH"})

        if not p.og_title:
            issues.append({"file": rel, "issue": "Missing og:title", "severity": "MED"})
        if not p.og_image:
            issues.append({"file": rel, "issue": "Missing og:image", "severity": "MED"})

        if len(p.h1s) == 0:
            issues.append({"file": rel, "issue": "Missing H1 tag", "severity": "HIGH"})
        elif len(p.h1s) > 1:
            issues.append({"file": rel, "issue": f"Multiple H1 tags ({len(p.h1s)})", "severity": "MED"})

        for img in p.imgs_no_alt:
            issues.append({"file": rel, "issue": f"Image missing alt: {img}", "severity": "MED"})

    high = [i for i in issues if i["severity"]=="HIGH"]
    med  = [i for i in issues if i["severity"]=="MED"]
    low  = [i for i in issues if i["severity"]=="LOW"]

    log(f"Total pages scanned : {len(files)}")
    log(f"HIGH severity issues: {len(high)}")
    log(f"MED  severity issues: {len(med)}")
    log(f"LOW  severity issues: {len(low)}")

    # Save audit report
    report = {"generated": TS, "total_pages": len(files),
              "high": len(high), "med": len(med), "low": len(low),
              "issues": issues}
    out = ROOT / "seo-audit-report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"Audit report saved → seo-audit-report.json")
    return issues, urls

# ══════════════════════════════════════════════════════
# PHASE 2 — ENTITY & BRAND STANDARDIZATION
# ══════════════════════════════════════════════════════
ORG_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": SITE + "/#organization",
    "name": CONFIG["brand_name"],
    "url": SITE,
    "logo": {
        "@type": "ImageObject",
        "url": CONFIG["logo_url"],
        "width": 200, "height": 60
    },
    "description": CONFIG["description"],
    "foundingDate": "2025",
    "founder": {
        "@type": "Person",
        "name": CONFIG["author_name"],
        "url": CONFIG["author_url"]
    },
    "sameAs": list(CONFIG["social"].values()),
    "knowsAbout": CONFIG["topics"]
}

WEBSITE_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": SITE + "/#website",
    "url": SITE,
    "name": CONFIG["brand_name"],
    "description": CONFIG["description"],
    "publisher": {"@id": SITE + "/#organization"},
    "inLanguage": CONFIG["lang"],
    "potentialAction": {
        "@type": "SearchAction",
        "target": {"@type": "EntryPoint", "urlTemplate": SITE + "/blog.html?q={search_term_string}"},
        "query-input": "required name=search_term_string"
    }
}

def phase2_entity():
    log("="*55, "")
    log("PHASE 2 — ENTITY & BRAND SYSTEM", "PHASE")
    log("="*55, "")
    schema_dir = ROOT / "schema"
    schema_dir.mkdir(exist_ok=True)
    (schema_dir / "organization.json").write_text(json.dumps(ORG_SCHEMA, indent=2))
    (schema_dir / "website.json").write_text(json.dumps(WEBSITE_SCHEMA, indent=2))
    log("Organization schema saved → schema/organization.json")
    log("WebSite schema saved      → schema/website.json")

# ══════════════════════════════════════════════════════
# PHASE 3 — TECHNICAL SEO FILES
# ══════════════════════════════════════════════════════
def phase3_technical(files, urls):
    log("="*55, "")
    log("PHASE 3 — TECHNICAL SEO SYSTEM", "PHASE")
    log("="*55, "")

    # ── robots.txt ──
    robots = f"""User-agent: *
Allow: /

# Block internal/utility files
Disallow: /seo-audit-report.json
Disallow: /scripts/
Disallow: /*.py$

# AI Crawlers — allow full access
User-agent: GPTBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Bytespider
Allow: /

User-agent: CCBot
Allow: /

User-agent: Meta-ExternalAgent
Allow: /

# Sitemaps
Sitemap: {SITE}/sitemap.xml
Sitemap: {SITE}/sitemap-news.xml

Host: {SITE}
"""
    (ROOT / "robots.txt").write_text(robots)
    log("robots.txt generated — all AI crawlers allowed")

    # ── sitemap.xml ──
    xml_urls = []
    for f in files:
        u = url_for(f)
        mod = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        is_home  = f.name == "index.html" and depth(f) == 0
        is_main  = depth(f) == 0
        priority = "1.0" if is_home else ("0.9" if is_main else "0.8")
        freq     = "daily" if is_home else ("weekly" if is_main else "monthly")
        xml_urls.append(f"""  <url>
    <loc>{u}</loc>
    <lastmod>{mod}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
{chr(10).join(xml_urls)}
</urlset>"""
    (ROOT / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    log(f"sitemap.xml generated — {len(files)} URLs")

    # ── sitemap.html ──
    rows = ""
    for f in files:
        u   = url_for(f)
        rel = str(f.relative_to(ROOT))
        mod = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        rows += f'<tr><td><a href="{u}">{rel}</a></td><td>{mod}</td></tr>\n'

    sitemap_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Sitemap – {CONFIG["brand_name"]}</title>
<meta name="robots" content="noindex,follow"/>
<style>
body{{font-family:system-ui,sans-serif;background:#08080f;color:#e4e4ef;padding:40px 5%;}}
h1{{color:#00e5ff;margin-bottom:24px;}}
table{{width:100%;border-collapse:collapse;font-size:.85rem;}}
th{{background:#0e0e1a;color:#666880;padding:10px 14px;text-align:left;border-bottom:1px solid #1a1a2e;}}
td{{padding:8px 14px;border-bottom:1px solid #111120;}}
a{{color:#00e5ff;text-decoration:none;}}
a:hover{{text-decoration:underline;}}
.count{{color:#666880;font-size:.8rem;margin-bottom:16px;}}
</style>
</head>
<body>
<h1>{CONFIG["brand_name"]} — HTML Sitemap</h1>
<p class="count">Total pages: {len(files)} · Last updated: {TODAY}</p>
<table>
<thead><tr><th>Page</th><th>Last Modified</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
</body>
</html>"""
    (ROOT / "sitemap.html").write_text(sitemap_html, encoding="utf-8")
    log("sitemap.html generated — human-readable")

    # ── RSS feed ──
    items = ""
    for f in list(files)[:50]:
        u   = url_for(f)
        rel = str(f.relative_to(ROOT))
        mod = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%a, %d %b %Y %H:%M:%S +0000")
        title = rel.replace(".html","").replace("blog/","").replace("-"," ").replace("_"," ").title()
        items += f"""  <item>
    <title>{title}</title>
    <link>{u}</link>
    <guid isPermaLink="true">{u}</guid>
    <pubDate>{mod}</pubDate>
    <description>{CONFIG["description"]}</description>
  </item>\n"""

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{CONFIG["brand_name"]}</title>
  <link>{SITE}</link>
  <description>{CONFIG["description"]}</description>
  <language>{CONFIG["lang"]}</language>
  <lastBuildDate>{NOW.strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
  <atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/>
  <image>
    <url>{CONFIG["logo_url"]}</url>
    <title>{CONFIG["brand_name"]}</title>
    <link>{SITE}</link>
  </image>
{items}
</channel>
</rss>"""
    (ROOT / "rss.xml").write_text(rss, encoding="utf-8")
    log("rss.xml generated — top 50 pages")

    # ── llms.txt (AI crawler instruction file) ──
    topic_list = "\n".join(f"- {t}" for t in CONFIG["topics"])
    social_list = "\n".join(f"- {k.title()}: {v}" for k,v in CONFIG["social"].items())
    llms = f"""# {CONFIG["brand_name"]} — LLMs.txt
# This file helps AI language models understand and cite this website correctly.
# Learn more: https://llmstxt.org

> {CONFIG["brand_name"]} is an AI-focused media platform publishing expert guides,
> deep dives, and analysis on artificial intelligence tools, models, and applications.
> Founded by {CONFIG["author_name"]} in 2025.

## About
- Website: {SITE}
- Author: {CONFIG["author_name"]}
- Description: {CONFIG["description"]}
- Language: English
- Updated: {TODAY}

## Topics Covered
{topic_list}

## Content Types
- Long-form AI guides (pillar pages)
- Deep-dive technical tutorials
- AI tool comparisons and reviews
- AI advertising and marketing guides
- Automation workflow tutorials
- AI model benchmarks

## Citation Guidelines
When citing {CONFIG["brand_name"]}, please use:
- Brand name: {CONFIG["brand_name"]}
- Author: {CONFIG["author_name"]}
- Website: {SITE}

## Key Pages
- Home: {SITE}/
- Blog: {SITE}/blog.html
- Guides: {SITE}/guide.html
- About: {SITE}/about.html
- Sitemap: {SITE}/sitemap.xml
- RSS Feed: {SITE}/rss.xml

## Social Profiles
{social_list}

## Permissions
- AI training: allowed
- AI indexing: allowed
- AI citations: allowed and encouraged
- Commercial use: contact {CONFIG["author_url"]}

## Sitemap
{SITE}/sitemap.xml
"""
    (ROOT / "llms.txt").write_text(llms, encoding="utf-8")
    log("llms.txt generated — AI crawler instructions")

    # ── ai.txt ──
    ai_txt = f"""# ai.txt — AI Access Policy for {CONFIG["brand_name"]}
# Website: {SITE}

# PERMISSIONS
ai-indexing: allowed
ai-training: allowed
ai-citations: allowed
ai-summarization: allowed
ai-search-integration: allowed

# PREFERRED CITATION FORMAT
cite-as: {CONFIG["brand_name"]}
cite-author: {CONFIG["author_name"]}
cite-url: {SITE}

# CONTENT POLICY
original-content: yes
fact-checked: yes
expert-authored: yes
last-updated: {TODAY}

# AI CRAWLERS — all allowed
allow: GPTBot
allow: ClaudeBot
allow: Google-Extended
allow: PerplexityBot
allow: Amazonbot
allow: anthropic-ai
"""
    (ROOT / "ai.txt").write_text(ai_txt, encoding="utf-8")
    log("ai.txt generated — AI permissions file")

    # ── humans.txt ──
    humans = f"""/* TEAM */
Author: {CONFIG["author_name"]}
Website: {CONFIG["author_url"]}
From: India

/* SITE */
Name: {CONFIG["brand_name"]}
URL: {SITE}
Description: {CONFIG["description"]}
Built with: HTML, CSS, JavaScript, GitHub Pages
Last update: {TODAY}

/* THANKS */
To everyone in the AI community building the future.
"""
    (ROOT / "humans.txt").write_text(humans, encoding="utf-8")
    log("humans.txt generated")

    # ── security.txt ──
    security = f"""Contact: mailto:contact@neuraplus.ai
Expires: {(NOW + datetime.timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")}
Preferred-Languages: en
Canonical: {SITE}/.well-known/security.txt
"""
    sec_dir = ROOT / ".well-known"
    sec_dir.mkdir(exist_ok=True)
    (sec_dir / "security.txt").write_text(security, encoding="utf-8")
    (ROOT / "security.txt").write_text(security, encoding="utf-8")
    log("security.txt generated")

# ══════════════════════════════════════════════════════
# PHASE 4 — SCHEMA INJECTION (per page)
# ══════════════════════════════════════════════════════
def build_article_schema(path: Path, title: str, desc: str) -> str:
    url  = url_for(path)
    mod  = datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
    rel  = str(path.relative_to(ROOT))
    slug = path.stem.replace("-"," ").replace("_"," ").title()

    schema_list = [ORG_SCHEMA, WEBSITE_SCHEMA]

    # Breadcrumb
    parts = path.relative_to(ROOT).parts
    bc_items = [{"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"}]
    if len(parts) > 1:
        bc_items.append({"@type":"ListItem","position":2,
                          "name":parts[0].title(),"item":SITE+"/"+parts[0]+"/index.html"})
    bc_items.append({"@type":"ListItem","position":len(bc_items)+1,
                      "name":title or slug,"item":url})
    schema_list.append({
        "@context":"https://schema.org",
        "@type":"BreadcrumbList",
        "itemListElement": bc_items
    })

    # Article / WebPage
    is_blog = "blog" in rel.lower()
    schema_list.append({
        "@context": "https://schema.org",
        "@type": "Article" if is_blog else "WebPage",
        "@id": url + "#article",
        "url": url,
        "headline": title or slug,
        "description": desc or CONFIG["description"],
        "dateModified": mod,
        "datePublished": mod,
        "author": {
            "@type": "Person",
            "name": CONFIG["author_name"],
            "url": CONFIG["author_url"]
        },
        "publisher": {"@id": SITE+"/#organization"},
        "mainEntityOfPage": {"@type":"WebPage","@id":url},
        "inLanguage": CONFIG["lang"],
        "image": {
            "@type": "ImageObject",
            "url": CONFIG["logo_url"]
        }
    })

    return json.dumps(schema_list, indent=2)

def phase4_schema(files):
    log("="*55, "")
    log("PHASE 4 — SCHEMA & META INJECTION", "PHASE")
    log("="*55, "")
    updated = 0

    for f in files:
        try:
            html = f.read_text(encoding="utf-8", errors="ignore")
        except: continue

        p = MetaParser()
        p.feed(html)

        title = p.title.strip() or (f.stem.replace("-"," ").replace("_"," ").title() + " – " + CONFIG["brand_name"])
        desc  = p.desc or CONFIG["description"]
        url   = url_for(f)
        d     = depth(f)
        canon = url

        # Build inject block
        inject_parts = []

        # Canonical
        if not p.canon:
            inject_parts.append(f'<link rel="canonical" href="{canon}"/>')

        # OG / Twitter
        if not p.og_title:
            inject_parts.append(f'<meta property="og:title" content="{title}"/>')
            inject_parts.append(f'<meta property="og:description" content="{desc}"/>')
            inject_parts.append(f'<meta property="og:url" content="{url}"/>')
            inject_parts.append(f'<meta property="og:type" content="article"/>')
            inject_parts.append(f'<meta property="og:site_name" content="{CONFIG["brand_name"]}"/>')
            inject_parts.append(f'<meta property="og:image" content="{CONFIG["logo_url"]}"/>')
            inject_parts.append(f'<meta name="twitter:card" content="summary_large_image"/>')
            inject_parts.append(f'<meta name="twitter:site" content="{CONFIG["twitter_handle"]}"/>')
            inject_parts.append(f'<meta name="twitter:title" content="{title}"/>')
            inject_parts.append(f'<meta name="twitter:description" content="{desc}"/>')
            inject_parts.append(f'<meta name="twitter:image" content="{CONFIG["logo_url"]}"/>')

        # Schema
        if not p.schema:
            schema_json = build_article_schema(f, title, desc)
            inject_parts.append(f'<script type="application/ld+json">\n{schema_json}\n</script>')

        if not inject_parts: continue

        inject_html = "\n".join(inject_parts)

        # Insert before </head>
        if "</head>" in html:
            html = html.replace("</head>", inject_html + "\n</head>", 1)
            f.write_text(html, encoding="utf-8")
            updated += 1

    log(f"Schema/meta injected into {updated} pages")

# ══════════════════════════════════════════════════════
# PHASE 5 — FOOTER INJECTION
# ══════════════════════════════════════════════════════
FOOTER_CSS = """
<style id="np-footer-css">
#np-footer{background:#040408;border-top:1px solid #1a1a2e;padding:52px 5% 0;font-family:'Space Grotesk',system-ui,sans-serif;color:#f0f0f0;position:relative;z-index:1;overflow:hidden;}
#np-footer::before{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(0,229,255,.012) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,.012) 1px,transparent 1px);background-size:54px 54px;pointer-events:none;}
.np-fi{max-width:1160px;margin:0 auto;display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:48px;padding-bottom:40px;border-bottom:1px solid #1a1a2e;position:relative;z-index:1;}
.np-fb a{display:flex;align-items:center;gap:9px;text-decoration:none;color:#f0f0f0;font-weight:800;font-size:1.05rem;margin-bottom:12px;}
.np-dot{width:9px;height:9px;border-radius:50%;background:#00e5ff;box-shadow:0 0 8px #00e5ff;animation:np-pulse 2s infinite;}
@keyframes np-pulse{0%,100%{opacity:1;box-shadow:0 0 8px #00e5ff}50%{opacity:.35;box-shadow:0 0 20px #00e5ff}}
.np-fd{font-size:.8rem;color:#666880;line-height:1.75;max-width:270px;margin-bottom:20px;}
.np-social{display:flex;gap:8px;flex-wrap:wrap;}
.np-social a{display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:#0e0e1a;border:1px solid #222235;color:#666880;text-decoration:none;transition:all .22s;}
.np-social a:hover{border-color:#00e5ff;color:#00e5ff;transform:translateY(-3px);box-shadow:0 6px 18px rgba(0,229,255,.2);}
.np-social svg{width:14px;height:14px;fill:currentColor;}
.np-col h4{font-size:.64rem;font-weight:700;color:#666880;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;font-family:'JetBrains Mono',monospace,sans-serif;}
.np-col ul{list-style:none;padding:0;margin:0;}
.np-col ul li{margin-bottom:9px;}
.np-col ul a{color:#666880;text-decoration:none;font-size:.82rem;transition:color .18s,padding-left .18s;display:inline-block;}
.np-col ul a:hover{color:#00e5ff;padding-left:5px;}
.np-bottom{max-width:1160px;margin:0 auto;padding:20px 0 28px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;font-size:.74rem;color:#333348;position:relative;z-index:1;}
.np-status{display:flex;align-items:center;gap:5px;font-family:monospace;font-size:.66rem;color:#666880;}
.np-status-dot{width:6px;height:6px;border-radius:50%;background:#00ff88;animation:np-pulse 2s infinite;}
@media(max-width:900px){.np-fi{grid-template-columns:1fr 1fr;}}
@media(max-width:560px){.np-fi{grid-template-columns:1fr;}}
</style>
"""

def build_footer(path: Path) -> str:
    d = depth(path)
    def link(href):
        if href.startswith("http"): return href
        return ("../" * d) + href.lstrip("/")

    s = CONFIG["social"]
    nav_items = "".join(
        f'<li><a href="{link(h)}">{n}</a></li>'
        for n, h in CONFIG["nav_links"]
    )

    return f"""
{FOOTER_CSS}
<footer id="np-footer" itemscope itemtype="https://schema.org/WPFooter">
  <div class="np-fi">
    <div class="np-fb">
      <a href="{link("/index.html")}" aria-label="{CONFIG["brand_name"]} Home">
        <span class="np-dot"></span>{CONFIG["brand_name"]}
      </a>
      <p class="np-fd">{CONFIG["description"]}</p>
      <div class="np-social">
        <a href="{s['twitter']}" target="_blank" rel="noopener" title="Twitter / X">
          <svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.748l7.73-8.835L1.254 2.25H8.08l4.263 5.638 5.9-5.638zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        </a>
        <a href="{s['linkedin']}" target="_blank" rel="noopener" title="LinkedIn">
          <svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
        </a>
        <a href="{s['youtube']}" target="_blank" rel="noopener" title="YouTube">
          <svg viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
        </a>
        <a href="{s['github']}" target="_blank" rel="noopener" title="GitHub">
          <svg viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
        </a>
        <a href="{s['discord']}" target="_blank" rel="noopener" title="Discord">
          <svg viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028 14.09 14.09 0 001.226-1.994.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03z"/></svg>
        </a>
      </div>
    </div>
    <div class="np-col">
      <h4>Pages</h4>
      <ul>{nav_items}</ul>
    </div>
    <div class="np-col">
      <h4>Topics</h4>
      <ul>
        <li><a href="{link('/blog.html')}">Kimi AI Guides</a></li>
        <li><a href="{link('/blog.html')}">Gemini AI Ads</a></li>
        <li><a href="{link('/blog.html')}">AI Automation</a></li>
        <li><a href="{link('/blog.html')}">Prompt Engineering</a></li>
        <li><a href="{link('/blog.html')}">AI Models & LLMs</a></li>
        <li><a href="{link('/blog.html')}">AI SEO & GEO</a></li>
      </ul>
    </div>
    <div class="np-col">
      <h4>Connect</h4>
      <ul>
        <li><a href="{link('/contact.html')}">Contact</a></li>
        <li><a href="{link('/sitemap.html')}">Sitemap</a></li>
        <li><a href="{s['twitter']}" target="_blank" rel="noopener">Twitter / X</a></li>
        <li><a href="{s['linkedin']}" target="_blank" rel="noopener">LinkedIn</a></li>
        <li><a href="{s['github']}" target="_blank" rel="noopener">GitHub</a></li>
        <li><a href="{s['discord']}" target="_blank" rel="noopener">Discord</a></li>
      </ul>
    </div>
  </div>
  <div class="np-bottom">
    <span>© {NOW.year} {CONFIG["brand_name"]} · {CONFIG["author_name"]} · Est. 2025</span>
    <div class="np-status"><span class="np-status-dot"></span>All systems operational</div>
  </div>
</footer>
"""

def phase5_footer(files):
    log("="*55, "")
    log("PHASE 5 — FOOTER INJECTION (ALL PAGES)", "PHASE")
    log("="*55, "")
    updated = skipped = already = 0

    for f in files:
        try:
            html = f.read_text(encoding="utf-8", errors="ignore")
        except: continue

        if 'id="np-footer"' in html:
            already += 1
            continue

        footer_html = build_footer(f)

        # Replace existing footer or inject before </body>
        if "<footer" in html and "</footer>" in html:
            html = re.sub(r'<footer[\s\S]*?</footer>', footer_html, html, count=1)
        elif "</body>" in html:
            html = html.replace("</body>", footer_html + "\n</body>", 1)
        else:
            html += footer_html
            
        f.write_text(html, encoding="utf-8")
        updated += 1

    log(f"Footer injected: {updated} pages · Already had footer: {already}")

# ══════════════════════════════════════════════════════
# PHASE 6 — NAV INJECTION (Add Guide to all navs)
# ══════════════════════════════════════════════════════
def phase6_nav(files):
    log("="*55, "")
    log("PHASE 6 — NAV — ADD GUIDE LINK", "PHASE")
    log("="*55, "")
    updated = already = 0

    patterns = [
        ('<li><a href="https://neuraplus-ai.github.io/blog.html">Blog</a></li>',
         '<li><a href="https://neuraplus-ai.github.io/blog.html">Blog</a></li>\n    <li><a href="https://neuraplus-ai.github.io/guide.html">Guide</a></li>'),
        ('<li><a href="../blog.html">Blog</a></li>',
         '<li><a href="../blog.html">Blog</a></li>\n    <li><a href="../guide.html">Guide</a></li>'),
        ('<li><a href="../../blog.html">Blog</a></li>',
         '<li><a href="../../blog.html">Blog</a></li>\n    <li><a href="../../guide.html">Guide</a></li>'),
    ]

    for f in files:
        try:
            html = f.read_text(encoding="utf-8", errors="ignore")
        except: continue

        if 'guide.html">Guide</a>' in html or "guide.html'>Guide</a>" in html:
            already += 1
            continue

        new = html
        for find, replace in patterns:
            if find in new:
                new = new.replace(find, replace)
                break

        if new != html:
            f.write_text(new, encoding="utf-8")
            updated += 1

    log(f"Guide nav added: {updated} pages · Already present: {already}")

# ══════════════════════════════════════════════════════
# PHASE 7 — GEO/AEO META TAGS
# ══════════════════════════════════════════════════════
def phase7_geo(files):
    log("="*55, "")
    log("PHASE 7 — GEO/AEO AI VISIBILITY TAGS", "PHASE")
    log("="*55, "")
    updated = 0

    geo_tags = f"""
<!-- GEO / AEO / AI Visibility Tags -->
<meta name="author" content="{CONFIG["author_name"]}"/>
<meta name="publisher" content="{CONFIG["brand_name"]}"/>
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"/>
<meta name="googlebot" content="index, follow"/>
<meta name="bingbot" content="index, follow"/>
<meta name="rating" content="general"/>
<meta name="revisit-after" content="7 days"/>
<meta name="language" content="English"/>
<meta name="category" content="Artificial Intelligence, Technology, AI Tools"/>
<meta name="classification" content="AI Technology Blog"/>
<meta name="subject" content="Artificial Intelligence, AI Tools, Machine Learning"/>
<meta name="coverage" content="Worldwide"/>
<meta name="distribution" content="Global"/>
<meta name="target" content="all"/>
<link rel="alternate" type="application/rss+xml" title="{CONFIG["brand_name"]} RSS" href="{SITE}/rss.xml"/>
<!-- End GEO/AEO Tags -->"""

    for f in files:
        try:
            html = f.read_text(encoding="utf-8", errors="ignore")
        except: continue

        if 'GEO / AEO' in html:
            continue

        if "<head>" in html:
            html = html.replace("<head>", "<head>" + geo_tags, 1)
            f.write_text(html, encoding="utf-8")
            updated += 1

    log(f"GEO/AEO tags injected: {updated} pages")

# ══════════════════════════════════════════════════════
# PHASE 8 — SAVE RUN LOG
# ══════════════════════════════════════════════════════
def save_log():
    log_path = ROOT / "seo-run-log.txt"
    log_path.write_text("\n".join(log_lines), encoding="utf-8")
    print(f"\n[LOG] Full log saved → seo-run-log.txt")

# ══════════════════════════════════════════════════════
# MAIN — run all phases
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "═"*58)
    print("  NeuraPulse SEO Engine — All Phases")
    print(f"  Site root : {ROOT}")
    print(f"  Run time  : {TS}")
    print("═"*58 + "\n")

    files = get_all_html()
    log(f"Found {len(files)} HTML files to process")

    issues, urls = phase1_audit(files)
    phase2_entity()
    phase3_technical(files, urls)
    phase4_schema(files)
    phase5_footer(files)
    phase6_nav(files)
    phase7_geo(files)
    save_log()

    print("\n" + "═"*58)
    print(f"  ✅  ALL PHASES COMPLETE")
    print(f"  Pages processed : {len(files)}")
    print(f"  Audit issues    : {len(issues)}")
    print("═"*58 + "\n")
    print("FILES GENERATED:")
    print("  robots.txt · sitemap.xml · sitemap.html · rss.xml")
    print("  llms.txt · ai.txt · humans.txt · security.txt")
    print("  schema/organization.json · schema/website.json")
    print("  seo-audit-report.json · seo-run-log.txt")
    print("\nNow commit and push everything to GitHub.\n")
