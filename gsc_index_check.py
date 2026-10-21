#!/usr/bin/env python3
"""
=============================================================================
 SPEECHTECHJOBS -- GOOGLE INDEX CHECKER (Search Console URL Inspection API)
=============================================================================
 Why this matters here:
   Google traffic is a RANKING problem -- but you can't rank a page Google
   hasn't indexed. This asks Google, URL by URL, what it actually did with
   each page in the sitemap: indexed, crawled-but-rejected, discovered-but-
   never-crawled, or unknown. That answer decides whether the next fix is
   content (rankings) or crawlability (indexing).

   IndexNow (indexnow.py) covers Bing. Google does not support IndexNow, so
   this is the Google-side check that every page actually made it in.

 ONE-TIME SETUP
 --------------
   1. Google Cloud Console -> create/select a project -> enable the
      "Google Search Console API".
   2. OAuth consent screen -> External, Testing mode -> add your Google
      account as a test user.
   3. Credentials -> Create OAuth client ID -> type "Desktop app" ->
      download the JSON -> save it next to this script as gsc_client.json
   4. First run opens a browser to approve READ-ONLY Search Console access.
      The refresh token is saved to gsc_token.json. Both files are
      gitignored -- this repo is public, never commit them.

 USAGE
 -----
   # Inspect every URL in the live sitemap:
   python gsc_index_check.py --sitemap

   # Inspect specific URLs (e.g. a few days after publishing a digest):
   python gsc_index_check.py https://speechtechjobs.com/blog/new-post

 NOTES
 -----
   * Read-only scope (webmasters.readonly). It cannot change anything.
   * Quota: 2,000 inspections/day, 600/min per property. The sitemap is
     ~50 URLs, so a full run is nowhere near it.
   * Every run writes a CSV snapshot to gsc_reports/ (gitignored). Keep
     these -- a dated history of index coverage is due-diligence material.
=============================================================================
"""

import sys
import os
import csv
import json
import time
import base64
import hashlib
import secrets
import datetime
import webbrowser
import urllib.parse
import urllib.request
import urllib.error
from collections import Counter
from http.server import HTTPServer, BaseHTTPRequestHandler

from indexnow import HOST, get_sitemap_urls, clean

# ---------------------------------------------------------------- CONFIG ---
HERE        = os.path.dirname(os.path.abspath(__file__))
CLIENT_FILE = os.path.join(HERE, "gsc_client.json")
TOKEN_FILE  = os.path.join(HERE, "gsc_token.json")
REPORT_DIR  = os.path.join(HERE, "gsc_reports")

SCOPE       = "https://www.googleapis.com/auth/webmasters.readonly"
AUTH_URL    = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL   = "https://oauth2.googleapis.com/token"
SITES_URL   = "https://www.googleapis.com/webmasters/v3/sites"
INSPECT_URL = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"


# ----------------------------------------------------------------- OAUTH ---
def load_client():
    if not os.path.exists(CLIENT_FILE):
        print(f"\n  Missing {os.path.basename(CLIENT_FILE)}.")
        print("  See ONE-TIME SETUP at the top of this script.\n")
        sys.exit(1)
    with open(CLIENT_FILE) as f:
        data = json.load(f)
    c = data.get("installed") or data.get("web")
    if not c:
        print("\n  gsc_client.json isn't an OAuth client file "
              "(expected a Desktop app client).\n")
        sys.exit(1)
    return c["client_id"], c["client_secret"]


def post_form(url, fields):
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def authorize(client_id, client_secret):
    """Loopback + PKCE installed-app flow. Returns a refresh token."""
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    result = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [None])[0] == state:
                result["code"] = q.get("code", [None])[0]
                result["error"] = q.get("error", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Done. You can close this tab.")

        def log_message(self, *a):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    redirect = f"http://127.0.0.1:{server.server_port}/"
    url = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    })
    print("\n  Opening browser for Google sign-in (read-only Search Console).")
    print("  If it doesn't open, paste this URL:\n\n  " + url + "\n")
    webbrowser.open(url)
    try:
        while "code" not in result and "error" not in result:
            server.handle_request()
    except KeyboardInterrupt:
        print("\n  Cancelled. (Blocked by Google? Add your account as a test "
              "user on the OAuth consent screen, then re-run.)\n")
        sys.exit(1)
    finally:
        server.server_close()

    if not result.get("code"):
        print(f"\n  Authorization failed: {result.get('error')}\n")
        sys.exit(1)

    tok = post_form(TOKEN_URL, {
        "code": result["code"],
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect,
        "grant_type": "authorization_code",
        "code_verifier": verifier,
    })
    with open(TOKEN_FILE, "w") as f:
        json.dump({"refresh_token": tok["refresh_token"]}, f)
    print(f"  Saved refresh token to {os.path.basename(TOKEN_FILE)}")
    return tok["access_token"]


def get_access_token():
    client_id, client_secret = load_client()
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            refresh = json.load(f).get("refresh_token")
        try:
            return post_form(TOKEN_URL, {
                "refresh_token": refresh,
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "refresh_token",
            })["access_token"]
        except urllib.error.HTTPError:
            # Testing-mode refresh tokens expire after 7 days -- re-auth.
            print("\n  Saved token expired or was revoked -- re-authorizing.")
    return authorize(client_id, client_secret)


# ------------------------------------------------------------------- API ---
def api(url, token, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method="POST" if data else "GET",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def find_property(token):
    """Prefer the domain property; fall back to the URL-prefix one."""
    sites = api(SITES_URL, token).get("siteEntry", [])
    owned = {s["siteUrl"] for s in sites
             if s.get("permissionLevel") != "siteUnverifiedUser"}
    for candidate in (f"sc-domain:{HOST}", f"https://{HOST}/",
                      f"https://www.{HOST}/"):
        if candidate in owned:
            return candidate
    print(f"\n  No verified Search Console property for {HOST} on this "
          "Google account.")
    print("  Properties this account can see:")
    for s in sorted(owned) or ["(none)"]:
        print("     " + s)
    print()
    sys.exit(1)


def inspect(url, site, token):
    res = api(INSPECT_URL, token, {"inspectionUrl": url, "siteUrl": site})
    r = res.get("inspectionResult", {}).get("indexStatusResult", {})
    canon = r.get("googleCanonical", "")
    return {
        "url": url,
        "verdict": r.get("verdict", ""),
        "coverage": r.get("coverageState", ""),
        "last_crawl": r.get("lastCrawlTime", "")[:10],
        "fetch": r.get("pageFetchState", ""),
        "robots": r.get("robotsTxtState", ""),
        "google_canonical": canon,
        "canonical_mismatch": bool(canon) and canon.rstrip("/") != url.rstrip("/"),
        "in_sitemap": bool(r.get("sitemap")),
    }


# ---------------------------------------------------------------- REPORT ---
def report(rows):
    print("\n" + "=" * 74)
    print("RESULTS")
    print("=" * 74)
    prefix = f"https://{HOST}"
    for r in sorted(rows, key=lambda r: (r["verdict"] == "PASS", r["url"])):
        flag = "OK " if r["verdict"] == "PASS" else "!! "
        path = r["url"][len(prefix):] or "/"
        print(f"  {flag}{path:<48} {r['coverage'][:34]:<34} {r['last_crawl']}")
        if r["canonical_mismatch"]:
            print(f"       Google chose a different canonical: {r['google_canonical']}")

    print("\n" + "=" * 74)
    print("SUMMARY")
    print("=" * 74)
    for state, n in Counter(r["coverage"] for r in rows).most_common():
        print(f"  {n:>3}  {state}")
    mism = sum(r["canonical_mismatch"] for r in rows)
    if mism:
        print(f"\n  {mism} URL(s) where Google picked a different canonical.")

    os.makedirs(REPORT_DIR, exist_ok=True)
    out = os.path.join(REPORT_DIR,
                       f"index-{datetime.date.today().isoformat()}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\n  Snapshot saved: {os.path.relpath(out, HERE)}")


def main():
    args = sys.argv[1:]
    if "--sitemap" in args:
        urls = get_sitemap_urls()
        print(f"\n  Found {len(urls)} URLs in sitemap")
    elif args:
        urls = args
    else:
        print(__doc__)
        sys.exit(0)

    good, bad = clean(urls)
    if bad:
        print(f"\n  Skipped {len(bad)} URL(s) not on https://{HOST}/:")
        for u in bad[:10]:
            print("     " + u)
    if not good:
        print("\n  Nothing valid to inspect.")
        sys.exit(1)

    token = get_access_token()
    try:
        site = find_property(token)
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e)["error"]["message"]
        except Exception:
            msg = e.reason
        print(f"\n  HTTP {e.code}: {msg}\n")
        sys.exit(1)
    print(f"  Property : {site}")
    print(f"  Checking : {len(good)} URL(s)\n")

    rows = []
    for i, u in enumerate(good, 1):
        try:
            rows.append(inspect(u, site, token))
            print(f"  [{i}/{len(good)}] {rows[-1]['coverage'] or '?'}  {u}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            print(f"  [{i}/{len(good)}] HTTP {e.code}  {u}\n       {body}")
            if e.code == 429:
                print("\n  Quota hit -- stopping. Try again later.")
                break
        time.sleep(0.2)  # stay well under 600/min

    if rows:
        report(rows)
    print()


if __name__ == "__main__":
    main()
