#!/usr/bin/env python3
"""
Build the paste-ready Brevo email body for a weekly digest, straight from the
published digest page.

    python make_email.py               # newest digest in blog/
    python make_email.py 2026-11-17    # a specific issue

Writes data/email/YYYY-MM-DD.html: the intro, each section heading and its
one-line takeaway, then every role with its title linked to that role's anchor
on the digest page. Every link back to the site carries
utm_source=newsletter&utm_medium=email&utm_campaign=digest-YYYY-MM-DD, so GA4
can show which issues bring visits and signups. Styles are inline so they
survive Brevo's editor.

In Brevo: add an HTML/code block, paste the file's contents, and turn off
Brevo's Google Analytics link tracking for the campaign (it would overwrite
these UTMs).
"""
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).parent
BLOG = REPO / "blog"
OUT = REPO / "data" / "email"
DIGEST_RE = re.compile(r"^who-is-hiring-speech-ai-(\d{4}-\d{2}-\d{2})\.html$")
SECTION_RE = re.compile(
    r'<h2>(.*?)</h2>\s*(?:<p class="section-lead">(.*?)</p>\s*)?<ul>(.*?)</ul>', re.S)
ROLE_RE = re.compile(
    r'<li id="([^"]+)"><strong>(.*?)</strong>\s*<span class="role-loc">(.*?)</span><br>(.*?)<a href', re.S)


def clean(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        dates = sorted(m.group(1) for f in BLOG.iterdir() if (m := DIGEST_RE.match(f.name)))
        if not dates:
            sys.exit("No digests found in blog/.")
        date = dates[-1]
    page_path = BLOG / f"who-is-hiring-speech-ai-{date}.html"
    if not page_path.exists():
        sys.exit(f"Not found: {page_path.relative_to(REPO)}")
    page = page_path.read_text(encoding="utf-8")

    base = f"https://speechtechjobs.com/blog/who-is-hiring-speech-ai-{date}"
    utm = f"utm_source=newsletter&utm_medium=email&utm_campaign=digest-{date}"

    def digest_link(anchor=""):
        return f"{base}?{utm}" + (f"#{anchor}" if anchor else "")

    def site_link(path):
        return f"https://speechtechjobs.com{path}?{utm}"

    body = page[page.index('<div class="article-content">'):page.index("<!-- STJ:DIGEST_NAV -->")]
    intro = re.search(r"<p>(.*?)</p>", body, re.S).group(1)
    parts = [f'<p style="font-size:16px;line-height:1.6;margin:0 0 20px;">{clean(intro)}</p>']
    n_roles = 0
    for sec in SECTION_RE.finditer(body):
        h2, lead, ul = sec.groups()
        parts.append(f'<h2 style="font-size:20px;margin:28px 0 8px;">{h2}</h2>')
        if lead:
            lead = re.sub(r'href="(/[^"]*)"', lambda a: f'href="{site_link(a.group(1))}"', clean(lead))
            parts.append(f'<p style="font-size:15px;color:#555;line-height:1.5;margin:0 0 14px;">{lead}</p>')
        for role in ROLE_RE.finditer(ul):
            anchor, title, meta, note = role.groups()
            meta = re.sub(r"^&middot;\s*", "", clean(meta))
            parts.append(
                f'<p style="font-size:15px;line-height:1.55;margin:0 0 16px;">'
                f'<a href="{digest_link(anchor)}" style="color:#0066ff;font-weight:600;text-decoration:none;">{clean(title)}</a>'
                f'<br><span style="color:#737373;font-size:13px;">{meta}</span>'
                f'<br>{clean(note)}</p>')
            n_roles += 1
    parts.append(f'<p style="font-size:15px;margin:28px 0 8px;"><strong>What do these roles pay?</strong> '
                 f'<a href="{site_link("/speech-ai-salaries")}">Speech AI salaries by role</a>, '
                 f'from the pay ranges in live postings.</p>')
    parts.append(f'<p style="font-size:15px;margin:0 0 8px;"><strong>Hiring for a speech-tech role?</strong> '
                 f'<a href="{site_link("/hire-talent")}">Tell us about it</a> and we\'ll include it in the digest.</p>')
    parts.append(f'<p style="font-size:15px;margin:0;"><a href="{digest_link()}">Read this issue on the web</a></p>')

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{date}.html"
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"{n_roles} roles -> {out.relative_to(REPO)}")
    print(f"Web link: {digest_link()}")


if __name__ == "__main__":
    main()
