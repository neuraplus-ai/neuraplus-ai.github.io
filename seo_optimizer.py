import os
import glob
import json
from bs4 import BeautifulSoup

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SITE_URL       = "https://neuraplus-ai.github.io"
SITE_NAME      = "NeuraPlusAI"
OG_IMAGE       = f"{SITE_URL}/favicon.svg"
TWITTER_HANDLE = "@neuraplus_ai"

PAGE_SEO = {
    "index.html": {
        "title": "NeuraPlusAI – AI-Powered Tools for Everyone",
        "description": "NeuraPlusAI offers cutting-edge artificial intelligence tools to boost productivity, creativity, and automation for individuals and businesses.",
        "keywords": "AI tools, artificial intelligence, automation, productivity, NeuraPlusAI",
        "schema_type": "WebSite",
    },
    "about.html": {
        "title": "About NeuraPlusAI – Our Mission & Team",
        "description": "Learn about NeuraPlusAI's mission to democratize artificial intelligence and the passionate team behind our AI-powered platform.",
        "keywords": "about NeuraPlusAI, AI mission, AI team, artificial intelligence company",
        "schema_type": "WebPage",
    },
    "contact.html": {
        "title": "Contact NeuraPlusAI – Get in Touch",
        "description": "Have questions or feedback? Contact the NeuraPlusAI team. We'd love to hear from you and help you with your AI journey.",
        "keywords": "contact NeuraPlusAI, AI support, get in touch, AI help",
        "schema_type": "WebPage",
    },
    "blog.html": {
        "title": "NeuraPlusAI Blog – AI News, Tips & Insights",
        "description": "Explore the NeuraPlusAI blog for the latest articles on artificial intelligence, machine learning trends, tutorials, and industry insights.",
        "keywords": "AI blog, artificial intelligence news, machine learning tips, NeuraPlusAI blog",
        "schema_type": "WebPage",
    },
    "privacy-policy.html": {
        "title": "Privacy Policy – NeuraPlusAI",
        "description": "Read NeuraPlusAI's privacy policy to understand how we collect, use, and protect your personal information.",
        "keywords": "privacy policy, NeuraPlusAI privacy, data protection, user data",
        "schema_type": "WebPage",
    },
}

BLOG_DEFAULT = {
    "title": "NeuraPlusAI Blog Post – AI Insights",
    "description": "Read this insightful article on artificial intelligence from the NeuraPlusAI blog.",
    "keywords": "AI blog, artificial intelligence, NeuraPlusAI",
    "schema_type": "BlogPosting",
}
# ──────────────────────────────────────────────────────────────────────────────


def get_page_url(filepath):
    rel = filepath.replace("\\", "/").lstrip("./")
    if rel == "index.html":
        return SITE_URL + "/"
    return f"{SITE_URL}/{rel}"


def set_meta(head, soup, attrs, value):
    """Find or create a <meta> tag. Avoids the 'name' conflict bug."""
    existing = head.find("meta", attrs=attrs)
    if existing:
        existing["content"] = value
    else:
        tag = soup.new_tag("meta")
        for k, v in attrs.items():
            tag[k] = v
        tag["content"] = value
        head.append(tag)


def set_link(head, soup, rel_value, attr, value):
    """Find or create a <link> tag."""
    existing = head.find("link", rel=rel_value)
    if existing:
        existing[attr] = value
    else:
        tag = soup.new_tag("link")
        tag["rel"] = rel_value
        tag[attr] = value
        head.append(tag)


def build_schema(schema_type, title, description, url):
    base = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": title,
        "description": description,
        "url": url,
    }
    if schema_type == "WebSite":
        base["potentialAction"] = {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/?s={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    if schema_type == "BlogPosting":
        base["headline"] = title
        base["author"] = {"@type": "Organization", "name": SITE_NAME}
        base["publisher"] = {
            "@type": "Organization",
            "name": SITE_NAME,
            "logo": {"@type": "ImageObject", "url": OG_IMAGE}
        }
    return base


def inject_seo(filepath, seo):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    soup = BeautifulSoup(content, "lxml")
    head = soup.find("head")
    if not head:
        print(f"  ⚠️  No <head> in {filepath}, skipping.")
        return

    title_text  = seo["title"]
    desc_text   = seo["description"]
    kw_text     = seo["keywords"]
    page_url    = get_page_url(filepath)
    schema_type = seo.get("schema_type", "WebPage")

    # charset
    if not head.find("meta", charset=True):
        ct = soup.new_tag("meta")
        ct["charset"] = "UTF-8"
        head.insert(0, ct)

    # viewport
    if not head.find("meta", attrs={"name": "viewport"}):
        vp = soup.new_tag("meta")
        vp["name"] = "viewport"
        vp["content"] = "width=device-width, initial-scale=1.0"
        head.append(vp)

    # <title>
    t = head.find("title")
    if t:
        t.string = title_text
    else:
        t = soup.new_tag("title")
        t.string = title_text
        head.append(t)

    # basic meta
    set_meta(head, soup, {"name": "description"}, desc_text)
    set_meta(head, soup, {"name": "keywords"},    kw_text)
    set_meta(head, soup, {"name": "robots"},      "index, follow")
    set_link(head, soup, "canonical",             "href", page_url)

    # Open Graph
    set_meta(head, soup, {"property": "og:type"},         "website")
    set_meta(head, soup, {"property": "og:site_name"},    SITE_NAME)
    set_meta(head, soup, {"property": "og:title"},        title_text)
    set_meta(head, soup, {"property": "og:description"},  desc_text)
    set_meta(head, soup, {"property": "og:url"},          page_url)
    set_meta(head, soup, {"property": "og:image"},        OG_IMAGE)
    set_meta(head, soup, {"property": "og:image:width"},  "1200")
    set_meta(head, soup, {"property": "og:image:height"}, "630")

    # Twitter Card
    set_meta(head, soup, {"name": "twitter:card"},        "summary_large_image")
    set_meta(head, soup, {"name": "twitter:title"},       title_text)
    set_meta(head, soup, {"name": "twitter:description"}, desc_text)
    set_meta(head, soup, {"name": "twitter:image"},       OG_IMAGE)
    set_meta(head, soup, {"name": "twitter:site"},        TWITTER_HANDLE)

    # JSON-LD Schema — remove old first
    for old in head.find_all("script", attrs={"type": "application/ld+json"}):
        old.decompose()
    schema_tag = soup.new_tag("script")
    schema_tag["type"] = "application/ld+json"
    schema_tag.string = json.dumps(build_schema(schema_type, title_text, desc_text, page_url), indent=2)
    head.append(schema_tag)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"  ✅ {filepath}")


def main():
    html_files = list(set(glob.glob("**/*.html", recursive=True) + glob.glob("*.html")))
    html_files = [f for f in html_files if "google" not in f.lower()]

    print(f"\n🔍 Found {len(html_files)} HTML files\n")

    for filepath in sorted(html_files):
        filename = os.path.basename(filepath)

        if filename in PAGE_SEO:
            seo = PAGE_SEO[filename]
        elif "blog" in filepath.lower():
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
            temp = BeautifulSoup(raw, "lxml")
            h1 = temp.find("h1")
            seo = BLOG_DEFAULT.copy()
            if h1:
                h1_text = h1.get_text(strip=True)
                seo["title"]       = f"{h1_text} – NeuraPlusAI Blog"
                seo["description"] = f"Read '{h1_text}' on the NeuraPlusAI blog."
        else:
            name = filename.replace(".html", "").replace("-", " ").title()
            seo = {
                "title":       f"{name} – NeuraPlusAI",
                "description": f"NeuraPlusAI – {name} page.",
                "keywords":    f"NeuraPlusAI, {name}",
                "schema_type": "WebPage",
            }

        inject_seo(filepath, seo)

    print("\n🎉 SEO optimization complete!\n")


if __name__ == "__main__":
    main()
