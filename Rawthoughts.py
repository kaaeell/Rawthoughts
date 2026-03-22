# rawthoughts.py
#
# i made this because i kept losing thoughts between tabs.
# you just type whatever's in your head and it sorts it out.
# no setup, no accounts, just run it.

import json
import os
import re
import sys
from datetime import datetime, date

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

CATEGORIES = {
    "TODO": {
        "keywords": [
            "need to", "have to", "don't forget", "to do", "gotta", "must",
            "should", "fix", "finish", "buy", "call", "email", "remind",
            "todo", "check", "update", "schedule", "pay", "send", "reply",
        ],
    },
    "IDEA": {
        "keywords": [
            "what if", "would be cool", "why not", "could be", "idea",
            "maybe", "could", "imagine", "app", "project", "build", "create",
            "make", "feature", "concept", "potential", "possible", "pitch",
            "startup", "tool",
        ],
    },
    "FEELING": {
        "keywords": [
            "feel like", "feeling", "feel", "happy", "sad", "angry",
            "anxious", "worried", "excited", "tired", "stressed", "love",
            "hate", "miss", "scared", "frustrated", "proud", "grateful",
            "lonely", "bored", "nervous", "overwhelmed", "calm", "annoyed",
            "confused", "lost", "hope",
        ],
    },
}

CAT_META = {
    "TODO":    (GREEN,   "✅"),
    "IDEA":    (CYAN,    "💡"),
    "FEELING": (MAGENTA, "💭"),
    "RANDOM":  (YELLOW,  "🌀"),
}

PIN_ICON = f"{YELLOW}📌{RESET}"


def classify(text):
    lower = text.lower()
    scores = {cat: 0 for cat in CATEGORIES}
    for cat, data in CATEGORIES.items():
        for kw in data["keywords"]:
            pattern = r'\b' + re.escape(kw) + r'\b'
            matches = re.findall(pattern, lower)
            weight = 2 if " " in kw else 1
            scores[cat] += len(matches) * weight
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


def get_streak(thoughts):
    """Count consecutive days (ending today) that have at least one thought."""
    if not thoughts:
        return 0
    days = sorted({t["timestamp"][:10] for t in thoughts}, reverse=True)
    streak = 0
    check = date.today()
    for d in days:
        if date.fromisoformat(d) == check:
            streak += 1
            prev = check.toordinal() - 1
            check = date.fromordinal(prev)
        else:
            break
    return streak


def sorted_thoughts(thoughts):
    """Pinned thoughts always first, rest in original order."""
    pinned = [t for t in thoughts if t.get("pinned")]
    rest   = [t for t in thoughts if not t.get("pinned")]
    return pinned + rest


def fmt_thought(t, idx):
    ts = t["timestamp"][:16].replace("T", " ")
    c, icon = CAT_META.get(t["category"], (WHITE, "•"))
    tag = f"{c}{BOLD}[{icon} {t['category']}]{RESET}"
    pin = f" {PIN_ICON}" if t.get("pinned") else ""
    return f"  {GRAY}{idx:>3}.{RESET} {tag}{pin} {WHITE}{t['text']}{RESET}  {DIM}{ts}{RESET}"


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
        t = {"text": raw, "category": classify(raw), "timestamp": datetime.now().isoformat(), "pinned": False}
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
    display = list(reversed(sorted_thoughts(thoughts)))
    print(f"\n  {BOLD}everything ({len(display)} thoughts):{RESET}\n")
    for i, t in enumerate(display, 1):
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
            pin = f" {PIN_ICON}" if t.get("pinned") else ""
            print(f"  {WHITE}{t['text']}{RESET}{pin}  {DIM}{ts}{RESET}")
    print()


def search_mode(thoughts):
    if not thoughts:
        print(f"\n  {DIM}nothing to search yet.{RESET}\n")
        return
    try:
        query = input(f"\n  {BOLD}search:{RESET} ").strip().lower()
    except EOFError:
        return
    if not query:
        return
    results = [t for t in thoughts if query in t["text"].lower()]
    if not results:
        print(f"\n  {DIM}no matches for '{query}'{RESET}\n")
        return
    display = list(reversed(sorted_thoughts(thoughts)))
    print(f"\n  {BOLD}{len(results)} result{'s' if len(results) != 1 else ''} for '{query}':{RESET}\n")
    for i, t in enumerate(display, 1):
        if t in results:
            highlighted = re.sub(
                f"({re.escape(query)})",
                f"{YELLOW}\\1{RESET}{WHITE}",
                t["text"],
                flags=re.IGNORECASE,
            )
            ts = t["timestamp"][:16].replace("T", " ")
            c, icon = CAT_META.get(t["category"], (WHITE, "•"))
            tag = f"{c}{BOLD}[{icon} {t['category']}]{RESET}"
            pin = f" {PIN_ICON}" if t.get("pinned") else ""
            print(f"  {GRAY}{i:>3}.{RESET} {tag}{pin} {WHITE}{highlighted}{RESET}  {DIM}{ts}{RESET}")
    print()


def _pick_thought(thoughts, prompt):
    """Show list, ask for a number, return (real_index, thought) or (None, None)."""
    view_all(thoughts)
    try:
        raw = input(f"  {BOLD}{prompt} (or 'cancel'):{RESET} ").strip().lower()
    except EOFError:
        return None, None
    if raw in ("cancel", "c", "q", ""):
        print(f"  cancelled.\n")
        return None, None
    try:
        idx = int(raw)
        display = list(reversed(sorted_thoughts(thoughts)))
        if not (1 <= idx <= len(display)):
            raise ValueError
        t = display[idx - 1]
        real_idx = thoughts.index(t)
        return real_idx, t
    except ValueError:
        print(f"  {RED}invalid number.{RESET}\n")
        return None, None


def edit_mode(thoughts):
    if not thoughts:
        print(f"\n  {DIM}nothing to edit yet.{RESET}\n")
        return
    real_idx, t = _pick_thought(thoughts, "enter number to edit")
    if t is None:
        return
    print(f"\n  {DIM}editing:{RESET} {WHITE}{t['text']}{RESET}")
    try:
        new_text = input(f"  {BOLD}new text:{RESET} ").strip()
    except EOFError:
        return
    if not new_text:
        print(f"  cancelled.\n")
        return
    thoughts[real_idx]["text"] = new_text
    thoughts[real_idx]["category"] = classify(new_text)
    thoughts[real_idx]["edited"] = datetime.now().isoformat()
    c, icon = CAT_META.get(thoughts[real_idx]["category"], (WHITE, "•"))
    print(f"  {DIM}↳ re-tagged as {c}{icon} {thoughts[real_idx]['category']}{RESET}\n")
    save(thoughts)
    print(f"  {GREEN}updated.{RESET}\n")


def pin_mode(thoughts):
    if not thoughts:
        print(f"\n  {DIM}nothing to pin yet.{RESET}\n")
        return
    real_idx, t = _pick_thought(thoughts, "enter number to pin/unpin")
    if t is None:
        return
    thoughts[real_idx]["pinned"] = not thoughts[real_idx].get("pinned", False)
    state = "pinned 📌" if thoughts[real_idx]["pinned"] else "unpinned"
    save(thoughts)
    print(f"  {GREEN}{state}:{RESET} {WHITE}{t['text']}{RESET}\n")


def delete_mode(thoughts):
    if not thoughts:
        print(f"\n  {DIM}nothing to delete.{RESET}\n")
        return
    real_idx, t = _pick_thought(thoughts, "enter number to delete")
    if t is None:
        return
    c, icon = CAT_META.get(t["category"], (WHITE, "•"))
    print(f"\n  {DIM}deleting:{RESET} {c}{icon}{RESET} {WHITE}{t['text']}{RESET}")
    confirm = input(f"  {RED}sure? (yes/no):{RESET} ").strip().lower()
    if confirm == "yes":
        thoughts.pop(real_idx)
        save(thoughts)
        print(f"  {DIM}gone.{RESET}\n")
    else:
        print(f"  cancelled.\n")


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

    streak = get_streak(thoughts)
    if streak:
        print(f"\n  {YELLOW}🔥 {streak}-day streak{RESET}")

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
    pinned = [t for t in thoughts if t.get("pinned")]
    if pinned:
        lines.append("\n## 📌 pinned\n")
        for t in pinned:
            ts = t["timestamp"][:16].replace("T", " ")
            lines.append(f"- {t['text']}  _{ts}_")
    for cat in ["TODO", "IDEA", "FEELING", "RANDOM"]:
        items = [t for t in thoughts if t["category"] == cat and not t.get("pinned")]
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
        streak = get_streak(thoughts)
        streak_str = f"  {YELLOW}🔥 {streak}d{RESET}" if streak >= 2 else ""
        print(f"  {' · '.join(parts)}  {DIM}({total} total){RESET}{streak_str}\n")

    print(f"  {GREEN}d{RESET} dump   {GREEN}v{RESET} view all   {GREEN}c{RESET} by category")
    print(f"  {GREEN}s{RESET} stats  {GREEN}/{RESET} search     {GREEN}e{RESET} export")
    print(f"  {GREEN}u{RESET} edit   {GREEN}p{RESET} pin        {GREEN}r{RESET} delete")
    print(f"  {GREEN}x{RESET} clear  {GREEN}q{RESET} quit")
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
        elif choice == "/":
            search_mode(thoughts)
            input(f"  {DIM}enter to go back{RESET}")
        elif choice == "u":
            edit_mode(thoughts)
            input(f"  {DIM}enter to go back{RESET}")
        elif choice == "p":
            pin_mode(thoughts)
            input(f"  {DIM}enter to go back{RESET}")
        elif choice == "r":
            delete_mode(thoughts)
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
