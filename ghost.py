# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "elevenlabs"]
# ///
"""Group Project Ghost — the nag you never write.

Reads tasks.yaml, asks a local Ollama model to compose the follow-ups you'd
otherwise write yourself, and prints them ready to paste.
shortcut: delivery is copy-paste (no WhatsApp/Discord/email sending), upgrade
          only if a paste ever becomes the tedious part.
"""

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

import yaml

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "gemma3:4b"

TONES = {
    "polite": "warm, friendly, teammate-to-teammate",
    "sloth": "impossibly lazy and low-effort, but still gets the point across",
    "passive-aggressive": ("relentlessly pleasant on the surface with a clear "
                           "edge underneath — the tone of someone who has "
                           "asked three times already"),
}


def load_tasks(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "tasks" not in data:
        raise ValueError(f"{path} has no 'tasks' key — is it a ghost file?")
    return data


def overdue_tasks(data: dict, today: dt.date) -> list[dict]:
    out = []
    for t in data["tasks"]:
        if str(t.get("status", "")).lower() in ("done", "wip"):
            continue
        due = t.get("due")
        if isinstance(due, str):
            due = dt.date.fromisoformat(due)
        if due and due < today:
            out.append({**t, "due": due})
    return sorted(out, key=lambda t: t["due"])


def nudges_for(data: dict, today: dt.date, tone: str, model: str) -> dict[str, str]:
    """One ready-to-paste message per slacker, keyed by member name."""
    late = overdue_tasks(data, today)
    by_owner: dict[str, list[dict]] = {}
    for t in late:
        by_owner.setdefault(str(t["owner"]), []).append(t)

    drafts = {}
    for owner, tasks in by_owner.items():
        lines = "\n".join(
            f"- {t['task']} (was due {t['due']:%b %d})" for t in tasks
        )
        prompt = (
            f"You are a member of a student group project. Write ONE short "
            f"message ({owner} is the recipient) chasing them for overdue "
            f"work, without sounding like a manager.\n"
            f"Project: {data.get('project', 'our project')}\n"
            f"Overdue:\n{lines}\n"
            f"Tone: {TONES[tone]}.\n"
            f"Two or three sentences, no emoji, no subject line, ready to paste."
        )
        drafts[owner] = ask_model(prompt, model)
    return drafts


def brief_for(data: dict, today: dt.date, model: str) -> str:
    late = overdue_tasks(data, today)
    if not late:
        return "Nothing overdue. The team is ahead. Stay lazy."
    lines = "\n".join(f"- {t['task']} — {t['owner']} (due {t['due']:%b %d})"
                      for t in late)
    prompt = (
        f"You are a lazily efficient project assistant. Give a two-line "
        f"morning brief about this group project, straight to the point:\n"
        f"{lines}"
    )
    return ask_model(prompt, model)


def ask_model(prompt: str, model: str) -> str:
    body = json.dumps({
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": "You write brief, human messages."},
            {"role": "user", "content": prompt},
        ],
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.load(resp)["message"]["content"].strip()
    except OSError as e:
        sys.exit(f"Ollama is unreachable ({e}). Start it with `ollama serve`.")


def speak(text: str, out: Path) -> None:
    """Render text to mp3 with ElevenLabs (key lives in .env.local)."""
    env_file = Path(__file__).with_name(".env.local")
    if env_file.exists() and "ELEVENLABS_API_KEY" not in os.environ:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, sep, val = line.partition("=")
            if sep and not key.strip().startswith("#"):
                os.environ.setdefault(key.strip(), val.strip())

    from elevenlabs import ElevenLabs  # import lazily: only --speak needs it

    client = ElevenLabs()
    audio = client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",  # George — narrator
        model_id="eleven_v4",
    )
    out.write_bytes(b"".join(audio))


def selftest() -> None:
    data = load_tasks(Path(__file__).with_name("tasks.yaml"))
    today = dt.date(2026, 10, 22)
    late = overdue_tasks(data, today)
    assert len(late) == 2, f"expected 2 overdue, got {len(late)}"
    assert {t["owner"] for t in late} == {"arun", "priya"}
    assert late[0]["owner"] == "arun", "oldest overdue first"
    done = [t for t in data["tasks"] if t["status"] == "done"]
    assert len(done) == 3
    print("selftest ok: 2 overdue (arun, priya), 3 done, oldest first")


def main() -> None:
    p = argparse.ArgumentParser(description="the nag you never write")
    p.add_argument("--tasks", type=Path, default=Path("tasks.yaml"))
    p.add_argument("--tone", choices=TONES, default="polite")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--brief", action="store_true",
                   help="two-line spoken-style morning brief")
    p.add_argument("--speak", action="store_true",
                   help="render the brief to brief.mp3 (ElevenLabs voice)")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows console mangles — and ’

    if args.selftest:
        selftest()
        return

    data = load_tasks(args.tasks)
    today = dt.date.today()
    late = overdue_tasks(data, today)
    if not late:
        print("Nothing overdue. Stay lazy.")
        return

    if args.brief:
        text = brief_for(data, today, args.model)
        print(text)
        if args.speak:
            out = Path("brief.mp3")
            speak(text, out)
            print(f"\nsaved {out} — play it and stay in bed.")
        return

    print(f"{len(late)} overdue — nudges ready to paste:\n")
    for owner, draft in nudges_for(data, today, args.tone, args.model).items():
        print(f"--- to {owner} ---\n{draft}\n")


if __name__ == "__main__":
    main()
