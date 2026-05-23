#!/usr/bin/env python3
"""
NeuraPulse — Safe Footer & Social Links Injector
================================================
SAFE RULES:
  ✅ Pages WITH footer but NO social links  → adds social links only
  ✅ Pages with NO footer at all            → adds full footer
  ⏭  Pages that already have social links   → SKIPPED (untouched)
  ⏭  Pages that already have full footer    → SKIPPED (untouched)

Run from your repo ROOT:
  python safe_footer_inject.py
"""

import os, re
from pathlib import Path

# ── CONFIG ─────────────────────────────────────────
SITE        = "https://neuraplus-ai.github.io"
BRAND       = "NeuraPulse"
AUTHOR      = "Prashant Lalwani"
SITE_ROOT   = "."

SOCIAL = {
    "twitter":  "https://twitter.com/neuraplus_ai",
    "linkedin": "https://linkedin.com/in/prashant-lalwani",
    "youtube":  "https://youtube.com/@neurapulse",
    "github":   "https://github.com/neuraplus-ai",
    "discord":  "https://discord.gg/neurapulse",
}

SKIP_FILES = {
    "safe_footer_inject.py",
    "seo_engine.py",
    "add_guide_nav.py",
}
SKIP_DIRS = {".git", "node_modules", ".github", "scripts", "assets"}

# ── DETECTION ──────────────────────────────────────
def has_social_links(html):
    """True if page already has real social icon links."""
    signals = [
        'twitter.com', 'linkedin.com', 'youtube.com',
        'discord.gg', 'f-social', 'np-social',
        'social-link', 'social-links',
    ]
    return any(s in html for s in signals)

def has_footer(html):
    """True if page has any <footer> tag."""
    return '<footer' in html.lower()

def has_np_footer(html):
    """True if page already has OUR injected footer."""
    return 'id="np-footer"' in html or "id='np-footer'" in html

# ── SOCIAL BLOCK (inject into existing footer) ─────
SOCIAL_HTML = """
<!-- NeuraPulse Social Links -->
<div class="np-social-inject" style="display:flex;gap:8px;flex-wrap:wrap;margin-top:16px;">
  <a href="{twitter}" target="_blank" rel="noopener" title="Twitter / X"
     style="display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:#0e0e1a;border:1px solid #222235;color:#666880;text-decoration:none;transition:all .22s;"
     onmouseover="this.style.borderColor='#00e5ff';this.style.color='#00e5ff'"
     onmouseout="this.style.borderColor='#222235';this.style.color='#666880'">
    <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.748l7.73-8.835L1.254 2.25H8.08l4.263 5.638 5.9-5.638zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
  </a>
  <a href="{linkedin}" target="_blank" rel="noopener" title="LinkedIn"
     style="display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:#0e0e1a;border:1px solid #222235;color:#666880;text-decoration:none;transition:all .22s;"
     onmouseover="this.style.borderColor='#00e5ff';this.style.color='#00e5ff'"
     onmouseout="this.style.borderColor='#222235';this.style.color='#666880'">
    <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
  </a>
  <a href="{youtube}" target="_blank" rel="noopener" title="YouTube"
     style="display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:#0e0e1a;border:1px solid #222235;color:#666880;text-decoration:none;transition:all .22s;"
     onmouseover="this.style.borderColor='#00e5ff';this.style.color='#00e5ff'"
     onmouseout="this.style.borderColor='#222235';this.style.color='#666880'">
    <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
  </a>
  <a href="{github}" target="_blank" rel="noopener" title="GitHub"
     style="display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:#0e0e1a;border:1px solid #222235;color:#666880;text-decoration:none;transition:all .22s;"
     onmouseover="this.style.borderColor='#00e5ff';this.style.color='#00e5ff'"
     onmouseout="this.style.borderColor='#222235';this.style.color='#666880'">
    <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
  </a>
  <a href="{discord}" target="_blank" rel="noopener" title="Discord"
     style="display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:#0e0e1a;border:1px solid #222235;color:#666880;text-decoration:none;transition:all .22s;"
     onmouseover="this.style.borderColor='#00e5ff';this.style.color='#00e5ff'"
     onmouseout="this.style.borderColor='#222235';this.style.color='#666880'">
    <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028 14.09 14.09 0 001.226-1.994.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03z"/></svg>
  </a>
</div>
<!-- End NeuraPulse Social Links -->
""".format(**SOCIAL)

# ── FULL FOOTER (for pages with no footer at all) ──
def build_full_footer(path: Path) -> str:
    d = len(path.relative_to(Path(SITE_ROOT).resolve()).parts) - 1
    pre = "../" * d

    def lnk(href):
        if href.startswith("http"): return href
        return pre + href.lstrip("/")

    nav_links = [
        ("Home",    "index.html"),
        ("Blog",    "blog.html"),
        ("Guide",   "guide.html"),
        ("About",   "about.html"),
        ("Contact", "contact.html"),
    ]
    nav_items = "".join(
        f'<li style="margin-bottom:8px"><a href="{lnk(h)}" style="color:#666880;text-decoration:none;font-size:.82rem;transition:color .18s;" onmouseover="this.style.color=\'#00e5ff\'" onmouseout="this.style.color=\'#666880\'">{n}</a></li>'
        for n, h in nav_links
    )

    return f"""
<!-- NeuraPulse Footer -->
<style>
@keyframes np-pulse{{0%,100%{{opacity:1;box-shadow:0 0 8px #00e5ff}}50%{{opacity:.35;box-shadow:0 0 20px #00e5ff}}}}
#np-footer{{background:#040408;border-top:1px solid #1a1a2e;padding:52px 5% 0;font-family:'Space Grotesk',system-ui,sans-serif;color:#f0f0f0;position:relative;overflow:hidden;}}
#np-footer::before{{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(0,229,255,.012) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,.012) 1px,transparent 1px);background-size:54px 54px;pointer-events:none;}}
.np-fi{{max-width:1160px;margin:0 auto;display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:48px;padding-bottom:40px;border-bottom:1px solid #1a1a2e;position:relative;z-index:1;}}
.np-fb-logo{{display:flex;align-items:center;gap:9px;text-decoration:none;color:#f0f0f0;font-weight:800;font-size:1.05rem;margin-bottom:12px;}}
.np-dot{{width:9px;height:9px;border-radius:50%;background:#00e5ff;box-shadow:0 0 8px #00e5ff;animation:np-pulse 2s infinite;flex-shrink:0;}}
.np-fd{{font-size:.8rem;color:#666880;line-height:1.75;max-width:270px;margin-bottom:20px;}}
.np-social{{display:flex;gap:8px;flex-wrap:wrap;}}
.np-social a{{display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:#0e0e1a;border:1px solid #222235;color:#666880;text-decoration:none;transition:all .22s;}}
.np-social a:hover{{border-color:#00e5ff;color:#00e5ff;transform:translateY(-3px);box-shadow:0 6px 18px rgba(0,229,255,.2);}}
.np-social svg{{width:14px;height:14px;fill:currentColor;}}
.np-col h4{{font-size:.64rem;font-weight:700;color:#666880;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;font-family:monospace;}}
.np-col ul{{list-style:none;padding:0;margin:0;}}
.np-bottom{{max-width:1160px;margin:0 auto;padding:20px 0 28px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;font-size:.74rem;color:#333348;position:relative;z-index:1;}}
.np-status{{display:flex;align-items:center;gap:5px;font-family:monospace;font-size:.66rem;color:#666880;}}
.np-status-dot{{width:6px;height:6px;border-radius:50%;background:#00ff88;animation:np-pulse 2s infinite;}}
@media(max-width:900px){{.np-fi{{grid-template-columns:1fr 1fr;}}}}
@media(max-width:560px){{.np-fi{{grid-template-columns:1fr;}}}}
</style>
<footer id="np-footer">
  <div class="np-fi">
    <div>
      <a class="np-fb-logo" href="{lnk('index.html')}">
        <span class="np-dot"></span>{BRAND}
      </a>
      <p class="np-fd">Expert AI guides, tools, and analysis — making artificial intelligence understandable and actionable for developers and creators worldwide.</p>
      <div class="np-social">
        <a href="{SOCIAL['twitter']}" target="_blank" rel="noopener" title="Twitter / X">
          <svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.748l7.73-8.835L1.254 2.25H8.08l4.263 5.638 5.9-5.638zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        </a>
        <a href="{SOCIAL['linkedin']}" target="_blank" rel="noopener" title="LinkedIn">
          <svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
        </a>
        <a href="{SOCIAL['youtube']}" target="_blank" rel="noopener" title="YouTube">
          <svg viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
        </a>
        <a href="{SOCIAL['github']}" target="_blank" rel="noopener" title="GitHub">
          <svg viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
        </a>
        <a href="{SOCIAL['discord']}" target="_blank" rel="noopener" title="Discord">
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
        <li style="margin-bottom:8px"><a href="{lnk('blog.html')}" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">Kimi AI Guides</a></li>
        <li style="margin-bottom:8px"><a href="{lnk('blog.html')}" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">Gemini AI Ads</a></li>
        <li style="margin-bottom:8px"><a href="{lnk('blog.html')}" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">AI Automation</a></li>
        <li style="margin-bottom:8px"><a href="{lnk('blog.html')}" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">Prompt Engineering</a></li>
        <li style="margin-bottom:8px"><a href="{lnk('blog.html')}" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">AI SEO & GEO</a></li>
      </ul>
    </div>
    <div class="np-col">
      <h4>Connect</h4>
      <ul>
        <li style="margin-bottom:8px"><a href="{lnk('contact.html')}" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">Contact</a></li>
        <li style="margin-bottom:8px"><a href="{lnk('sitemap.html')}" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">Sitemap</a></li>
        <li style="margin-bottom:8px"><a href="{SOCIAL['twitter']}" target="_blank" rel="noopener" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">Twitter / X</a></li>
        <li style="margin-bottom:8px"><a href="{SOCIAL['linkedin']}" target="_blank" rel="noopener" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">LinkedIn</a></li>
        <li style="margin-bottom:8px"><a href="{SOCIAL['github']}" target="_blank" rel="noopener" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">GitHub</a></li>
        <li style="margin-bottom:8px"><a href="{SOCIAL['discord']}" target="_blank" rel="noopener" style="color:#666880;text-decoration:none;font-size:.82rem;" onmouseover="this.style.color='#00e5ff'" onmouseout="this.style.color='#666880'">Discord</a></li>
      </ul>
    </div>
  </div>
  <div class="np-bottom">
    <span>© 2026 {BRAND} · {AUTHOR} · Est. 2025</span>
    <div class="np-status"><span class="np-status-dot"></span>All systems operational</div>
  </div>
</footer>
<!-- End NeuraPulse Footer -->
"""

# ── MAIN ───────────────────────────────────────────
def main():
    root = Path(SITE_ROOT).resolve()

    counts = {
        "social_added":   0,   # had footer, added social icons only
        "footer_added":   0,   # had no footer, added full footer
        "skipped_safe":   0,   # already had social links — untouched
        "skipped_err":    0,   # read error
    }
    social_added_files  = []
    footer_added_files  = []
    skipped_safe_files  = []

    all_html = []
    for path in sorted(root.rglob("*.html")):
        rel   = path.relative_to(root)
        parts = rel.parts
        if any(p in SKIP_DIRS for p in parts): continue
        if path.name in SKIP_FILES:            continue
        all_html.append(path)

    print(f"\n{'='*55}")
    print(f"  NeuraPulse Safe Footer Injector")
    print(f"  Scanning {len(all_html)} HTML files...")
    print(f"{'='*55}\n")

    for f in all_html:
        try:
            html = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            counts["skipped_err"] += 1
            continue

        rel = str(f.relative_to(root))

        # ── CASE 1: already has social links → SKIP, touch nothing ──
        if has_social_links(html):
            counts["skipped_safe"] += 1
            skipped_safe_files.append(rel)
            continue

        # ── CASE 2: has footer but no social links → add social only ──
        if has_footer(html):
            # Try to inject social links just before </footer>
            if "</footer>" in html:
                html = html.replace("</footer>", SOCIAL_HTML + "\n</footer>", 1)
            else:
                # footer tag exists but no closing tag — append after <footer ...>
                html = re.sub(r'(<footer[^>]*>)', r'\1' + SOCIAL_HTML, html, count=1)
            f.write_text(html, encoding="utf-8")
            counts["social_added"] += 1
            social_added_files.append(rel)
            continue

        # ── CASE 3: no footer at all → add full footer ──
        full = build_full_footer(f)
        if "</body>" in html:
            html = html.replace("</body>", full + "\n</body>", 1)
        else:
            html += full
        f.write_text(html, encoding="utf-8")
        counts["footer_added"] += 1
        footer_added_files.append(rel)

    # ── REPORT ──
    print(f"{'='*55}")
    print(f"  ✅  SOCIAL LINKS ADDED (had footer, no socials): {counts['social_added']}")
    for f in social_added_files[:10]:
        print(f"      + {f}")
    if len(social_added_files) > 10:
        print(f"      ... and {len(social_added_files)-10} more")

    print(f"\n  ✅  FULL FOOTER ADDED (had no footer): {counts['footer_added']}")
    for f in footer_added_files[:10]:
        print(f"      + {f}")
    if len(footer_added_files) > 10:
        print(f"      ... and {len(footer_added_files)-10} more")

    print(f"\n  ⏭   SKIPPED SAFE (already had social links): {counts['skipped_safe']}")
    print(f"  ⚠️   SKIPPED ERRORS: {counts['skipped_err']}")
    print(f"\n  Total pages processed: {len(all_html)}")
    print(f"{'='*55}\n")
    print("Done! Now run:  git add . && git commit -m 'Add social links to all pages' && git push\n")

if __name__ == "__main__":
    main()
