# SpeechTechJobs — Content Plan

_Last updated: 2026-08-31_

## Why this plan exists

The job-board model didn't produce signups. The traffic that *does* arrive is
split between people researching **speech-tech careers** (salaries, interviews,
how to break in), people researching **tooling** (Kaldi, Whisper, conferences),
and hiring managers looking for **Whisper/speech contractors**. The site has been
reframed as a careers hub with a weekly newsletter. Content is now the growth
lever and the path to revenue.

Everything here is grounded in Google Search Console and Bing Webmaster data as of
August 2026. We build on clusters that **already rank**, not guesses.

### The flywheel

```
SEO guides  ──►  organic traffic  ──►  newsletter signups
     ▲                                        │
     │                                        ▼
guide backlog  ◄── topic ideas ◄──  weekly "who's hiring" digest
                                     (retains list, adds fresh-content
                                      signal, grows subscribers)
                                              │
                                              ▼
                              list size unlocks sponsorships +
                              gives paid employer posts distribution
```

---

## The engine: two streams

| Stream | Cadence | Purpose | Effort |
|---|---|---|---|
| **"Who's hiring in speech AI"** digest | Weekly (suggest Tue) | Fresh-content signal, the newsletter itself, list growth | ~90 min/wk |
| **SEO guide** expanding a ranking cluster | Weekly (suggest Thu) | Compounding organic traffic into the funnel | ~3–4 hrs each |

Confirmed realistic: **one digest + one guide per week.**

Every publish ends with the same three steps:

1. Add the URL to `sitemap.xml` (extensionless form, e.g. `/blog/my-post`).
2. `python indexnow.py https://speechtechjobs.com/blog/my-post`
3. Digest only: send the Brevo campaign to the newsletter list.

---

## Stream 1 — Weekly "Who's hiring in speech AI" digest

Answers queries the site already receives: _"current open asr tts jobs"_,
_"speech ai voice research jobs"_, _"speech ai jobs"_, _"remote speech
recognition jobs"_.

### Tracked companies (the source list)

Skim these career pages each week. Add/remove as the market shifts.

**ASR / transcription:** Deepgram, AssemblyAI, Speechmatics, Rev, Verbit,
Otter.ai, Fireflies.ai, Descript, Speechify, Wispr Flow
**TTS / voice:** ElevenLabs, Cartesia, Rime, PlayHT, WellSaid
**Voice agents:** PolyAI, Vapi, Retell AI, Cresta, Parloa
**Speech analytics / contact center:** Gong, Observe.ai, Uniphore, CallMiner, Cognigy
**Embedded / edge:** Picovoice, Sensory, Cerence, SoundHound
**Healthcare speech:** Suki.ai, Abridge, DeepScribe, Nuance (Microsoft)
**Audio infra / accents:** Krisp, Sanas, Gladia
**Big labs:** Google (Speech/Assistant), Amazon (Alexa AGI), Apple (Siri), Meta FAIR, NVIDIA (NeMo), Microsoft
**Research-adjacent:** Kensho, ASAPP

**Also grep weekly** for `Whisper`, `ASR`, `speech recognition`, `TTS`,
`diarization`, `speech scientist`:
- `job-boards.greenhouse.io`
- `jobs.ashbyhq.com`
- `jobs.lever.co`

### Weekly workflow (~90 min)

1. Open the tracked list, collect roles posted/updated in the last ~10 days (12–20 is the target).
2. For each: role title, company, location (or Remote + region), salary **if the posting states it**, one-line note, link to the **company's own posting**.
3. Group into: ASR · TTS · Speech analytics · Voice agents · Research.
4. Write a 2–3 sentence intro — this doubles as the email subject line hook.
5. Publish the post, send the Brevo campaign, run IndexNow.

### Post + email format

```
Title:   Who's hiring in speech AI — <Month D, YYYY>
Slug:    /blog/who-is-hiring-speech-ai-YYYY-MM-DD
H1:      Who's hiring in speech AI this week

<2–3 sentence intro / hook>

## ASR & transcription
**<Role> — <Company>** · <location> · <salary if listed>
<one-line note>. [View posting](company-url)
...

## Text-to-speech & voice
...

## Speech analytics
...

## Voice agents
...

## Research
...

---
Hiring for a speech-tech role? [Post it here](/hire-talent).
Browse open roles by specialty: [speechtechjobs.com](/#specialties)
```

Brevo: new campaign from the digest template, paste the body, subject = the intro
hook, send to the newsletter list. Each issue keeps a permanent blog URL as the
archive.

---

## Stream 2 — SEO guide calendar

**Rule: expand what already ranks.** Five clusters, ranked by opportunity in our
own data.

### Cluster A — Kaldi (highest opportunity, do first)

`what-is-kaldi-complete-guide-2026` ranks ~#6.7 on 278 Bing impressions. There are
**150+ long-tail Kaldi queries** with almost no competition (`kaldi vs whisper
self hosted`, `kaldi enterprise on-premise`, `next gen kaldi`, `what is kaldi
decoder`, `kaldi recognizer sample rate`, plus dozens of misspellings). "kaldi"
alone = 133 impressions.

| Post | Target query | Primary internal link |
|---|---|---|
| Is Kaldi still used in 2026? | `kaldi 2026`, `is kaldi still used`, `kaldi vs whisper` | `/open-source-asr-jobs` |
| Kaldi vs Whisper for self-hosted / enterprise ASR | `kaldi vs whisper self hosted enterprise`, `kaldi enterprise on-premise` | `/kaldi-production-engineer-jobs` |
| Next-gen Kaldi: k2, icefall, sherpa explained | `next gen kaldi`, `k2 kaldi` | `/open-source-asr-jobs` |
| Whisper vs wav2vec2 vs MMS: which model to build on | `whisper vs wav2vec2 vs mms comparison` | `/whisper-jobs` |
| Kaldi troubleshooting: `<unk>`, sample rate, decoder basics | `kaldi recognizer sample rate`, `what is kaldi decoder`, `<unk> kaldi output` | existing Kaldi guide |

### Cluster B — Conferences & deadlines (best-performing page today)

`speech-tech-conferences-2026` = **575 impressions / 22 clicks / pos 6.5** — the
single best entry point on the site. `asru 2026` already ranks **pos 3 at 25%
CTR**. Treat these as living pages; prioritize whichever conference has the
nearest deadline or event (as of now: ASRU 2026 and SLT 2026 in December, then
ICASSP 2027 and Interspeech 2027 calls opening).

| Post | Target query | Primary internal link |
|---|---|---|
| ASRU 2026: dates, deadlines, what to expect | `asru 2026`, `ieee asru 2026`, `asru 2026 call for paper` | `/asr-research-jobs` |
| Speech-AI conference deadline tracker 2026–2027 (living table) | `speech conferences 2026`, `upcoming speech/audio conference deadlines` | conferences post |
| Interspeech 2027: dates, deadlines, venue, cost (living page) | `interspeech 2027`, `interspeech deadline`, `interspeech dates` | `/asr-research-jobs` |
| ICASSP 2027: dates, acceptance rate, deadlines | `icassp deadline`, `icassp acceptance rate`, `is icassp tier 1` | `/asr-research-jobs` |

**Now:** add an email-capture block to the existing `speech-tech-conferences-2026`
post — it's the top entry point and currently has none.

### Cluster C — Interview prep (converts, and we rank)

`speech-recognition-interview-questions-2026` gets clicks.
`speech-analytics-interview-questions-2026` also ranks. Extend the set.

| Post | Target query | Primary internal link |
|---|---|---|
| TTS / voice synthesis interview questions | `tts interview questions`, `asr tts ml engineer interview questions` | `/spoken-nlp-jobs` |
| Voice biometrics interview questions | ties to `/voice-biometrics-jobs` (7.35% CTR page) | `/voice-biometrics-jobs` |
| Speaker diarization interview questions | `diarization interview questions` | `/asr-research-jobs` |
| Speech-AI system design interview walkthrough | `asr code question`, `asr interview questions` | `/blog/how-to-break-into-speech-tech-2026` |

### Cluster D — Salary guides

`whisper-ai-jobs-salary-guide-2026` ranks ~pos 4.
`speech-recognition-engineer-salary-2026` exists.

| Post | Target query | Primary internal link |
|---|---|---|
| Voice AI engineer salary & skills 2026 | `voice ai engineer job requirements 2026`, `speech ai engineer career path` | `/spoken-nlp-jobs` |
| ASR research scientist salary 2026 | `speech scientist`, `speech scientist jobs` | `/asr-research-jobs` |
| TTS / voice engineer salary 2026 | `text to speech jobs` | `/spoken-nlp-jobs` |
| Speech data / annotation roles: pay and how to get in | `speech data jobs`, `speech data collection jobs` | `/jobs` |

### Cluster E — "Hire Whisper" buyer funnel

`hire whisper developers` / `whisper api developers for hire` / `hire whisper
integration experts` each pull ~90–100 impressions/quarter at **0% CTR**. Capture
that intent and route it to `/hire-whisper-engineers`.

| Post | Target query | Primary internal link |
|---|---|---|
| How to hire a Whisper engineer (in-house vs contract vs agency) | `how to hire whisper developers`, `where to hire whisper developers` | `/hire-whisper-engineers` |
| Whisper contractor rates in 2026 | `whisper developers for hire`, `freelance whisper developers` | `/hire-whisper-engineers` |
| Self-hosted Whisper vs commercial ASR API: real cost breakdown | `commercial providers whisper wav2vec2 mms` | `/hire-whisper-engineers` |
| What a Whisper engineer actually does (for hiring managers) | `hire whisper integration experts` | `/hire-whisper-engineers` |

---

## The first 12 weeks

| Week of | Digest | Guide | Housekeeping |
|---|---|---|---|
| **Sep 1** | Issue #1 | Is Kaldi still used in 2026? | Finalize tracked-company list; add email capture to conferences post |
| **Sep 8** | Issue #2 | ASRU 2026: dates, deadlines, what to expect | Build the Brevo digest template |
| **Sep 15** | Issue #3 | How to hire a Whisper engineer in 2026 | — |
| **Sep 22** | Issue #4 | Kaldi vs Whisper for self-hosted / enterprise ASR | Internal-link audit pass 1 |
| **Sep 29** | Issue #5 | TTS / voice synthesis interview questions | **Month 1 review** (GSC + Bing + Brevo) |
| **Oct 6** | Issue #6 | Speech-AI conference deadline tracker 2026–2027 | Refresh existing `speech-tech-conferences-2026` post |
| **Oct 13** | Issue #7 | Voice AI engineer salary & skills 2026 | — |
| **Oct 20** | Issue #8 | Next-gen Kaldi: k2, icefall, sherpa explained | Check which new URLs are indexed |
| **Oct 27** | Issue #9 | Self-hosted Whisper vs commercial ASR API cost breakdown | **Month 2 review** |
| **Nov 3** | Issue #10 | Whisper vs wav2vec2 vs MMS: which model to build on | — |
| **Nov 10** | Issue #11 | Voice biometrics interview questions | Internal-link audit pass 2 |
| **Nov 17** | Issue #12 | ASR research scientist salary 2026 | **Quarter review**; assess sponsor readiness |

---

## Publishing workflow

### Files & slugs

- Guides: `blog/<slug>.html`, canonical URL `/blog/<slug>` (no `.html`).
- Digests: `blog/who-is-hiring-speech-ai-YYYY-MM-DD.html`.
- Use the same `<head>` structure as existing blog posts, and **include the
  canonical tag**: `<link rel="canonical" href="https://speechtechjobs.com/blog/<slug>">`.
- Match the existing blog CSS / layout so pages look consistent.

### On-page SEO checklist (per guide)

- [ ] Title tag: primary query near the front, < 60 chars, ends `| SpeechTechJobs`
- [ ] Meta description: ~150 chars, contains the query + a reason to click
- [ ] One `<h1>` = the topic. `<h2>`s = the sub-questions people actually search.
- [ ] Answer the core query in the first ~100 words.
- [ ] 800–1,800 words. Living pages (trackers) can be shorter but dated.
- [ ] FAQ block when the query is a question (helps featured snippets).
- [ ] Visible publish date; "Last updated" line on living pages.
- [ ] Canonical tag present.
- [ ] Added to `sitemap.xml` (extensionless URL).
- [ ] `python indexnow.py <url>` run after deploy.

### Internal linking rules

- Every guide links to **at least three** things: (1) its primary category/jobs
  page, (2) the newsletter signup (`/#newsletter` or an on-page block),
  (3) one sibling guide in the same cluster.
- Every category/jobs page links back to its cluster's best guide.
- The weekly digest links to `/hire-talent` and `/#specialties`.

### Brevo (digest send)

- New campaign from the digest template → paste post body → subject = the intro
  hook → send to the newsletter list.
- Newsletter list only. Do **not** send digests to employer-inquiry contacts.

---

## Measurement

### Monthly review (GSC + Bing Webmaster + Brevo)

- New guide URLs: impressions, clicks, average position for the target query.
- Newsletter: subscriber count, issue open rate. **This is the number that
  unlocks sponsorships.**
- `/hire-whisper-engineers` and `/hire-talent`: form submissions.
- Total indexed pages (baseline: 15 indexed / 18 not indexed, Aug 2026) — trend up.
- Bing conference + Kaldi clusters: combined impressions.

### Targets

| By end of | Subscribers | Organic | Funnel |
|---|---|---|---|
| Month 1 | 25–50 | 8 new URLs indexed; issues #1–4 out | — |
| Month 3 | 150–300 | 3+ guides in top 20 for target query; conferences+Kaldi clusters > 1,500 impressions/mo (Bing) | 1–3 form submits total |
| Month 6 | 500–1,000 | 2–3 guides in top 10 | Steady form submits; soft-pitch first sponsor |

---

## Backlog beyond week 12

Work down the cluster tables above, keeping the weekly interleave (rotate A→B→C→D→E).
Priority order within the remaining backlog:

1. Remaining **Kaldi** posts (troubleshooting, model comparison) — lowest
   competition, proven Bing demand.
2. **Conference** living pages for whichever event's deadline is next.
3. **Hire-Whisper** funnel posts 2–4 — highest commercial intent.
4. **Interview** and **salary** posts to fill the weeks between.

New cluster candidates once the above is thin:
- "Speechmatics / Speechify / Picovoice / PolyAI careers" pages (brand queries
  already in GSC: `speechmatics jobs`, `speechify careers`, `picovoice careers`).
- Embedded / on-device voice (`embedded voice developer`, `embedded speech
  technology` — feeds `/embedded-voice-ai-jobs`).
- "How to get a job in voice technology" expansion (multiple variants in Bing data,
  including one for career-changers/seniors).

---

## Monetization triggers

Act when the metric is hit, not before:

| Trigger | Action |
|---|---|
| ~500 subscribers, steady open rate | Soft-pitch one sponsor slot to a tracked company's devrel/recruiting team (~free or trial) |
| ~1,000 subscribers | Sell one paid sponsor slot per issue, start ~$150–250 |
| First unprompted employer form submits | Formalize the placement-fee terms on `/hire-talent` |
| 3+ guides in top 10 and traffic trending up for 3 straight months | Add cheap paid job postings ($99) sold to tracked companies as proof-of-life for a future sale |
