# Group Project Ghost

> Week 3 — Hacktoberfest Open-Source AI Challenge: "Slow and Steady" (due Oct 25, 11:59 PM PDT)

## Problem Statement

How might we stop the one student who always becomes the group project's de-facto nag — using open-source AI at the core — so that keeping a team on track costs them nothing but a paste?

## Recommended Direction

A local CLI agent that reads a shared `tasks.yaml` for a group project and, with one command, produces the follow-up messages you'd otherwise spend mental energy composing: one nudge per overdue teammate in a configurable tone, plus a spoken two-line morning brief (ElevenLabs) you can listen to without sitting up.

The laziness claim: composing the nag is the tedious part, pasting isn't. The ghost does all composing; you never write a status message again. Open-weight model (Ollama) does the writing — that's the hard requirement of the challenge. ElevenLabs is the delivery mechanism that makes it voice-first, which is the differentiator no Week 3 entry has used, and the hook for the Best Use of ElevenLabs category.

The story is personal: "I was too lazy to be my group's project manager."

## Key Assumptions to Validate

- [ ] A local small model (gemma/qwen via Ollama) writes usable, on-tone nudges from `tasks.yaml` — test on the real project data on day 1.
- [ ] The demo reads honest, not fake — base it on a real course project; admit the teammates are renamed in the post.
- [ ] Tone control works: demo one deliberately over-the-top passive-aggressive mode (the humor beat).
- [ ] Pre-generated `mp3`s ship in the repo; at most one live ElevenLabs call during the demo.
- [ ] Lazy payoff is measurable: minutes of nag-composing avoided per day, tracked over the project's own use.

## MVP Scope

In:
- `tasks.yaml` (task, owner, due date, status) — part of the demo, not setup chore
- `python ghost.py` → per-person nudge drafts + tone flag
- `python ghost.py --brief` → spoken 2-line morning brief (ElevenLabs TTS)
- local Ollama model as the writing core
- one README + one DEV post with `#hf26challenge`

## Not Doing (and Why)

- Real message sending (WhatsApp/Discord/email) — integration eats the 3-day budget; one paste is the send.
- Multiple projects, auth, database, web UI — no one asked, judges won't see it.
- Calendar/schedule automation — scope creep past Oct 25.
- Chasing teammates across platforms — the ghost prepares, it doesn't hunt.

## Open Questions

- Which Ollama model is the lightest that still holds tone? (decide day 1, benchmark against 3 sample nudges)
- Do we demo `--brief` live or with a shipped mp3? (lean shipped, one live call max)
