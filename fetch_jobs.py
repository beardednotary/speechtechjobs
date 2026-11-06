#!/usr/bin/env python3
"""
Pull speech-AI roles from company job boards (Greenhouse, Lever, Ashby public
APIs), keep a running archive, and draft this week's digest candidates.

    python fetch_jobs.py              # fetch, update archive, write candidates
    python fetch_jobs.py --days 14    # widen the "recent" window (default 10)

Boards live in data/boards.json. Outputs:
  data/jobs-archive.json            every matching role ever seen, with
                                    first_seen / last_seen / closed_on dates
                                    (the raw material for hiring reports)
  data/candidates/YYYY-MM-DD.html   paste-ready <li> items for roles posted in
                                    the window, grouped by a guessed section,
                                    with a description excerpt to write the
                                    one-line note from

The digest is still written by hand: pick roles from the candidates file,
write the note, and paste them into the digest post. build_jobs.py then runs
as before. Companies on Workday or custom career sites are still checked by
hand (see CONTENT-PLAN.md).
"""
import argparse
import concurrent.futures as cf
import html
import json
import pathlib
import re
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

REPO = pathlib.Path(__file__).parent
DATA = REPO / "data"
ARCHIVE = DATA / "jobs-archive.json"
CANDIDATES = DATA / "candidates"
UA = {"User-Agent": "speechtechjobs-fetch/1.0 (+https://speechtechjobs.com)"}

API = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{}/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/{}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{}?includeCompensation=true",
}

SPEECH_TITLE = re.compile(
    r"\b(speech|voice|audio|asr|tts|text[- ]to[- ]speech|speaker|acoustic|diariz\w*|whisper|"
    r"spoken|phonet\w*|transcri\w*|wake[- ]?word|keyword spotting|conversational|dialog(ue)?|"
    r"realtime|real-time|telephony|sound)\b", re.I)
# Titles that are speech-relevant at a speech-native company.
CORE_TITLE = re.compile(
    r"\b(research\w*|scientist|machine learning|ml|applied ai|models?|modeling|inference|training|"
    r"data engineer\w*|embedded|on-device|edge|forward[- ]deployed|solutions (engineer|architect)|"
    r"sales engineer|gpu|cuda|linguist\w*|evals?|audio|speech|voice)\b", re.I)
# Titles that make a description-only match believable at a general AI company.
ML_TITLE = re.compile(r"\b(research\w*|scientist|machine learning|ml|applied ai|models?|inference)\b", re.I)
SPEECH_DESC = re.compile(
    r"\b(speech recognition|asr|text[- ]to[- ]speech|tts|speech|voice|audio|speaker|"
    r"diarization|acoustic|whisper|wav2vec|conformer|spoken)\b", re.I)
SKIP_TITLE = re.compile(r"\b(intern(ship)?|account executive|sdr|bdr|recruit\w*|counsel|"
                        r"paralegal|accountant|payroll|office manager|executive assistant|finance|"
                        r"marketing|web engineer|customer success|support engineer|legal|people|"
                        r"freelance|product designer|it engineer)\b", re.I)
_PLACES = (r"USA|US|UK|United Kingdom|Europe|EMEA|APAC|LATAM|Americas|North America|Remote|Canada|"
           r"Mexico|Colombia|Argentina|Brazil|Sweden|Germany|France|Spain|Poland|Netherlands|"
           r"Ireland|India|Japan|Korea|Singapore|Australia|London|Berlin|New York|San Francisco")
# Location tails that split one role into several postings: " - Austin, TX, USA",
# " - Mexico", " (Singapore)", " [UK - Remote]".
CITY_SUFFIX = re.compile(
    r"\s*(?:[-–—]\s*[^-–—]+,\s*[A-Z]{2}(?:,\s*USA)?"
    r"|[-–—]\s*(?:" + _PLACES + r")(?:\s*[-–—/]\s*(?:" + _PLACES + r"))?"
    r"|\((?:" + _PLACES + r")[^)]*\)|\[[^\]]*\])\s*$", re.I)


def base_title(t):
    prev = None
    while prev != t:
        prev, t = t, CITY_SUFFIX.sub("", t).strip()
    return t

SECTIONS = [  # (section, title regex) — first match wins; edit headings in the digest as usual
    ("Speech & audio research", re.compile(r"research|scientist", re.I)),
    ("Text-to-speech & voice", re.compile(r"\btts\b|text[- ]to[- ]speech|voice (model|clon|design|quality)|audio gen", re.I)),
    ("Voice agents", re.compile(r"agent|conversational|dialog|forward deployed|telephony|realtime|real-time", re.I)),
    ("Speech analytics", re.compile(r"analytic|conversation intelligence|contact center", re.I)),
    ("ASR & speech engineering", re.compile(r".", re.S)),
]

PAY_RE = re.compile(
    r"(?:US)?\$\s?\d{2,3}(?:,\d{3})+(?:\.\d+)?\s*(?:USD)?\s*(?:-|–|—|to)\s*(?:US)?\$?\s?\d{2,3}(?:,\d{3})+(?:\.\d+)?"
    r"|\$\d{2,3}(?:\.\d)?\s?[Kk]\s*(?:-|–|—|to)\s*\$?\d{2,3}(?:\.\d)?\s?[Kk]")


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def strip_html(s):
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def iso_day(v):
    """Epoch ms or ISO string -> YYYY-MM-DD (or None)."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc).date().isoformat()
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return str(v)[:10] or None


def find_pay(text):
    m = PAY_RE.search(text or "")
    return re.sub(r"\s+", " ", m.group(0)).strip() if m else ""


def normalize(board, raw):
    """One ATS posting -> common dict."""
    ats = board["ats"]
    if ats == "greenhouse":
        desc = strip_html(raw.get("content"))
        loc = (raw.get("location") or {}).get("name", "")
        return dict(ext_id=str(raw["id"]), title=raw.get("title", ""), url=raw.get("absolute_url", ""),
                    location=loc, remote=bool(re.search(r"remote", loc, re.I)),
                    posted=iso_day(raw.get("first_published") or raw.get("updated_at")),
                    pay=find_pay(desc), desc=desc)
    if ats == "lever":
        cats = raw.get("categories") or {}
        desc = raw.get("descriptionPlain") or strip_html(raw.get("description"))
        sr = raw.get("salaryRange") or {}
        pay = ""
        if sr.get("min") and sr.get("max"):
            pay = f"${sr['min']:,}–${sr['max']:,} {sr.get('currency', '')}".strip()
        return dict(ext_id=raw["id"], title=raw.get("text", ""), url=raw.get("hostedUrl", ""),
                    location=cats.get("location", ""), remote=raw.get("workplaceType") == "remote",
                    posted=iso_day(raw.get("createdAt")), pay=pay or find_pay(desc), desc=desc)
    # ashby
    comp = raw.get("compensation") or {}
    desc = raw.get("descriptionPlain") or strip_html(raw.get("descriptionHtml"))
    pay = comp.get("scrapeableCompensationSalarySummary") or comp.get("compensationTierSummary") or ""
    return dict(ext_id=raw["id"], title=raw.get("title", ""), url=raw.get("jobUrl", ""),
                location=raw.get("location", ""), remote=bool(raw.get("isRemote")),
                posted=iso_day(raw.get("publishedAt")), pay=pay or find_pay(desc), desc=desc)


def relevant(board, job):
    t = job["title"]
    if SKIP_TITLE.search(t):
        return False
    if SPEECH_TITLE.search(t):
        return True
    if board["focus"] == "speech":
        return bool(CORE_TITLE.search(t))
    return bool(ML_TITLE.search(t)) and len(SPEECH_DESC.findall(job["desc"])) >= 4


def fetch_board(board):
    url = API[board["ats"]].format(urllib.parse.quote(board["token"]))
    d = get_json(url)
    raws = d.get("jobs", []) if isinstance(d, dict) else d
    if board["ats"] == "ashby":
        raws = [r for r in raws if r.get("isListed", True)]
    merged = {}
    for r in raws:
        j = normalize(board, r)
        if not relevant(board, j):
            continue
        base = base_title(j["title"])
        city = j["title"][len(base):].strip(" -–—()[]") if base != j["title"] else ""
        k = base.lower()
        if k in merged:  # same role posted once per city: one record, all locations
            m = merged[k]
            loc = city or j["location"]
            if loc and loc not in m["locations"]:
                m["locations"].append(loc)
            m["posted"] = max(filter(None, [m["posted"], j["posted"]]), default=None)
            continue
        j["title"] = base
        j["locations"] = [city or j["location"]] if (city or j["location"]) else []
        merged[k] = j
    for j in merged.values():
        if len(j["locations"]) > 1:
            j["location"] = f"{j['locations'][0]} + {len(j['locations']) - 1} more"
    return list(merged.values()), len(raws)


def section_for(title):
    for name, rx in SECTIONS:
        if rx.search(title):
            return name
    return SECTIONS[-1][0]


ROLE_START = re.compile(r"\b(about the role|the role|role overview|what you'll do|what you will do|"
                        r"the opportunity|your role|responsibilities|in this role|position overview)\b", re.I)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def li(job):
    loc = job["location"] or ("Remote" if job["remote"] else "")
    meta = " &middot; ".join(x for x in [html.escape(loc), html.escape(job["pay"])] if x)
    desc = re.sub(r"\s+", " ", job["desc"])
    m = ROLE_START.search(desc)  # skip the company boilerplate when we can
    desc = desc[m.start():] if m else desc
    excerpt = html.escape(desc[:600]) + ("…" if len(desc) > 600 else "")
    return (
        f'                    <li id="{slug(job["company"] + "-" + job["title"])}"><strong>{html.escape(job["title"])} &mdash; {html.escape(job["company"])}</strong>\n'
        f'                        <span class="role-loc">&middot; {meta}</span><br>\n'
        f'                        TODO: one-line note.\n'
        f'                        <a href="{html.escape(job["url"])}">View posting</a></li>\n'
        f'                    <!-- posted {job["posted"]} · first seen {job["first_seen"]} · excerpt: {excerpt.replace("--", "–")} -->\n'
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=10, help="'recent' window for candidates")
    args = ap.parse_args()
    today = date.today().isoformat()
    since = (date.today() - timedelta(days=args.days)).isoformat()

    boards = json.loads((DATA / "boards.json").read_text(encoding="utf-8"))["boards"]
    archive = json.loads(ARCHIVE.read_text(encoding="utf-8")) if ARCHIVE.exists() else {}
    first_run = not archive

    seen, failed, totals = set(), [], {}
    with cf.ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(fetch_board, b): b for b in boards}
        for f in cf.as_completed(futs):
            b = futs[f]
            try:
                jobs, n_all = f.result()
            except Exception as e:  # keep going; a dead board shouldn't stop the run
                failed.append(f"{b['company']} ({b['ats']}/{b['token']}): {e}")
                continue
            totals[b["company"]] = (len(jobs), n_all)
            for j in jobs:
                key = f"{b['ats']}:{b['token']}:{slug(j['title'])}"
                seen.add(key)
                prev = archive.get(key, {})
                archive[key] = {
                    "company": b["company"], "ats": b["ats"], "board": b["token"],
                    "title": j["title"], "url": j["url"], "location": j["location"],
                    "locations": j["locations"], "remote": j["remote"], "pay": j["pay"], "posted": j["posted"],
                    "section": section_for(j["title"]),
                    "first_seen": prev.get("first_seen", today), "last_seen": today,
                    "active": True, "closed_on": None,
                }
                j["company"], j["first_seen"] = b["company"], archive[key]["first_seen"]
                if (j["posted"] and j["posted"] >= since) or (not first_run and not prev):
                    archive[key]["_candidate"] = j

    failed_boards = {x.split(" (")[0] for x in failed}
    closed = 0
    for key, rec in archive.items():
        if rec.get("active") and key not in seen and rec["company"] not in failed_boards:
            rec["active"], rec["closed_on"] = False, today
            closed += 1

    cands = [rec.pop("_candidate") for rec in archive.values() if "_candidate" in rec]
    cands.sort(key=lambda j: (j["posted"] or "", j["company"]), reverse=True)

    DATA.mkdir(exist_ok=True)
    ARCHIVE.write_text(json.dumps(dict(sorted(archive.items())), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    CANDIDATES.mkdir(exist_ok=True)
    out = [f"<!-- Digest candidates {today}: {len(cands)} roles posted since {since} "
           f"(or new since the last run). Pick 12–20, write each note, paste into the digest. -->\n"]
    for name, _ in SECTIONS:
        group = [j for j in cands if section_for(j["title"]) == name]
        if group:
            out.append(f"                <h2>{html.escape(name)}</h2>\n                <ul>\n")
            out.extend(li(j) for j in group)
            out.append("                </ul>\n\n")
    cand_path = CANDIDATES / f"{today}.html"
    cand_path.write_text("".join(out), encoding="utf-8")

    active = sum(1 for r in archive.values() if r["active"])
    print(f"Boards: {len(totals)} ok, {len(failed)} failed")
    for co, (n, n_all) in sorted(totals.items(), key=lambda x: -x[1][0]):
        if n:
            print(f"  {co:22} {n:3} speech roles of {n_all}")
    for msg in failed:
        print(f"  FAILED {msg}")
    print(f"Archive: {len(archive)} roles ({active} open, {closed} closed this run) -> {ARCHIVE.relative_to(REPO)}")
    print(f"Candidates: {len(cands)} -> {cand_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
