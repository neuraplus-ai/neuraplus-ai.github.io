#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  NeuraPulse — Blog Card Injector v3.0                       ║
║  Matches exact card style from blog.html screenshot         ║
║  Unique live-animated SVG thumbnails per topic              ║
╚══════════════════════════════════════════════════════════════╝
DROP IN REPO ROOT → python neurapulse_card_injector.py
"""
import os, re, datetime
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────
SITE        = "https://neuraplus-ai.github.io"
AUTHOR      = "Prashant Lalwani"
BLOG_DIR    = "blog"
BLOG_PAGE   = "blog.html"
GUIDE_PAGE  = "guide.html"
BLOG_START  = "<!-- NP:BLOG-CARDS-START -->"
BLOG_END    = "<!-- NP:BLOG-CARDS-END -->"
GUIDE_START = "<!-- NP:GUIDE-CARDS-START -->"
GUIDE_END   = "<!-- NP:GUIDE-CARDS-END -->"
TODAY       = datetime.datetime.now().strftime("%Y-%m-%d")
ROOT        = Path(".").resolve()

SKIP = {
    "neurapulse_card_injector.py","neurapulse_enterprise.py",
    "master_inject.py","seo_engine.py",
    "blog.html","guide.html","index.html","about.html","contact.html",
}

# ── META EXTRACTION ──────────────────────────────────────────────
def extract(path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE|re.DOTALL)
    title = re.sub(r'<[^>]+>','', m.group(1)).strip().split('—')[0].split('–')[0].split('|')[0].strip() if m else path.stem.replace('-',' ').title()
    d = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']{30,})', html, re.IGNORECASE)
    if d:
        desc = d.group(1).strip()
    else:
        ps = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        desc = re.sub(r'<[^>]+>','', ps[0]).strip()[:180] if ps else f"Deep dive into {title} — expert AI guide for 2026."
    dt = re.search(r'(\d{4}-\d{2}-\d{2})', html)
    date = dt.group(1) if dt else TODAY
    words = len(re.sub(r'<[^>]+>',' ', html).split())
    mins  = max(5, round(words/220))
    return title, desc[:180], date, mins

# ── TAG SYSTEM ───────────────────────────────────────────────────
TAGS = [
    (["coding","for-coding","developer","github","debug","programm","api","javascript","python"],
     "AI CODING",    "#00d4ff","rgba(0,212,255,.1)","rgba(0,212,255,.35)"),
    (["website","builder","wordpress","generator","web-tool","html","deploy","build-a-website"],
     "WEB BUILD",    "#00ffb3","rgba(0,255,179,.08)","rgba(0,255,179,.35)"),
    (["chatbot","chat","widget","bot","messag"],
     "CHATBOT",      "#a78bfa","rgba(167,139,250,.1)","rgba(167,139,250,.35)"),
    (["vs-","versus","comparison","alternative","benchmark","like-kimi"],
     "COMPARISON",   "#fb923c","rgba(251,146,60,.1)","rgba(251,146,60,.35)"),
    (["beginner","tutorial","how-to","step-by-step","for-beginners","start","learn"],
     "BEGINNER",     "#34d399","rgba(52,211,153,.1)","rgba(52,211,153,.35)"),
    (["free","tool","best","top","list","resource","easy-ai"],
     "AI TOOLS",     "#00d4ff","rgba(0,212,255,.1)","rgba(0,212,255,.35)"),
    (["seo","rank","search","keyword","traffic","geo"],
     "AI SEO",       "#fbbf24","rgba(251,191,36,.1)","rgba(251,191,36,.35)"),
    (["automat","workflow","n8n","zapier","no-code"],
     "AUTOMATION",   "#4ade80","rgba(74,222,128,.1)","rgba(74,222,128,.35)"),
    (["web-tools","tools-in","2026"],
     "WEB TOOLS",    "#00d4ff","rgba(0,212,255,.1)","rgba(0,212,255,.35)"),
]

def get_tag(slug, title):
    t = (slug+' '+title).lower()
    for kws, *info in TAGS:
        if any(k in t for k in kws): return info
    return ["KIMI AI","#00d4ff","rgba(0,212,255,.1)","rgba(0,212,255,.35)"]

# ── 8 UNIQUE ANIMATED SVG THUMBNAILS ─────────────────────────────
def get_svg(slug, title):
    s = (slug+' '+title).lower()

    # 1. CODING
    if any(k in s for k in ["coding","developer","github","debug","programm","api"]):
        return """
<rect width="300" height="180" fill="#0c1120"/>
<rect x="20" y="15" width="260" height="150" rx="8" fill="#111827"/>
<rect x="20" y="15" width="260" height="20" rx="8 8 0 0" fill="#1a2236"/>
<circle cx="35" cy="25" r="4" fill="#ff5f57"/>
<circle cx="48" cy="25" r="4" fill="#ffbd2e"/>
<circle cx="61" cy="25" r="4" fill="#28ca41"/>
<text x="35" y="55" font-family="JetBrains Mono,monospace" font-size="9" fill="#c792ea">function</text>
<text x="91" y="55" font-family="JetBrains Mono,monospace" font-size="9" fill="#82aaff"> buildWithKimi</text>
<text x="196" y="55" font-family="JetBrains Mono,monospace" font-size="9" fill="#89ddff">() {</text>
<text x="43" y="71" font-family="JetBrains Mono,monospace" font-size="9" fill="#8899aa">  const</text>
<text x="77" y="71" font-family="JetBrains Mono,monospace" font-size="9" fill="#82aaff"> ctx</text>
<text x="97" y="71" font-family="JetBrains Mono,monospace" font-size="9" fill="#89ddff"> = </text>
<text x="111" y="71" font-family="JetBrains Mono,monospace" font-size="9" fill="#c3e88d">"2M tokens"</text>
<text x="43" y="87" font-family="JetBrains Mono,monospace" font-size="9" fill="#8899aa">  return</text>
<text x="87" y="87" font-family="JetBrains Mono,monospace" font-size="9" fill="#c3e88d"> output</text>
<text x="131" y="87" font-family="JetBrains Mono,monospace" font-size="9" fill="#89ddff">.best()</text>
<text x="35" y="103" font-family="JetBrains Mono,monospace" font-size="9" fill="#89ddff">}</text>
<rect x="175" y="98" width="2" height="11" fill="#00d4ff">
  <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
</rect>
<line x1="35" y1="115" x2="265" y2="115" stroke="#1a2236" stroke-width="1"/>
<text x="35" y="130" font-family="JetBrains Mono,monospace" font-size="7" fill="#546e7a">// Kimi K2 · 2M tokens · SWE-Bench #1</text>
<rect x="20" y="138" width="260" height="27" rx="0 0 8 8" fill="#0d1117"/>
<text x="48" y="156" font-family="JetBrains Mono,monospace" font-size="7" fill="#8899aa">kimi-k2 </text>
<text x="84" y="156" font-family="JetBrains Mono,monospace" font-size="7" fill="#00d4ff">main</text>
<text x="108" y="156" font-family="JetBrains Mono,monospace" font-size="7" fill="#546e7a"> · no issues</text>"""

    # 2. WEBSITE BUILDER
    if any(k in s for k in ["website","builder","wordpress","generator","build-a","web tool"]):
        return """
<rect width="300" height="180" fill="#0c1120"/>
<rect x="15" y="12" width="270" height="156" rx="8" fill="#111827"/>
<rect x="15" y="12" width="270" height="22" rx="8 8 0 0" fill="#1a2236"/>
<circle cx="30" cy="23" r="4" fill="#ff5f57"/>
<circle cx="44" cy="23" r="4" fill="#ffbd2e"/>
<circle cx="58" cy="23" r="4" fill="#28ca41"/>
<rect x="70" y="17" width="160" height="12" rx="6" fill="#0d1117"/>
<text x="88" y="26" font-family="Space Grotesk,sans-serif" font-size="7" fill="#556677">kimi.ai/generate ✓</text>
<rect x="15" y="34" width="0" height="4" fill="rgba(0,212,255,0.6)">
  <animate attributeName="width" values="0;270;270" dur="2s" repeatCount="indefinite"/>
</rect>
<rect x="25" y="48" width="240" height="30" rx="4" fill="#0d1117"/>
<rect x="35" y="55" width="0" height="6" rx="3" fill="rgba(0,212,255,0.6)">
  <animate attributeName="width" values="0;120" dur="1.2s" fill="freeze"/>
</rect>
<rect x="35" y="65" width="0" height="4" rx="2" fill="rgba(0,212,255,0.2)">
  <animate attributeName="width" values="0;80" dur="1.6s" fill="freeze"/>
</rect>
<rect x="25" y="86" width="110" height="60" rx="4" fill="#0d1117"/>
<rect x="35" y="94" width="90" height="4" rx="2" fill="rgba(255,255,255,0.1)"/>
<rect x="35" y="102" width="70" height="4" rx="2" fill="rgba(255,255,255,0.08)"/>
<rect x="35" y="110" width="80" height="4" rx="2" fill="rgba(255,255,255,0.07)"/>
<rect x="35" y="118" width="60" height="4" rx="2" fill="rgba(255,255,255,0.06)"/>
<rect x="35" y="130" width="70" height="12" rx="4" fill="rgba(0,212,255,0.3)"/>
<text x="48" y="139" font-family="Space Grotesk,sans-serif" font-size="7" fill="#000" font-weight="700">Deploy →</text>
<rect x="145" y="86" width="120" height="60" rx="4" fill="#0d1117"/>
<rect x="152" y="96" width="106" height="40" rx="3" fill="#131c2e"/>
<rect x="157" y="101" width="96" height="5" rx="2" fill="rgba(0,212,255,0.15)"/>
<rect x="157" y="110" width="76" height="3" rx="2" fill="rgba(255,255,255,0.07)"/>
<rect x="157" y="117" width="86" height="3" rx="2" fill="rgba(255,255,255,0.06)"/>
<circle cx="205" cy="136" r="4" fill="rgba(0,255,179,0.3)" stroke="rgba(0,255,179,0.6)" stroke-width="1">
  <animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite"/>
</circle>
<text x="214" y="139" font-family="JetBrains Mono,monospace" font-size="6" fill="#00ffb3">LIVE</text>"""

    # 3. CHATBOT
    if any(k in s for k in ["chatbot","chat","widget","bot","messag"]):
        return """
<rect width="300" height="180" fill="#0c1120"/>
<rect x="20" y="10" width="260" height="160" rx="12" fill="#111827"/>
<rect x="20" y="10" width="260" height="28" rx="12 12 0 0" fill="#1a2236"/>
<circle cx="40" cy="24" r="9" fill="rgba(0,212,255,0.15)" stroke="rgba(0,212,255,0.5)" stroke-width="1.5"/>
<text x="40" y="28" font-family="Arial" font-size="8" font-weight="bold" fill="#00d4ff" text-anchor="middle">AI</text>
<text x="55" y="20" font-family="Space Grotesk,sans-serif" font-size="8" font-weight="600" fill="#fff">Kimi AI Chat</text>
<text x="55" y="31" font-family="Space Grotesk,sans-serif" font-size="7" fill="#00ffb3">● Online</text>
<rect x="30" y="48" width="150" height="20" rx="10 10 10 2" fill="#1e2d45">
  <animate attributeName="opacity" values="0;1" dur="0.4s" fill="freeze"/>
</rect>
<text x="40" y="61" font-family="Space Grotesk,sans-serif" font-size="8" fill="#c9d8e8">How can I help you today?</text>
<rect x="120" y="76" width="130" height="20" rx="10 10 2 10" fill="rgba(0,212,255,0.25)">
  <animate attributeName="opacity" values="0;1" dur="0.4s" begin="0.6s" fill="freeze"/>
</rect>
<text x="128" y="89" font-family="Space Grotesk,sans-serif" font-size="8" fill="#fff" font-weight="600">Build my website now!</text>
<rect x="30" y="104" width="160" height="20" rx="10 10 10 2" fill="#1e2d45">
  <animate attributeName="opacity" values="0;1" dur="0.4s" begin="1.2s" fill="freeze"/>
</rect>
<text x="40" y="117" font-family="Space Grotesk,sans-serif" font-size="8" fill="#c9d8e8">Generating your code now…</text>
<rect x="30" y="130" width="80" height="18" rx="9" fill="#1e2d45">
  <animate attributeName="opacity" values="0;1" dur="0.3s" begin="1.8s" fill="freeze"/>
</rect>
<circle cx="48" cy="139" r="3" fill="#8899aa">
  <animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" begin="1.8s" repeatCount="indefinite"/>
</circle>
<circle cx="58" cy="139" r="3" fill="#8899aa">
  <animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" begin="2s" repeatCount="indefinite"/>
</circle>
<circle cx="68" cy="139" r="3" fill="#8899aa">
  <animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" begin="2.2s" repeatCount="indefinite"/>
</circle>
<rect x="30" y="155" width="240" height="10" rx="5" fill="#0d1117"/>
<text x="80" y="163" font-family="Space Grotesk,sans-serif" font-size="7" fill="#556677">Type a message…</text>"""

    # 4. COMPARISON
    if any(k in s for k in ["vs-","versus","comparison","alternative","benchmark","like-kimi","alternatives"]):
        return """
<rect width="300" height="180" fill="#0c1120"/>
<rect x="10" y="20" width="120" height="130" rx="8" fill="#111827" stroke="rgba(0,212,255,0.3)" stroke-width="1.5"/>
<text x="70" y="52" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="800" fill="#00d4ff" text-anchor="middle">KIMI AI</text>
<rect x="25" y="60" width="90" height="5" rx="2.5" fill="rgba(0,212,255,0.2)"/>
<rect x="25" y="60" width="0" height="5" rx="2.5" fill="rgba(0,212,255,0.7)">
  <animate attributeName="width" values="0;90" dur="1.4s" fill="freeze"/>
</rect>
<text x="70" y="72" font-family="JetBrains Mono,monospace" font-size="7" fill="#8899aa" text-anchor="middle">Context: 2M</text>
<rect x="25" y="78" width="90" height="4" rx="2" fill="rgba(0,212,255,0.1)"/>
<rect x="25" y="78" width="0" height="4" rx="2" fill="rgba(0,212,255,0.5)">
  <animate attributeName="width" values="0;82" dur="1.6s" fill="freeze"/>
</rect>
<text x="70" y="91" font-family="JetBrains Mono,monospace" font-size="7" fill="#8899aa" text-anchor="middle">Coding: 97%</text>
<rect x="25" y="97" width="90" height="4" rx="2" fill="rgba(0,212,255,0.1)"/>
<rect x="25" y="97" width="0" height="4" rx="2" fill="rgba(0,255,179,0.5)">
  <animate attributeName="width" values="0;88" dur="1.8s" fill="freeze"/>
</rect>
<text x="70" y="110" font-family="JetBrains Mono,monospace" font-size="7" fill="#8899aa" text-anchor="middle">Free Tier: ✓</text>
<rect x="30" y="120" width="80" height="16" rx="6" fill="rgba(0,212,255,0.15)" stroke="rgba(0,212,255,0.4)" stroke-width="1"/>
<text x="70" y="132" font-family="Space Grotesk,sans-serif" font-size="7" fill="#00d4ff" text-anchor="middle" font-weight="700">WINNER ✓</text>
<text x="150" y="92" font-family="JetBrains Mono,monospace" font-size="20" font-weight="900" fill="rgba(0,212,255,0.6)" text-anchor="middle">VS</text>
<rect x="170" y="20" width="120" height="130" rx="8" fill="#111827" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
<text x="230" y="52" font-family="Space Grotesk,sans-serif" font-size="9" font-weight="800" fill="#8899aa" text-anchor="middle">OTHERS</text>
<rect x="185" y="60" width="90" height="5" rx="2.5" fill="rgba(255,255,255,0.1)"/>
<rect x="185" y="60" width="0" height="5" rx="2.5" fill="rgba(255,255,255,0.3)">
  <animate attributeName="width" values="0;45" dur="1.4s" fill="freeze"/>
</rect>
<text x="230" y="72" font-family="JetBrains Mono,monospace" font-size="7" fill="#556677" text-anchor="middle">Context: 128K</text>
<rect x="185" y="78" width="90" height="4" rx="2" fill="rgba(255,255,255,0.05)"/>
<rect x="185" y="78" width="0" height="4" rx="2" fill="rgba(255,255,255,0.2)">
  <animate attributeName="width" values="0;55" dur="1.6s" fill="freeze"/>
</rect>
<text x="230" y="91" font-family="JetBrains Mono,monospace" font-size="7" fill="#556677" text-anchor="middle">Coding: 81%</text>
<rect x="185" y="97" width="90" height="4" rx="2" fill="rgba(255,255,255,0.05)"/>
<rect x="185" y="97" width="0" height="4" rx="2" fill="rgba(255,255,255,0.15)">
  <animate attributeName="width" values="0;40" dur="1.8s" fill="freeze"/>
</rect>
<text x="230" y="110" font-family="JetBrains Mono,monospace" font-size="7" fill="#556677" text-anchor="middle">Free Tier: ✗</text>"""

    # 5. BEGINNER / HOW-TO
    if any(k in s for k in ["beginner","how-to","tutorial","step","start","learn","for-beginners"]):
        return """
<rect width="300" height="180" fill="#0c1120"/>
<g opacity="0">
  <rect x="20" y="18" width="260" height="28" rx="6" fill="#111827"/>
  <circle cx="38" cy="32" r="9" fill="rgba(0,212,255,0.2)" stroke="#00d4ff" stroke-width="1.5"/>
  <text x="38" y="36" font-family="JetBrains Mono,monospace" font-size="9" fill="#00d4ff" text-anchor="middle" font-weight="bold">1</text>
  <text x="54" y="30" font-family="Space Grotesk,sans-serif" font-size="8" font-weight="600" fill="#fff">Visit kimi.com</text>
  <text x="54" y="41" font-family="Space Grotesk,sans-serif" font-size="7" fill="#8899aa">Free sign-up · no credit card</text>
  <text x="261" y="37" font-family="Arial" font-size="12" fill="#00ffb3">✓</text>
  <animate attributeName="opacity" values="0;1" dur="0.3s" begin="0s" fill="freeze"/>
</g>
<g opacity="0">
  <rect x="20" y="54" width="260" height="28" rx="6" fill="#111827"/>
  <circle cx="38" cy="68" r="9" fill="rgba(0,212,255,0.15)" stroke="rgba(0,212,255,0.6)" stroke-width="1.5"/>
  <text x="38" y="72" font-family="JetBrains Mono,monospace" font-size="9" fill="#00d4ff" text-anchor="middle" font-weight="bold">2</text>
  <text x="54" y="66" font-family="Space Grotesk,sans-serif" font-size="8" font-weight="600" fill="#fff">Start a new chat</text>
  <text x="54" y="77" font-family="Space Grotesk,sans-serif" font-size="7" fill="#8899aa">Describe what you need clearly</text>
  <text x="261" y="73" font-family="Arial" font-size="12" fill="#00ffb3">✓</text>
  <animate attributeName="opacity" values="0;1" dur="0.3s" begin="0.5s" fill="freeze"/>
</g>
<g opacity="0">
  <rect x="20" y="90" width="260" height="28" rx="6" fill="#111827"/>
  <circle cx="38" cy="104" r="9" fill="rgba(0,212,255,0.1)" stroke="rgba(0,212,255,0.4)" stroke-width="1.5"/>
  <text x="38" y="108" font-family="JetBrains Mono,monospace" font-size="9" fill="#00d4ff" text-anchor="middle" font-weight="bold">3</text>
  <text x="54" y="102" font-family="Space Grotesk,sans-serif" font-size="8" font-weight="600" fill="#fff">Upload your files</text>
  <text x="54" y="113" font-family="Space Grotesk,sans-serif" font-size="7" fill="#8899aa">PDFs, docs, code — up to 2M tokens</text>
  <text x="261" y="109" font-family="Arial" font-size="12" fill="#00ffb3">✓</text>
  <animate attributeName="opacity" values="0;1" dur="0.3s" begin="1s" fill="freeze"/>
</g>
<g opacity="0">
  <rect x="20" y="126" width="260" height="28" rx="6" fill="#111827"/>
  <circle cx="38" cy="140" r="9" fill="rgba(0,212,255,0.08)" stroke="rgba(0,212,255,0.3)" stroke-width="1.5"/>
  <text x="38" y="144" font-family="JetBrains Mono,monospace" font-size="9" fill="#00d4ff" text-anchor="middle" font-weight="bold">4</text>
  <text x="54" y="138" font-family="Space Grotesk,sans-serif" font-size="8" font-weight="600" fill="#fff">Get results instantly</text>
  <text x="54" y="149" font-family="Space Grotesk,sans-serif" font-size="7" fill="#8899aa">Iterate · refine · export · deploy</text>
  <animate attributeName="opacity" values="0;1" dur="0.3s" begin="1.5s" fill="freeze"/>
</g>"""

    # 6. FREE / TOOLS / BEST
    if any(k in s for k in ["free","easy","best","top","tool","2026","resource"]):
        return """
<rect width="300" height="180" fill="#0c1120"/>
<rect x="18" y="18" width="80" height="28" rx="6" fill="rgba(0,212,255,0.15)" stroke="rgba(0,212,255,0.5)" stroke-width="1">
  <animate attributeName="opacity" values="0.6;1;0.6" dur="2.4s" begin="0s" repeatCount="indefinite"/>
</rect>
<text x="58" y="36" font-family="Space Grotesk,sans-serif" font-size="9" font-weight="700" fill="#00d4ff" text-anchor="middle">Kimi AI</text>
<rect x="108" y="18" width="80" height="28" rx="6" fill="#111827" stroke="rgba(255,255,255,0.1)" stroke-width="1">
  <animate attributeName="opacity" values="0.6;1;0.6" dur="2.4s" begin="0.4s" repeatCount="indefinite"/>
</rect>
<text x="148" y="36" font-family="Space Grotesk,sans-serif" font-size="9" fill="#8899aa" text-anchor="middle">ChatGPT</text>
<rect x="198" y="18" width="80" height="28" rx="6" fill="#111827" stroke="rgba(255,255,255,0.1)" stroke-width="1">
  <animate attributeName="opacity" values="0.6;1;0.6" dur="2.4s" begin="0.8s" repeatCount="indefinite"/>
</rect>
<text x="238" y="36" font-family="Space Grotesk,sans-serif" font-size="9" fill="#8899aa" text-anchor="middle">Claude</text>
<rect x="18" y="56" width="88" height="28" rx="6" fill="#111827" stroke="rgba(255,255,255,0.08)" stroke-width="1">
  <animate attributeName="opacity" values="0.6;1;0.6" dur="2.4s" begin="0.2s" repeatCount="indefinite"/>
</rect>
<text x="62" y="74" font-family="Space Grotesk,sans-serif" font-size="9" fill="#8899aa" text-anchor="middle">Gemini Pro</text>
<rect x="116" y="56" width="72" height="28" rx="6" fill="rgba(0,255,179,0.15)" stroke="rgba(0,255,179,0.4)" stroke-width="1">
  <animate attributeName="opacity" values="0.6;1;0.6" dur="2.4s" begin="0.6s" repeatCount="indefinite"/>
</rect>
<text x="152" y="74" font-family="Space Grotesk,sans-serif" font-size="9" font-weight="700" fill="#00ffb3" text-anchor="middle">$0 FREE</text>
<rect x="198" y="56" width="80" height="28" rx="6" fill="#111827" stroke="rgba(255,255,255,0.08)" stroke-width="1">
  <animate attributeName="opacity" values="0.6;1;0.6" dur="2.4s" begin="1s" repeatCount="indefinite"/>
</rect>
<text x="238" y="74" font-family="Space Grotesk,sans-serif" font-size="9" fill="#8899aa" text-anchor="middle">Llama 4</text>
<rect x="128" y="94" width="80" height="28" rx="6" fill="rgba(0,212,255,0.1)" stroke="rgba(0,212,255,0.3)" stroke-width="1">
  <animate attributeName="opacity" values="0.6;1;0.6" dur="2.4s" begin="0.7s" repeatCount="indefinite"/>
</rect>
<text x="168" y="112" font-family="Space Grotesk,sans-serif" font-size="9" fill="#00d4ff" text-anchor="middle">2M Tokens</text>
<text x="150" y="155" font-family="Space Mono,monospace" font-size="8" fill="#a0a0b5" text-anchor="middle">BEST AI TOOLS 2026</text>"""

    # 7. SEO / AUTOMATION
    if any(k in s for k in ["seo","rank","search","automat","workflow","n8n"]):
        return """
<rect width="300" height="180" fill="#0c1120"/>
<rect x="20" y="20" width="260" height="140" rx="8" fill="#111827"/>
<text x="150" y="50" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="800" fill="#fbbf24" text-anchor="middle">SEO PERFORMANCE</text>
<rect x="35" y="60" width="230" height="8" rx="4" fill="rgba(255,255,255,0.05)"/>
<rect x="35" y="60" width="0" height="8" rx="4" fill="rgba(251,191,36,0.7)">
  <animate attributeName="width" values="0;200" dur="1.8s" fill="freeze"/>
</rect>
<text x="240" y="68" font-family="JetBrains Mono,monospace" font-size="7" fill="#fbbf24">87%</text>
<rect x="35" y="78" width="230" height="8" rx="4" fill="rgba(255,255,255,0.05)"/>
<rect x="35" y="78" width="0" height="8" rx="4" fill="rgba(0,212,255,0.6)">
  <animate attributeName="width" values="0;180" dur="2s" fill="freeze"/>
</rect>
<text x="240" y="86" font-family="JetBrains Mono,monospace" font-size="7" fill="#00d4ff">78%</text>
<rect x="35" y="96" width="230" height="8" rx="4" fill="rgba(255,255,255,0.05)"/>
<rect x="35" y="96" width="0" height="8" rx="4" fill="rgba(0,255,179,0.6)">
  <animate attributeName="width" values="0;220" dur="2.2s" fill="freeze"/>
</rect>
<text x="240" y="104" font-family="JetBrains Mono,monospace" font-size="7" fill="#00ffb3">96%</text>
<text x="35" y="122" font-family="JetBrains Mono,monospace" font-size="7" fill="#556677">Traffic</text>
<text x="35" y="134" font-family="JetBrains Mono,monospace" font-size="7" fill="#556677">Rankings</text>
<text x="35" y="146" font-family="JetBrains Mono,monospace" font-size="7" fill="#556677">AI Citations</text>"""

    # 8. DEFAULT — Kimi neural network
    return """
<rect width="300" height="180" fill="#0c1120"/>
<circle cx="150" cy="82" r="28" fill="rgba(0,212,255,0.06)" stroke="rgba(0,212,255,0.3)" stroke-width="1.5"/>
<circle cx="150" cy="82" r="15" fill="rgba(0,212,255,0.1)" stroke="rgba(0,212,255,0.5)" stroke-width="1.5"/>
<text x="150" y="87" font-family="JetBrains Mono,monospace" font-size="11" font-weight="900" fill="#00d4ff" text-anchor="middle">K2</text>
<circle cx="150" cy="40" r="6" fill="#00d4ff">
  <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" begin="0s" repeatCount="indefinite"/>
</circle>
<circle cx="185" cy="57" r="6" fill="#00ffb3">
  <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" begin="0.4s" repeatCount="indefinite"/>
</circle>
<circle cx="192" cy="97" r="5" fill="#a78bfa">
  <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" begin="0.8s" repeatCount="indefinite"/>
</circle>
<circle cx="150" cy="120" r="5" fill="#00d4ff">
  <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" begin="1.2s" repeatCount="indefinite"/>
</circle>
<circle cx="108" cy="97" r="5" fill="#00ffb3">
  <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" begin="1.6s" repeatCount="indefinite"/>
</circle>
<circle cx="115" cy="57" r="6" fill="#00d4ff">
  <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" begin="2s" repeatCount="indefinite"/>
</circle>
<line x1="150" y1="67" x2="150" y2="46" stroke="rgba(0,212,255,0.4)" stroke-width="1" stroke-dasharray="3,2">
  <animate attributeName="stroke-dashoffset" values="10;0" dur="1s" repeatCount="indefinite"/>
</line>
<line x1="163" y1="74" x2="185" y2="63" stroke="rgba(0,255,179,0.4)" stroke-width="1" stroke-dasharray="3,2">
  <animate attributeName="stroke-dashoffset" values="10;0" dur="1.2s" repeatCount="indefinite"/>
</line>
<line x1="165" y1="86" x2="187" y2="94" stroke="rgba(167,139,250,0.4)" stroke-width="1" stroke-dasharray="3,2">
  <animate attributeName="stroke-dashoffset" values="10;0" dur="1.4s" repeatCount="indefinite"/>
</line>
<line x1="150" y1="97" x2="150" y2="115" stroke="rgba(0,212,255,0.4)" stroke-width="1" stroke-dasharray="3,2">
  <animate attributeName="stroke-dashoffset" values="10;0" dur="1.6s" repeatCount="indefinite"/>
</line>
<line x1="135" y1="86" x2="113" y2="94" stroke="rgba(0,255,179,0.4)" stroke-width="1" stroke-dasharray="3,2">
  <animate attributeName="stroke-dashoffset" values="10;0" dur="1.8s" repeatCount="indefinite"/>
</line>
<line x1="137" y1="74" x2="121" y2="63" stroke="rgba(0,212,255,0.4)" stroke-width="1" stroke-dasharray="3,2">
  <animate attributeName="stroke-dashoffset" values="10;0" dur="2s" repeatCount="indefinite"/>
</line>
<rect x="200" y="30" width="82" height="14" rx="4" fill="#111827"/>
<rect x="204" y="34" width="0" height="6" rx="3" fill="rgba(0,212,255,0.5)">
  <animate attributeName="width" values="0;50" dur="1.5s" fill="freeze"/>
</rect>
<rect x="200" y="50" width="82" height="14" rx="4" fill="#111827"/>
<rect x="204" y="54" width="0" height="6" rx="3" fill="rgba(0,255,179,0.4)">
  <animate attributeName="width" values="0;65" dur="1.7s" fill="freeze"/>
</rect>
<rect x="200" y="70" width="82" height="14" rx="4" fill="#111827"/>
<rect x="204" y="74" width="0" height="6" rx="3" fill="rgba(167,139,250,0.4)">
  <animate attributeName="width" values="0;40" dur="1.9s" fill="freeze"/>
</rect>
<text x="150" y="160" font-family="Space Mono,monospace" font-size="8" fill="#a0a0b5" text-anchor="middle">KIMI AI 2026</text>"""


# ── BUILD BLOG CARD ────────────────────────────────────────────
def blog_card(path, slug_prefix="blog/"):
    title, desc, date, mins = extract(path)
    url  = f"{SITE}/{slug_prefix}{path.name}"
    s    = path.stem
    info = get_tag(s, title)
    tc, bg, border, tag_t = info[1], info[2], info[3], info[0]
    t    = (s+title).lower()
    cats = []
    if "kimi" in t: cats.append("kimi")
    if any(k in t for k in ["website","web","build"]): cats.append("web")
    if any(k in t for k in ["cod","develop"]): cats.append("coding")
    if any(k in t for k in ["tool","free","best"]): cats.append("tools")
    if any(k in t for k in ["begin","tutorial","how"]): cats.append("guide")
    if not cats: cats = ["ai"]
    dc = " ".join(cats)

    return f'''<a class="card fade live-card" data-cat="{dc}" href="{url}">
  <div class="cimg">
    <svg height="100%" viewBox="0 0 300 180" width="100%" xmlns="http://www.w3.org/2000/svg">
      {get_svg(s, title)}
    </svg>
  </div>
  <div class="cbdy">
    <span class="ctag" style="color:{tc};background:{bg};border:1px solid {border}">{tag_t}</span>
    <h2>{title}</h2>
    <p>{desc}</p>
    <div class="cmeta">
      <div class="cinfo">
        <div class="av">PL</div>
        <div>
          <div class="caut">{AUTHOR}</div>
          <div class="cdate">{date} · {mins} min</div>
        </div>
      </div>
      <span class="rarrow">Read →</span>
    </div>
  </div>
</a>'''


# ── BUILD GUIDE CARD ───────────────────────────────────────────
def guide_card(path, slug_prefix="blog/"):
    title, desc, date, mins = extract(path)
    url  = f"{SITE}/{slug_prefix}{path.name}"
    s    = path.stem
    info = get_tag(s, title)
    tc, bg, border, tag_t = info[1], info[2], info[3], info[0]
    t    = (s+title).lower()
    cats = []
    if "kimi" in t: cats.append("tools")
    if any(k in t for k in ["begin","how","tutorial"]): cats.append("prompts")
    if any(k in t for k in ["website","web"]): cats.append("tools")
    if not cats: cats = ["tools"]
    dc = " ".join(set(cats))
    chapters = max(4, min(9, mins // 2))
    feat = "featured" if any(k in t for k in ["beginner","complete","full guide","how-to"]) else ""

    return f'''<a href="{url}" class="guide-card {feat} reveal" data-cat="{dc}">
  <div class="gc-graphic">
    <div class="gc-sweep"></div>
    <svg height="152" viewBox="0 0 300 180" width="100%" xmlns="http://www.w3.org/2000/svg" style="position:relative;z-index:1;">
      {get_svg(s, title)}
    </svg>
  </div>
  <div class="gc-body">
    <div class="gc-eyebrow">
      <span class="gc-tag" style="color:{tc};background:{bg};border:1px solid {border}">{tag_t}</span>
      <span class="gc-status live">Live</span>
    </div>
    <div class="gc-title">{title}</div>
    <div class="gc-desc">{desc}</div>
    <div class="gc-footer">
      <div class="gc-chapters"><span class="gc-chapters-dot" style="background:{tc};width:4px;height:4px;border-radius:50%;display:inline-block;margin-right:5px;"></span>{chapters} Chapters · {mins} min read</div>
      <span>{date[:7]}</span>
      <span class="gc-arr">↗</span>
    </div>
  </div>
</a>'''


# ── INJECT INTO PAGE ──────────────────────────────────────────
def inject_cards(page_path, cards_html, start, end):
    if not page_path.exists():
        print(f"  ⚠  {page_path.name} not found — skipping")
        return False
    html = page_path.read_text(encoding="utf-8", errors="ignore")
    if start not in html:
        print(f"  ℹ  Adding markers to {page_path.name}")
        for pat in [
            r'(<div[^>]+id="[^"]*(?:cardGrid|guideGrid|blogGrid|card-grid|blog-grid|guide-grid)[^"]*"[^>]*>)',
            r'(<div[^>]+class="[^"]*(?:card-grid|blog-grid|guide-grid|guide-grid-inner)[^"]*"[^>]*>)',
        ]:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                html = html[:m.end()] + f"\n{start}\n{end}\n" + html[m.end():]
                break
        else:
            html = html.replace("</body>", f"\n{start}\n{end}\n</body>") if "</body>" in html else html + f"\n{start}\n{end}\n"

    new = re.sub(
        re.escape(start) + r'[\s\S]*?' + re.escape(end),
        f"{start}\n{cards_html}\n{end}",
        html
    )
    if new != html:
        page_path.write_text(new, encoding="utf-8")
        return True
    return False


# ── MAIN ──────────────────────────────────────────────────────
def main():
    print("\n" + "═"*58)
    print("  NeuraPulse Card Injector v3.0")
    print("═"*58)

    blog_dir = ROOT / BLOG_DIR
    if blog_dir.exists():
        files = sorted(f for f in blog_dir.glob("*.html") if f.name not in SKIP)
    else:
        print(f"  ⚠  No blog/ dir — scanning root")
        files = sorted(f for f in ROOT.glob("*.html") if f.name not in SKIP)

    print(f"  {len(files)} blog files found\n")
    if not files:
        print("  ❌ No blog .html files found. Put posts in blog/ folder."); return

    bc = "\n".join(blog_card(f) for f in files)
    gc = "\n".join(guide_card(f) for f in files)

    for f in files:
        t, *_ = extract(f)
        print(f"  ✅ {f.stem[:48]:50} → {t[:40]}")

    r1 = inject_cards(ROOT/BLOG_PAGE,  bc, BLOG_START,  BLOG_END)
    r2 = inject_cards(ROOT/GUIDE_PAGE, gc, GUIDE_START, GUIDE_END)

    print(f"\n  {'✅' if r1 else '⚠ '} blog.html  {'updated' if r1 else 'unchanged/missing'}")
    print(f"  {'✅' if r2 else '⚠ '} guide.html {'updated' if r2 else 'unchanged/missing'}")

    # Generate preview file
    prev = ROOT / "card-preview.html"
    prev.write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Card Preview — NeuraPulse</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#08080f;font-family:'Space Grotesk',sans-serif;padding:40px 5%;}}
h1{{color:#00d4ff;font-size:1.3rem;margin-bottom:6px;font-family:'JetBrains Mono',monospace;}}
.sub{{color:#556677;font-size:.82rem;margin-bottom:32px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:22px;margin-bottom:60px;}}
.card{{background:#111827;border:1px solid rgba(0,212,255,.12);border-radius:14px;overflow:hidden;
  text-decoration:none;color:inherit;transition:transform .3s,box-shadow .3s,border-color .3s;display:flex;flex-direction:column;}}
.card:hover{{transform:translateY(-6px);box-shadow:0 20px 50px rgba(0,212,255,.12);border-color:rgba(0,212,255,.3);}}
.cimg{{width:100%;border-bottom:1px solid rgba(0,212,255,.08);}}
.cimg svg{{display:block;width:100%;height:auto;}}
.cbdy{{padding:18px;display:flex;flex-direction:column;flex:1;}}
.ctag{{display:inline-block;font-size:.65rem;font-weight:700;letter-spacing:.1em;padding:3px 10px;border-radius:20px;margin-bottom:10px;}}
.cbdy h2{{font-size:.98rem;font-weight:700;color:#fff;line-height:1.35;margin-bottom:8px;}}
.cbdy p{{color:#8899aa;font-size:.82rem;line-height:1.6;margin-bottom:14px;flex:1;}}
.cmeta{{display:flex;align-items:center;justify-content:space-between;border-top:1px solid rgba(0,212,255,.08);padding-top:12px;}}
.cinfo{{display:flex;align-items:center;gap:10px;}}
.av{{width:30px;height:30px;border-radius:50%;background:rgba(0,212,255,.15);border:1px solid rgba(0,212,255,.3);
  display:flex;align-items:center;justify-content:center;font-size:.65rem;font-weight:700;color:#00d4ff;flex-shrink:0;}}
.caut{{font-size:.77rem;font-weight:600;color:#c9d8e8;}}
.cdate{{font-size:.7rem;color:#556677;}}
.rarrow{{color:#00d4ff;font-size:.85rem;font-weight:600;}}
.fade{{opacity:0;transform:translateY(18px);animation:fu .5s ease forwards;}}
@keyframes fu{{to{{opacity:1;transform:translateY(0)}}}}
.guide-card{{background:#111827;border:1px solid rgba(0,229,255,.1);border-radius:14px;overflow:hidden;
  text-decoration:none;color:inherit;display:flex;flex-direction:column;transition:transform .3s,box-shadow .3s;}}
.guide-card:hover{{transform:translateY(-6px);box-shadow:0 20px 50px rgba(0,229,255,.1);border-color:rgba(0,229,255,.3);}}
.gc-graphic{{border-bottom:1px solid rgba(0,229,255,.08);position:relative;overflow:hidden;}}
.gc-graphic svg{{display:block;width:100%;height:auto;}}
.gc-sweep{{display:none;}}
.gc-body{{padding:18px;display:flex;flex-direction:column;flex:1;}}
.gc-eyebrow{{display:flex;align-items:center;gap:8px;margin-bottom:8px;}}
.gc-tag{{font-size:.62rem;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;padding:3px 10px;border-radius:20px;}}
.gc-status.live{{color:#00ff88;font-size:.62rem;font-weight:700;font-family:'JetBrains Mono',monospace;}}
.gc-title{{font-size:.98rem;font-weight:700;color:#fff;line-height:1.3;margin-bottom:8px;}}
.gc-desc{{font-size:.82rem;color:#666880;line-height:1.6;margin-bottom:14px;flex:1;}}
.gc-footer{{display:flex;align-items:center;justify-content:space-between;border-top:1px solid rgba(0,229,255,.08);padding-top:12px;font-size:.72rem;color:#666880;}}
.gc-chapters{{display:flex;align-items:center;font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#00e5ff;}}
.gc-arr{{color:#666880;font-size:1rem;}}
.reveal{{opacity:0;transform:translateY(22px);animation:fu .5s ease forwards;}}
</style>
</head>
<body>
<h1>📋 Blog Cards Preview — {len(files)} cards</h1>
<p class="sub">Auto-generated {TODAY} · Add markers to blog.html to inject</p>
<p style="color:#8899aa;font-size:.8rem;margin-bottom:24px;">Add <code style="background:#111;padding:2px 6px;border-radius:4px;color:#00d4ff;"><!-- NP:BLOG-CARDS-START --></code> and <code style="background:#111;padding:2px 6px;border-radius:4px;color:#00d4ff;"><!-- NP:BLOG-CARDS-END --></code> inside your card grid div in blog.html</p>
<div class="grid">{bc}</div>
<h1 style="margin-top:40px;">📚 Guide Cards Preview — {len(files)} cards</h1>
<p class="sub">Add markers to guide.html to inject</p>
<div class="grid">{gc}</div>
</body></html>""", encoding="utf-8")

    print(f"\n  ✅ card-preview.html — open this in browser to preview all cards")
    print(f"\n  MARKERS TO ADD IN YOUR HTML:")
    print(f"  blog.html  → inside your card grid: <!-- NP:BLOG-CARDS-START --> <!-- NP:BLOG-CARDS-END -->")
    print(f"  guide.html → inside your guide grid: <!-- NP:GUIDE-CARDS-START --> <!-- NP:GUIDE-CARDS-END -->")
    print(f"\n  Then run: git add . && git commit -m 'Add blog cards' && git push")
    print("═"*58)

if __name__ == "__main__":
    main()
