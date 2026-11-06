#!/usr/bin/env python3
"""
Build /speech-ai-salaries from the pay ranges in the role archive.

    python fetch_jobs.py        # refresh data/jobs-archive.json first
    python build_salaries.py    # writes speech-ai-salaries.html

Uses every open role in data/jobs-archive.json that lists an annual USD
range. The page shell (head, nav, analytics, newsletter form, footer) is
copied from jobs.html so styling and tracking match the rest of the site.
"""
import html
import json
import pathlib
import re
import statistics
from datetime import date

REPO = pathlib.Path(__file__).parent
ARCHIVE = REPO / "data" / "jobs-archive.json"
OUT = REPO / "speech-ai-salaries.html"
URL = "https://speechtechjobs.com/speech-ai-salaries"

GROUPS = [  # first match wins
    ("Leadership & management", re.compile(r"\b(director|head of|manager|vp|principal)\b", re.I)),
    ("Solutions & forward-deployed engineering", re.compile(r"solutions|forward[- ]deployed|sales engineer|customer|conversational design", re.I)),
    ("Research scientists & research engineers", re.compile(r"research|scientist", re.I)),
    ("ML, inference & data engineering", re.compile(r"machine learning|\bml\b|applied ai|model|inference|training|\bdata\b|speech llm", re.I)),
    ("Software & audio engineering", re.compile(r"engineer|developer|architect", re.I)),
]
NUM = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*([Kk])?")


def parse_pay(s):
    """'$150K - $250K', '$160,000 — $185,000' -> (150000, 250000); None if not annual USD."""
    if not s or re.search(r"[£€]|CAD|AUD|GBP|EUR|/\s*h(ou)?r|hourly|per hour", s, re.I):
        return None
    vals = []
    for n, k in NUM.findall(s)[:2]:
        v = float(n.replace(",", ""))
        vals.append(v * 1000 if k else v)
    if len(vals) != 2:
        return None
    lo, hi = sorted(vals)
    if lo < 30000 or hi > 1_000_000:
        return None
    return int(lo), int(hi)


def k(v):
    return f"${round(v / 1000):,}K"


def group_of(title):
    for name, rx in GROUPS:
        if rx.search(title):
            return name
    return None


def main():
    archive = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    rows, seen = [], set()
    for r in archive.values():
        if not r.get("active"):
            continue
        pay = parse_pay(r.get("pay"))
        g = group_of(r["title"])
        key = (r["company"], r["title"].lower())
        if not pay or not g or key in seen:
            continue
        seen.add(key)
        rows.append(dict(r, lo=pay[0], hi=pay[1], mid=(pay[0] + pay[1]) / 2, group=g))
    if not rows:
        raise SystemExit("No roles with USD pay ranges in the archive. Run fetch_jobs.py first.")

    today = date.today()
    updated = f"{today.strftime('%B')} {today.day}, {today.year}"
    companies = sorted({r["company"] for r in rows})
    overall_mid = statistics.median(r["mid"] for r in rows)

    stat_rows, sections = [], []
    for name, _ in GROUPS:
        g = sorted([r for r in rows if r["group"] == name], key=lambda r: -r["mid"])
        if not g:
            continue
        med_lo = statistics.median(r["lo"] for r in g)
        med_hi = statistics.median(r["hi"] for r in g)
        stat_rows.append(
            f"<tr><td>{html.escape(name)}</td><td>{len(g)}</td>"
            f"<td><strong>{k(med_lo)} &ndash; {k(med_hi)}</strong></td>"
            f"<td>{k(min(r['lo'] for r in g))} &ndash; {k(max(r['hi'] for r in g))}</td></tr>")
        items = "\n".join(
            f'<tr><td>{html.escape(r["title"])}</td><td>{html.escape(r["company"])}</td>'
            f'<td>{k(r["lo"])} &ndash; {k(r["hi"])}</td>'
            f'<td><a class="inline" href="{html.escape(r["url"])}" rel="nofollow noopener" target="_blank">Posting</a></td></tr>'
            for r in g)
        sections.append(
            f'<h3>{html.escape(name)}</h3>\n<div class="sal-wrap"><table class="sal">'
            f"<thead><tr><th>Role</th><th>Company</th><th>Posted range</th><th></th></tr></thead>"
            f"<tbody>\n{items}\n</tbody></table></div>")

    content = f"""
    <section class="section">
        <div class="container">
            <h1>Speech AI salaries 2026: pay ranges from live job postings</h1>
            <p class="sal-updated">Updated {updated} from <strong>{len(rows)} open roles</strong> at
            <strong>{len(companies)} speech and voice AI companies</strong> that publish pay ranges.</p>
            <p>These are the base salary ranges employers state in their own job postings: ASR,
            text-to-speech, voice agents and audio ML roles. Most come from US pay-transparency rules, so they're
            US ranges; equity and bonus come on top. The median posted midpoint across every role is
            <strong>{k(overall_mid)}</strong>.</p>

            <h2>Median posted range by role type</h2>
            <div class="sal-wrap"><table class="sal">
                <thead><tr><th>Role type</th><th>Roles</th><th>Median range</th><th>Lowest &ndash; highest</th></tr></thead>
                <tbody>
                {''.join(stat_rows)}
                </tbody>
            </table></div>
            <p class="sal-note">Median range = the median of the posted minimums and the median of the
            posted maximums. Roles posted in several cities are counted once.</p>

            <p>Want an estimate for your own level and location? Try the
            <a class="inline" href="/salary-estimator">salary estimator</a>. For the roles behind these numbers,
            each week's openings are in the <a class="inline" href="/jobs">Speech AI jobs digest</a>.</p>

            <h2>Every role behind the numbers</h2>
            {''.join(sections)}

            <h2>How this data is collected</h2>
            <p>Each week we pull open roles from the career pages of the speech-AI companies we track and keep
            the speech, voice and audio roles. Only annual US-dollar ranges stated in the posting are used, with
            no estimates or self-reported numbers. The page is rebuilt every time the jobs data refreshes, so roles
            that close drop out.</p>
        </div>
    </section>
"""
    shell = (REPO / "jobs.html").read_text(encoding="utf-8")
    title = "Speech AI Salaries 2026: Pay Ranges From Live Job Postings | SpeechTechJobs"
    desc = (f"Real pay ranges from {len(rows)} open speech and voice AI roles at {len(companies)} companies: "
            f"ASR, TTS, voice agents and audio ML. Median posted midpoint {k(overall_mid)}. Updated {updated}.")
    s = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", shell, count=1, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + html.escape(desc), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + html.escape(title), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + html.escape(desc), s, count=1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + URL, s, count=1)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + URL, s, count=1)
    s = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
    css = """
        .sal-wrap { overflow-x: auto; margin: 12px 0 8px; }
        table.sal { border-collapse: collapse; width: 100%; font-size: 14px; background: #fff; }
        table.sal th, table.sal td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
        table.sal th { font-size: 12px; text-transform: uppercase; letter-spacing: .5px; color: var(--muted); }
        .sal-updated { color: var(--muted); margin: 8px 0 16px; }
        .sal-note { font-size: 13px; color: var(--muted); }
        h3 { margin-top: 28px; }
    </style>"""
    s = s.replace("</style>", css, 1)
    # Body: keep nav, newsletter form and footer from jobs.html; swap the page content.
    head_end = s.index("</header>") + len("</header>")
    foot = s.index("<footer>")
    signup = re.search(r'<div class="signup" id="newsletter">.*?</form>\s*</div>', s, re.S).group(0)
    signup_section = f'\n    <section class="section">\n        <div class="container">\n            {signup}\n        </div>\n    </section>\n\n    '
    s = s[:head_end] + "\n" + content + signup_section + s[foot:]
    OUT.write_text(s, encoding="utf-8")
    print(f"{OUT.name}: {len(rows)} roles, {len(companies)} companies, median midpoint {k(overall_mid)}")


if __name__ == "__main__":
    main()
