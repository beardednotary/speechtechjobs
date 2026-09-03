# The Speech AI Career Starter Kit

_A SpeechTechJobs guide. Everything here is condensed from our free articles at
speechtechjobs.com/blog — follow the links for the full versions._

_Drop this text into a doc, add a cover and light design, export to PDF, and put
it at `/speech-ai-starter-kit.pdf`. Rebuild once a quarter from the latest
versions of the source pages._

---

## 1. The speech-AI job map

Speech AI splits into a handful of specialties. Rough US total-comp ranges for
mid-to-senior roles (see the salary guides for sourced detail and how to research
a specific offer):

| Specialty | What you work on | Rough range |
|---|---|---|
| ASR research | Novel models, SSL, publications | $200K–$350K+ |
| ASR / speech ML engineering | Fine-tuning, eval, production ASR | $150K–$260K |
| Whisper specialist work | Domain adaptation, inference optimization | $140K–$220K |
| TTS / voice synthesis | Vocoders, codec-LMs, prosody | $150K–$260K |
| Speech analytics | Diarization + sentiment + summarization | $150K–$240K |
| Voice biometrics | Speaker verification, anti-spoofing | $165K–$230K |
| Voice agents | ASR+TTS+LLM pipelines, real-time | $150K–$250K |
| Embedded / on-device | Quantization, edge inference, DSP | $145K–$215K |

Ranges vary widely by company stage, location, and level. Big labs and revenue-
intelligence companies sit at the top; earlier-stage startups trade cash for
equity.

---

## 2. How to break in

- **Pick a track.** Research (novel models, publications), applied ML
  (fine-tuning, evaluation, data), or systems/inference (latency, cost, serving).
  The interview loops differ.
- **Ship something with real audio.** A fine-tuned Whisper on a domain dataset, a
  streaming transcription demo, or a diarization + ASR pipeline with measured WER
  and DER beats a generic ML portfolio.
- **Learn the metrics.** WER, CER, RTF (real-time factor), DER — and how to read
  an evaluation that isn't leaking training data.
- **Contribute where the field lives.** Whisper, faster-whisper, NeMo, icefall,
  SpeechBrain, pyannote — a merged PR gets noticed.
- **Do you need a PhD?** For pure research roles at top labs, usually yes or an
  equivalent publication record. For applied and systems roles, no — a strong
  portfolio and one deep audio project is enough.

_Full guide: speechtechjobs.com/blog/how-to-break-into-speech-tech-2026_

---

## 3. The 10 ASR interview questions that come up most

1. **Explain WER. What are its limitations?** (Insertions/deletions/substitutions
   over reference length; doesn't weight semantic importance; sensitive to
   normalization.)
2. **CTC vs. attention vs. RNN-T — trade-offs?** (Alignment assumptions,
   streaming capability, training stability.)
3. **How does Whisper work, and where does it fail?** (Encoder-decoder,
   chunked; hallucinates on silence, long-form drift, weak word-level timestamps.)
4. **What is a WFST and why did classic ASR use it?** (Composing HMM/lexicon/LM
   into one searchable graph; efficient decoding, lattices.)
5. **How would you cut inference cost in half?** (faster-whisper/CTranslate2,
   smaller/distilled model, batching, VAD, quantization.)
6. **How do you build a fair evaluation set?** (Held-out speakers and conditions,
   no leakage, representative of production audio.)
7. **Streaming ASR — what changes?** (Latency budget, partial hypotheses,
   endpointing, lookahead vs. accuracy.)
8. **Speaker diarization pipeline — walk through it.** (VAD → embeddings
   (x-vector/ECAPA) → clustering → resegmentation; DER; overlap handling.)
9. **Fine-tuning: how do you know it helped?** (WER/CER delta on a held-out
   domain set, not training loss; significance.)
10. **When would you NOT use Whisper?** (Real-time/streaming, strict word-level
    timestamps, or when a commercial API is simply cheaper.)

_Full set with answers: speechtechjobs.com/blog/speech-recognition-interview-questions-2026_

---

## 4. The tools that matter

- **Whisper (OpenAI)** — the default for "paste audio, get a good transcript."
  Strong multilingual accuracy out of the box; weak at streaming and precise
  timestamps. Optimize with faster-whisper / CTranslate2.
- **Classic Kaldi** — the 2011 C++/WFST toolkit. Near-maintenance now, but still
  running in telephony, government, and enterprise systems. Knowing WFSTs,
  lattices and lexicons is a rare, transferable skill.
- **Next-gen Kaldi (k2 / lhotse / icefall / sherpa)** — PyTorch-native, actively
  developed, and a leading choice for streaming and on-device ASR.
- **NVIDIA NeMo / Riva** — production toolkit and serving stack; Parakeet and
  Canary model families.
- **wav2vec 2.0 / HuBERT / MMS (Meta)** — self-supervised speech representations;
  the research lineage behind a lot of modern ASR.
- **Vosk** — wraps Kaldi behind a simple offline API in ~20 languages; very
  widely used.

_Full comparisons: speechtechjobs.com/blog/is-kaldi-still-used-2026 and
/blog/kaldi-vs-whisper-vs-wav2vec-2026_

---

## 5. Where the jobs are

**Dedicated ASR / speech-to-text platforms:** Deepgram, AssemblyAI, Speechmatics,
Rev, Gladia, Otter.ai

**Big labs & platforms:** OpenAI, Google / DeepMind, Amazon (Alexa, Transcribe),
Apple, Microsoft (Azure Speech, Nuance), Meta AI (FAIR), NVIDIA

**Voice agents / conversational AI:** Cartesia, Rime, PolyAI, Vapi, Retell AI,
Cresta, Observe.AI, Gong

**Vertical ASR:** Suki, Abridge, DeepScribe, Nuance (healthcare); Verbit, Rev
(legal); Cerence, SoundHound (automotive)

_Full guide with careers links: speechtechjobs.com/blog/top-companies-hiring-asr-engineers-2026_

---

## 6. The 2026 speech-conference calendar

| Conference | Dates | Location |
|---|---|---|
| ICASSP 2026 | May 4–8, 2026 | Barcelona, Spain (concluded) |
| Interspeech 2026 | Sept 28 – Oct 1, 2026 | Sydney, Australia |
| SLT 2026 | Dec 13–16, 2026 | Palermo, Italy |

Note: there is **no ASRU 2026** — ASRU runs in odd years (next: 2027). SLT is its
even-year counterpart. ICASSP and Interspeech are the main recruiting venues; a
paper gets you approached directly, but the hallway track works without one.

_Details: speechtechjobs.com/blog/asru-2026 and /blog/speech-tech-conferences-2026_

---

## Keep going

- **Weekly digest** — new speech-AI roles from ~30 companies, every week:
  speechtechjobs.com
- **Browse by specialty** — speechtechjobs.com/#specialties
- **All guides** — speechtechjobs.com/blog
