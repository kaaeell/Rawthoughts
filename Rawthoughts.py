# rawthoughts.py
#
# i made this because i kept losing thoughts between tabs.
# you just type whatever's in your head and it sorts it out.
# no setup, no accounts, just run it.

import json
import os
import sys
from datetime import datetime

SAVE_FILE = os.path.join(os.path.dirname(__file__), ".rawthoughts.json")

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
GRAY    = "\033[90m"
WHITE   = "\033[97m"

# keyword lists aren't perfect but they don't need to be
CATEGORIES = {
    "TODO": {
        "color": GREEN,
        "icon": "✅",
        "keywords": [
            "need to", "should", "must", "have to", "gotta", "fix", "finish",
            "buy", "call", "email", "remind", "todo", "to do", "check", "update",
            "don't forget", "remember", "schedule", "pay", "send", "reply",
        ],
    },
    "IDEA": {
        "color": CYAN,
        "icon": "💡",
        "keywords": [
            "what if", "idea", "maybe", "could", "imagine", "would be cool",
            "app", "project", "build", "create", "make", "feature", "concept",
            "why not", "potential", "possible", "pitch", "startup", "tool",
        ],
    },
    "FEELING": {
        "color": MAGENTA,
        "icon": "💭",
        "keywords": [
            "feel", "feeling", "happy", "sad", "angry", "anxious", "worried",
            "excited", "tired", "stressed", "love", "hate", "miss", "scared",
            "frustrated", "proud", "grateful", "lonely", "bored", "nervous",
            "overwhelmed", "calm", "annoyed", "confused", "lost", "hope",
        ],
    },
}

CAT_META = {
    "TODO":    (GREEN,   "✅"),
    "IDEA":    (CYAN,    "💡"),
    "FEELING": (MAGENTA, "💭"),
    "RANDOM":  (YELLOW,  "🌀"),
}


def classify(text):
    lower = text.lower()
    scores = {cat: 0 for cat in CATEGORIES}
    for cat, data in CATEGORIES.items():
        for kw in data["keywords"]:
            if kw in lower:
                scores[cat] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "RANDOM"


def load():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f:
            return json.load(f)
    return []


def save(thoughts):
    with open(SAVE_FILE, "w") as f:
        json.dump(thoughts, f, indent=2)


def fmt_thought(t, idx):
    ts = t["timestamp"][:16].replace("T", " ")
    c, icon = CAT_META.get(t["category"], (WHITE, "•"))
    tag = f"{c}{BOLD}[{icon} {t['category']}]{RESET}"
    return f"  {GRAY}{idx:>3}.{RESET} {tag} {WHITE}{t['text']}{RESET}  {DIM}{ts}{RESET}"


def dump_mode(thoughts):
    print(f"\n  {BOLD}just type. hit enter after each thought. 'done' when you're done.{RESET}\n")
    added = 0
    while True:
        try:
            raw = input(f"  {GRAY}>{RESET} ").strip()
        except EOFError:
            break
        if raw.lower() in ("done", "exit", "quit", "q"):
            break
        if not raw:
            continue
        t = {"text": raw, "category": classify(raw), "timestamp": datetime.now().isoformat()}
        thoughts.append(t)
        c, icon = CAT_META.get(t["category"], (WHITE, "•"))
        print(f"  {DIM}↳ {c}{icon} {t['category']}{RESET}\n")
        added += 1
    save(thoughts)
    print(f"\n  {GREEN}saved {added} thought{'s' if added != 1 else ''}{RESET}\n")


def view_all(thoughts):
    if not thoughts:
        print(f"\n  {DIM}nothing here yet.{RESET}\n")
        return
    print(f"\n  {BOLD}everything ({len(thoughts)} thoughts):{RESET}\n")
    for i, t in enumerate(reversed(thoughts), 1):
        print(fmt_thought(t, i))
    print()


def view_by_category(thoughts):
    if not thoughts:
        print(f"\n  {DIM}nothing yet.{RESET}\n")
        return
    for cat in ["TODO", "IDEA", "FEELING", "RANDOM"]:
        items = [t for t in thoughts if t["category"] == cat]
        if not items:
            continue
        c, icon = CAT_META[cat]
        print(f"\n  {c}{BOLD}{icon} {cat} — {len(items)}{RESET}")
        print(f"  {GRAY}{'─' * 38}{RESET}")
        for t in reversed(items[-10:]):
            ts = t["timestamp"][:16].replace("T", " ")
            print(f"  {WHITE}{t['text']}{RESET}  {DIM}{ts}{RESET}")
    print()


def stats(thoughts):
    if not thoughts:
        print(f"\n  {DIM}no data yet.{RESET}\n")
        return
    total = len(thoughts)
    counts = {}
    for t in thoughts:
        counts[t["category"]] = counts.get(t["category"], 0) + 1

    print(f"\n  {BOLD}{total} thoughts total{RESET}\n")
    for cat in ["TODO", "IDEA", "FEELING", "RANDOM"]:
        n = counts.get(cat, 0)
        pct = round((n / total) * 100) if total else 0
        c, icon = CAT_META[cat]
        bar = "█" * (pct // 5)
        print(f"  {c}{icon} {cat:<8}{RESET}  {WHITE}{bar:<20}{RESET}  {DIM}{n} ({pct}%){RESET}")

    oldest = thoughts[0]
    print(f"\n  {DIM}first thought logged {oldest['timestamp'][:10]}{RESET}")
    print(f"  {DIM}it was: \"{oldest['text'][:60]}\"{RESET}\n")


def export_markdown(thoughts):
    if not thoughts:
        print(f"\n  {DIM}nothing to export.{RESET}\n")
        return
    path = os.path.join(os.path.dirname(__file__), "rawthoughts_export.md")
    lines = [
        "# rawthoughts export",
        f"\n_{datetime.now().strftime('%Y-%m-%d %H:%M')}_\n",
    ]
    icons = {"TODO": "✅", "IDEA": "💡", "FEELING": "💭", "RANDOM": "🌀"}
    for cat in ["TODO", "IDEA", "FEELING", "RANDOM"]:
        items = [t for t in thoughts if t["category"] == cat]
        if not items:
            continue
        lines.append(f"\n## {icons[cat]} {cat.lower()}\n")
        for t in items:
            ts = t["timestamp"][:16].replace("T", " ")
            lines.append(f"- {t['text']}  _{ts}_")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"\n  {GREEN}exported to {path}{RESET}\n")


def clear_all(thoughts):
    confirm = input(f"\n  {RED}wipe all {len(thoughts)} thoughts? (yes/no): {RESET}").strip().lower()
    if confirm == "yes":
        thoughts.clear()
        save(thoughts)
        print(f"  {DIM}clean slate.{RESET}\n")
    else:
        print(f"  cancelled.\n")


def header(thoughts):
    total = len(thoughts)
    counts = {}
    for t in thoughts:
        counts[t["category"]] = counts.get(t["category"], 0) + 1

    print(f"\n{BOLD}{CYAN}  rawthoughts{RESET}  {DIM}— dump your head, sort it later{RESET}\n")

    if total:
        parts = []
        for cat in ["TODO", "IDEA", "FEELING", "RANDOM"]:
            n = counts.get(cat, 0)
            if n:
                c, icon = CAT_META[cat]
                parts.append(f"{c}{icon} {n}{RESET}")
        print(f"  {' · '.join(parts)}  {DIM}({total} total){RESET}\n")

    print(f"  {GREEN}d{RESET} dump   {GREEN}v{RESET} view all   {GREEN}c{RESET} by category")
    print(f"  {GREEN}s{RESET} stats  {GREEN}e{RESET} export     {GREEN}x{RESET} clear")
    print(f"  {GREEN}q{RESET} quit")
    print(f"  {GRAY}{'─' * 36}{RESET}")


def main():
    thoughts = load()
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        header(thoughts)

        choice = input("\n  > ").strip().lower()

        if choice == "d":
            dump_mode(thoughts)
            input(f"  {DIM}enter to go back{RESET}")
        elif choice == "v":
            view_all(thoughts)
            input(f"  {DIM}enter to go back{RESET}")
        elif choice == "c":
            view_by_category(thoughts)
            input(f"  {DIM}enter to go back{RESET}")
        elif choice == "s":
            stats(thoughts)
            input(f"  {DIM}enter to go back{RESET}")
        elif choice == "e":
            export_markdown(thoughts)
            input(f"  {DIM}enter to go back{RESET}")
        elif choice == "x":
            clear_all(thoughts)
            input(f"  {DIM}enter to go back{RESET}")
        elif choice == "q":
            os.system("cls" if os.name == "nt" else "clear")
            print(f"\n  {DIM}later. your thoughts are safe.{RESET}\n")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {DIM}saved. go touch some grass.{RESET}\n")
        sys.exit(0)