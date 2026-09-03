#!/usr/bin/env python3
"""
Regenerate feed.xml from blog/*.html.

Run after publishing a post:
    python gen_feed.py

Pulls title, meta description, canonical URL, publish date and category from
each blog post. Newest first. Writes feed.xml at the repo root.
"""
import html
import re
import pathlib
from datetime import datetime, timezone
from xml.sax.saxutils import escape

REPO = pathlib.Path(__file__).parent
BLOG = REPO / "blog"
SITE = "https://speechtechjobs.com"
FEED_URL = f"{SITE}/feed.xml"
MAX_ITEMS = 25
DEFAULT_DATE = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}


def text(s):
    """HTML entities -> unicode, then XML-escape the significant chars."""
    return escape(html.unescape(s or "")).strip()


def find_date(s):
    m = re.search(r'"datePublished"\s*:\s*"(\d{4})-(\d{2})-(\d{2})"', s)
    if m:
        y, mo, d = map(int, m.groups())
        return datetime(y, mo, d, 12, 0, tzinfo=timezone.utc)
    for pat in (r'<span>([A-Z][a-z]+) (\d{1,2}), (\d{4})</span>',
                r'Last updated:\s*([A-Z][a-z]+) (\d{1,2}), (\d{4})'):
        m = re.search(pat, s)
        if m and m.group(1) in MONTHS:
            return datetime(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)),
                            12, 0, tzinfo=timezone.utc)
    return DEFAULT_DATE


def clean_title(t):
    return re.sub(r'\s*[|—-]\s*SpeechTechJobs\s*$', '', t).strip()


items = []
for f in BLOG.glob("*.html"):
    if f.name == "index.html":
        continue
    s = f.read_text(encoding="utf-8")
    mt = re.search(r'<title>(.*?)</title>', s, re.S)
    md = re.search(r'<meta name="description" content="(.*?)">', s, re.S)
    mc = re.search(r'<link rel="canonical" href="(https://[^"]+)"', s)
    mcat = re.search(r'<div class="article-category">([^<]+)</div>', s)
    if not (mt and mc):
        print(f"  skip {f.name}: missing title/canonical")
        continue
    items.append({
        "title": clean_title(html.unescape(mt.group(1))),
        "link": mc.group(1),
        "desc": md.group(1) if md else "",
        "date": find_date(s),
        "cat": mcat.group(1).strip() if mcat else None,
    })

items.sort(key=lambda x: x["date"], reverse=True)
items = items[:MAX_ITEMS]

now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
       '  <channel>',
       '    <title>SpeechTechJobs Blog</title>',
       f'    <link>{SITE}/blog</link>',
       '    <description>Guides on speech-technology careers, salaries, interviews, tools, and hiring.</description>',
       '    <language>en-us</language>',
       f'    <lastBuildDate>{now}</lastBuildDate>',
       f'    <atom:link href="{FEED_URL}" rel="self" type="application/rss+xml"/>']
for it in items:
    pub = it["date"].strftime("%a, %d %b %Y %H:%M:%S +0000")
    out += ['', '    <item>',
            f'      <title>{text(it["title"])}</title>',
            f'      <link>{it["link"]}</link>',
            f'      <guid isPermaLink="true">{it["link"]}</guid>',
            f'      <pubDate>{pub}</pubDate>',
            f'      <description>{text(it["desc"])}</description>']
    if it["cat"]:
        out.append(f'      <category>{text(it["cat"])}</category>')
    out.append('    </item>')
out += ['', '  </channel>', '</rss>', '']

(REPO / "feed.xml").write_text("\n".join(out), encoding="utf-8")
print(f"feed.xml: {len(items)} items, newest {items[0]['date'].date()} ({items[0]['title']})")
