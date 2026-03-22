# rawthoughts
dump your head. don't filter. it'll sort itself out.

---

i built this because i was tired of losing half-formed thoughts between browser tabs and sticky notes. no app, no login, no cloud. just open a terminal, type, close it. your thoughts sit in a little json file on your machine and mind their own business.

it auto-tags everything into **todo**, **idea**, **feeling**, or **random** based on what you wrote. it's not perfect — nothing is — but it's fast.

---

## getting started

```bash
git clone https://github.com/your-username/rawthoughts.git
cd rawthoughts
python rawthoughts.py
```

python 3.8+. no installs. no dependencies. nothing.

---

## usage

```
  rawthoughts  — dump your head, sort it later

  ✅ 4 · 💡 7 · 💭 2 · 🌀 3  (16 total)  🔥 3d

  d dump   v view all   c by category
  s stats  / search     e export
  u edit   p pin        r delete
  x clear  q quit
```

hit `d` and just type:

```
  > need to reply to that email from tuesday
  ↳ ✅ TODO

  > what if notes apps just didn't exist and we were all fine
  ↳ 💡 IDEA

  > feeling kind of burnt out honestly
  ↳ 💭 FEELING

  > a fork is just an aggressive spoon
  ↳ 🌀 RANDOM
```

---

## what the keys do

| key | what it does |
|-----|-------------|
| `d` | dump mode — just type until you're empty |
| `v` | everything, newest first. pinned thoughts float to the top. |
| `c` | grouped by tag |
| `s` | breakdown of what's in your head + streak |
| `/` | search across all your thoughts, matches highlighted |
| `u` | edit a thought by number — re-tags automatically |
| `p` | pin / unpin a thought so it stays at the top |
| `r` | delete a thought by number |
| `e` | export to a markdown file |
| `x` | wipe it all. fresh start. |
| `q` | quit (saves automatically) |

---

## how tagging works

it scans your text for keywords using word-boundary matching, so "fixed" won't accidentally trigger "fix". multi-word phrases like "need to" or "what if" score double, so longer matches win over coincidental single-word hits. if nothing sticks, it goes to **random**.

roughly what each tag looks for:

- **todo** — "need to", "gotta", "fix", "remind", "schedule", "don't forget" …
- **idea** — "what if", "would be cool", "build", "startup" …
- **feeling** — "feel", "tired", "anxious", "grateful", "overwhelmed" …
- **random** — everything else. often the best stuff.

it's intentionally simple. the point is speed, not a perfect classifier.

---

## files it creates

- `.rawthoughts.json` — where your thoughts live. hidden, local, yours.
- `rawthoughts_export.md` — only appears when you hit `e` to export. pinned thoughts get their own section at the top.

---

## why not notion / obsidian / [your app here]

because sometimes you just want to open a terminal and type. no mouse, no sidebar, no plugins to configure. this is that.

---

mit license. do whatever.
