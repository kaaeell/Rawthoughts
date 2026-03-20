# rawthoughts

dump your head. don't filter. it'll sort itself out.

---

i built this because i was tired of losing half-formed thoughts between browser tabs and sticky notes. no app, no login, no cloud. just open it, type, close it. your thoughts sit in a little json file on your machine and mind their own business.

it auto-tags everything into **todo**, **idea**, **feeling**, or **random** based on what you wrote. it's not perfect — nothing is — but it's good enough.

```
  rawthoughts  — dump your head, sort it later

  ✅ 4 · 💡 7 · 💭 2 · 🌀 3  (16 total)

  d dump   v view all   c by category
  s stats  e export     x clear
  q quit

  > d

  just type. hit enter after each thought. 'done' when you're done.

  > need to reply to that email from tuesday
  ↳ ✅ TODO

  > what if notes apps just didn't exist and we were all fine
  ↳ 💡 IDEA

  > feeling kind of burnt out honestly
  ↳ 💭 FEELING

  > a fork is just a aggressive spoon
  ↳ 🌀 RANDOM
```

---

## getting started

```bash
git clone https://github.com/your-username/rawthoughts.git
cd rawthoughts
python rawthoughts.py
```

python 3.8+. no installs. no requirements.txt. nothing.

---

## what the keys do

| key | what it does |
|-----|-------------|
| `d` | dump mode — just type until you're empty |
| `v` | see everything in reverse chronological order |
| `c` | grouped by tag |
| `s` | breakdown of what's in your head |
| `e` | export everything to a markdown file |
| `x` | wipe it all. fresh start. |
| `q` | quit (saves automatically) |

---

## how the tagging works

it scans your text for keywords and picks a tag. if nothing matches, it goes to random. here's roughly what it looks for:

- **todo** — "need to", "gotta", "fix", "remind", "schedule" etc.
- **idea** — "what if", "would be cool", "build", "startup" etc.
- **feeling** — "feel", "tired", "anxious", "grateful", "overwhelmed" etc.
- **random** — everything else. the good stuff usually.

it's a dumb classifier on purpose. the point is speed, not accuracy.

---

## files it creates

- `.rawthoughts.json` — where your thoughts live (hidden file, stays local)
- `rawthoughts_export.md` — only created when you hit `e` to export

---

## why not just use notion / obsidian / [insert app]

because sometimes you just want to open a terminal and type. no mouse, no formatting, no plugins. this is that.

---

mit license. do whatever.
