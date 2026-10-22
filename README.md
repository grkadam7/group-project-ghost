# Group Project Ghost

The nag you never write. A local open-source AI agent that reads your group
project's task list and composes the follow-up messages you'd otherwise spend
mental energy on — plus a spoken two-line morning brief so you can know the
state of the team without sitting up.

> Hacktoberfest 2026 — Week 3: *Slow and Steady*

## How it works

```
tasks.yaml  ──►  Ollama (gemma3:4b, runs on your machine)  ──►  nudges you paste
                                                       └────►  brief.mp3 (ElevenLabs voice)
```

Everything the model sees stays on your machine. ElevenLabs is only ever given
the two-line brief text.

## Requirements

- [Ollama](https://ollama.com) with a small model: `ollama pull gemma3:4b`
- [uv](https://docs.astral.sh/uv/) (runs the script, no venv setup)
- `ELEVENLABS_API_KEY` — only for `--speak` (get one via `npx -y @elevenlabs/cli@latest onboard init`)

## Usage

```bash
uv run ghost.py                      # per-person nudges, ready to paste
uv run ghost.py --tone passive-aggressive   # the demo tone
uv run ghost.py --brief              # two-line morning brief, spoken style
uv run ghost.py --brief --speak      # same, saved as brief.mp3
uv run ghost.py --selftest           # offline sanity check
```

Your project lives in `tasks.yaml`:

```yaml
project: DBMS Mini Project — Library Management
tasks:
  - task: Write the 6-page report
    owner: priya
    due: 2026-10-21
    status: todo      # done / wip / todo
```

## What it deliberately doesn't do

No WhatsApp, Discord, or email sending — the ghost prepares, you paste.
No accounts, no database, no web app. Composing is the tedious part;
pasting isn't.
