#!/usr/bin/env python3
"""
Regenerate job-listing sections from the weekly digests.

Run this every time a new digest is published (blog/who-is-hiring-speech-ai-YYYY-MM-DD.html):

    python build_jobs.py

It parses the two most recent digest posts, classifies each role into the
specialty page(s) it matches, and rewrites the content between STJ:* marker
comments in:
  - jobs.html            (latest-digest blurb + full open-roles list)
  - index.html           (homepage "Open roles this week")
  - the 7 specialty pages (voice-biometrics-jobs.html, etc.)
  - blog/speech-recognition-engineer-salary-2026.html (general mini-list)
  - blog/what-is-kaldi-complete-guide-2026.html (open-source-asr mini-list)

Nothing here touches the digest posts themselves — those are still written
by hand from templates/digest-template.html.
"""
import html
import re
import pathlib
from datetime import datetime

REPO = pathlib.Path(__file__).parent
BLOG = REPO / "blog"

DIGEST_RE = re.compile(r"^who-is-hiring-speech-ai-(\d{4})-(\d{2})-(\d{2})\.html$")
DIGESTS_TO_USE = 2          # how many recent weekly digests to pull roles from
JOBS_PAGE_MAX = 20          # cap on /jobs
HOME_MAX = 6                # cap on homepage
SPECIALTY_MAX = 4           # cap per specialty page
BLOG_MINI_MAX = 3           # cap on blog "next steps" mini-lists

SPECIALTY_LABELS = {
    "whisper-jobs": "Whisper",
    "open-source-asr-jobs": "Open Source ASR",
    "asr-research-jobs": "ASR Research",
    "embedded-voice-ai-jobs": "Embedded Voice AI",
    "speech-analytics-jobs": "Speech Analytics",
    "spoken-nlp-jobs": "Spoken NLP",
    "voice-biometrics-jobs": "Voice Biometrics",
}

SPECIALTY_KEYWORDS = {
    "whisper-jobs": ["whisper"],
    "open-source-asr-jobs": [
        "kaldi", "espnet", "vosk", "open source", "open-source", "self-host",
        "data & platform", "ml data", "platform engineer",
    ],
    "asr-research-jobs": [
        "research scientist", "self-supervised", "wav2vec", "hubert", "conformer",
        "rnn-t", "phd", "foundation model", "spatial audio", "research",
    ],
    "embedded-voice-ai-jobs": [
        "on-device", "edge device", "edge devices", "embedded", "firmware",
        "tflite", "quantization", "dsp", "non-nvidia", "hardware",
    ],
    "speech-analytics-jobs": [
        "speech analytics", "conversation intelligence", "contact center",
        "call center", "revenue intelligence", "communications capture",
    ],
    "spoken-nlp-jobs": [
        "conversational ai", "nlu", "intent", "dialogue", "voice agent",
        "voice interface", "forward deployed", "voice-ai",
    ],
    "voice-biometrics-jobs": [
        "speaker verification", "voice biometric", "anti-spoof", "antispoof",
        "deepfake", "liveness",
    ],
}


def find_digests():
    files = []
    for f in BLOG.glob("who-is-hiring-speech-ai-*.html"):
        m = DIGEST_RE.match(f.name)
        if m:
            y, mo, d = map(int, m.groups())
            files.append((datetime(y, mo, d), f))
    files.sort(key=lambda x: x[0], reverse=True)
    return files


def parse_digest(ddate, path):
    s = path.read_text(encoding="utf-8")
    label = f"Who's Hiring in Speech AI — {ddate.strftime('%B')} {ddate.day}, {ddate.year}"
    digest_url = f"/blog/{path.stem}"
    roles = []
    for h2 in re.finditer(r"<h2>(.*?)</h2>\s*<ul>(.*?)</ul>", s, re.S):
        category = html.unescape(h2.group(1)).strip()
        ul = h2.group(2)
        for li in re.finditer(r"<li>(.*?)</li>", ul, re.S):
            block = li.group(1)
            ms = re.search(r"<strong>(.*?)</strong>", block, re.S)
            if not ms:
                continue
            strong = re.sub(r"\s+", " ", ms.group(1)).strip()
            if "&mdash;" in strong:
                title_raw, company_raw = strong.rsplit("&mdash;", 1)
            elif "—" in strong:
                title_raw, company_raw = strong.rsplit("—", 1)
            else:
                title_raw, company_raw = strong, ""
            title_raw = title_raw.strip()
            company_raw = company_raw.strip()

            mloc = re.search(r'<span class="role-loc">(.*?)</span>', block, re.S)
            meta_html = re.sub(r"\s+", " ", mloc.group(1)).strip() if mloc else ""

            ma = re.search(r'<a href="([^"]+)"[^>]*>', block)
            role_url = ma.group(1) if ma else "#"

            note = ""
            if mloc:
                after = block[mloc.end():]
                after = re.sub(r"^\s*<br\s*/?>", "", after, count=1).strip()
                idx = after.find("<a ")
                note = after[:idx].strip() if idx != -1 else after.strip()
                note = re.sub(r"\s+", " ", note)

            roles.append({
                "title": title_raw,
                "company": company_raw,
                "meta": meta_html,
                "note": note,
                "url": role_url,
                "category": category,
                "ddate": ddate,
                "digest_label": label,
                "digest_url": digest_url,
            })
    return label, digest_url, roles


def classify(role):
    text = f"{role['title']} {role['note']} {role['category']}".lower()
    hits = []
    for slug, kws in SPECIALTY_KEYWORDS.items():
        score = sum(1 for k in kws if k in text)
        if score:
            hits.append((slug, score))
    hits.sort(key=lambda x: -x[1])
    return [s for s, _ in hits]


def truncate(text, n):
    if len(text) <= n:
        return text
    cut = text[:n]
    amp = cut.rfind("&")
    if amp != -1 and ";" not in cut[amp:]:
        cut = cut[:amp]
    sp = cut.rfind(" ")
    if sp > n * 0.6:
        cut = cut[:sp]
    return cut.rstrip() + "…"


def render_card(role, note_chars=None):
    posted = f"{role['ddate'].strftime('%b')} {role['ddate'].day}"
    note = role["note"]
    if note_chars:
        note = truncate(note, note_chars)
    note_html = f'<div style="font-size:13px;color:var(--fg);margin-top:8px;">{note}</div>' if note else ""
    meta = f" {role['meta']}" if role["meta"] else ""
    return (
        f'<a href="{role["url"]}" target="_blank" rel="noopener" '
        f'style="display:block;background:#fff;border:1px solid var(--border);border-radius:8px;'
        f'padding:18px 22px;margin-bottom:12px;text-decoration:none;color:var(--fg);">'
        f'<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:baseline;">'
        f'<span style="font-size:16px;font-weight:600;">{role["title"]}</span>'
        f'<span style="font-size:12px;color:var(--muted);white-space:nowrap;">Posted {posted}</span>'
        f'</div>'
        f'<div style="font-size:14px;color:var(--muted);margin-top:2px;">{role["company"]}{meta}</div>'
        f'{note_html}'
        f'<div style="font-size:12px;color:var(--accent);font-weight:600;margin-top:10px;">View posting &rarr;</div>'
        f'</a>'
    )


def render_list(roles, note_chars=None, empty_html=""):
    if not roles:
        return empty_html
    return "\n".join(render_card(r, note_chars) for r in roles)


def replace_marker(text, name, new_inner, path_for_error, allow_missing=False):
    pattern = re.compile(
        r"(<!--\s*STJ:" + re.escape(name) + r"(?::[a-z0-9-]+)?\s*-->)(.*?)(<!--\s*/STJ:" + re.escape(name) + r"\s*-->)",
        re.S,
    )
    new_text, count = pattern.subn(lambda m: m.group(1) + new_inner + m.group(3), text)
    if count == 0 and not allow_missing:
        raise RuntimeError(f"marker STJ:{name} not found in {path_for_error}")
    return new_text


def replace_marker_by_slug(text, name, slug, new_inner, path_for_error):
    pattern = re.compile(
        r"(<!--\s*STJ:" + re.escape(name) + r":" + re.escape(slug) + r"\s*-->)(.*?)(<!--\s*/STJ:" + re.escape(name) + r"\s*-->)",
        re.S,
    )
    new_text, count = pattern.subn(lambda m: m.group(1) + new_inner + m.group(3), text)
    if count == 0:
        raise RuntimeError(f"marker STJ:{name}:{slug} not found in {path_for_error}")
    return new_text


def main():
    digests = find_digests()
    if not digests:
        print("No digest posts found under blog/. Nothing to do.")
        return

    latest_date, latest_path = digests[0]
    latest_label, latest_url, latest_roles = parse_digest(latest_date, latest_path)

    pool = []
    used = digests[:DIGESTS_TO_USE]
    for ddate, path in used:
        _, _, roles = parse_digest(ddate, path)
        pool.extend(roles)
    pool.sort(key=lambda r: r["ddate"], reverse=True)

    by_specialty = {slug: [] for slug in SPECIALTY_LABELS}
    for role in pool:
        for slug in classify(role):
            if len(by_specialty[slug]) < 50:
                by_specialty[slug].append(role)

    # ---- jobs.html ----
    jobs_path = REPO / "jobs.html"
    s = jobs_path.read_text(encoding="utf-8")
    digest_block = (
        f'\n                <div>\n'
        f'                    <strong>Latest digest</strong><br>\n'
        f'                    <span>{latest_label} &middot; {len(latest_roles)} roles</span>\n'
        f'                </div>\n'
        f'                <a href="{latest_url}">Read it</a>\n                '
    )
    s = replace_marker(s, "LATEST_DIGEST", digest_block, jobs_path)
    listings = render_list(pool[:JOBS_PAGE_MAX])
    s = replace_marker(s, "JOB_LISTINGS", "\n" + listings + "\n", jobs_path)
    jobs_path.write_text(s, encoding="utf-8")
    print(f"jobs.html: {len(pool[:JOBS_PAGE_MAX])} roles listed")

    # ---- index.html ----
    idx_path = REPO / "index.html"
    s = idx_path.read_text(encoding="utf-8")
    listings = render_list(pool[:HOME_MAX])
    s = replace_marker(s, "JOB_LISTINGS", "\n" + listings + "\n", idx_path)
    idx_path.write_text(s, encoding="utf-8")
    print(f"index.html: {len(pool[:HOME_MAX])} roles listed")

    # ---- specialty pages ----
    for slug, label in SPECIALTY_LABELS.items():
        page_path = REPO / f"{slug}.html"
        if not page_path.exists():
            continue
        s = page_path.read_text(encoding="utf-8")
        roles = by_specialty[slug][:SPECIALTY_MAX]
        empty = (
            f'<p><strong>Live openings:</strong> no {label} roles in this week’s digest &mdash; '
            f'<a href="/jobs">see all open roles</a> or <a href="#newsletter">get the next digest</a>.</p>'
        )
        if roles:
            intro = (
                f'<p style="margin-bottom:16px;"><strong>Live openings:</strong> '
                f'{len(roles)} {label} role{"s" if len(roles) != 1 else ""} from the last '
                f'{DIGESTS_TO_USE} digests &mdash; <a href="/jobs">see all open roles</a>.</p>'
            )
            inner = intro + "\n" + render_list(roles)
        else:
            inner = empty
        s = replace_marker_by_slug(s, "SPECIALTY_JOBS", slug, inner, page_path)
        page_path.write_text(s, encoding="utf-8")
        print(f"{slug}.html: {len(roles)} roles listed")

    # ---- blog mini-lists ----
    blog_targets = [
        (BLOG / "speech-recognition-engineer-salary-2026.html", "general", pool[:BLOG_MINI_MAX]),
        (BLOG / "what-is-kaldi-complete-guide-2026.html", "open-source-asr-jobs", by_specialty["open-source-asr-jobs"][:BLOG_MINI_MAX]),
    ]
    for path, slug, roles in blog_targets:
        if not path.exists():
            continue
        s = path.read_text(encoding="utf-8")
        if roles:
            inner = render_list(roles, note_chars=140)
        else:
            inner = '<p style="font-size:14px;">No matching roles in this week’s digest &mdash; <a href="/jobs">see all open roles</a>.</p>'
        s = replace_marker_by_slug(s, "BLOG_JOBS", slug, "\n" + inner + "\n", path)
        path.write_text(s, encoding="utf-8")
        print(f"{path.name}: {len(roles)} roles listed")

    print(f"\nDone. Latest digest: {latest_label} ({len(latest_roles)} roles). Pool: {len(pool)} roles from {len(used)} digests.")


if __name__ == "__main__":
    main()
