"""Rebuild README.md for the learning log: today's prefilled entry link, stats and an index.

Entries live in entries/YYYY/YYYY-MM-DD.md (add -2, -3 ... for a second entry the same day).
Run:  python build_readme.py      (the GitHub Action runs it on every push and once a day)
"""
import collections
import datetime as dt
import re
import urllib.parse
from pathlib import Path

REPO = "chasemcapron/learning-log"
ROOT = Path(__file__).parent
CENTRAL = dt.timezone(dt.timedelta(hours=-6))
G = "39FF88"


def badge(label, logo_svg=None):
    return f"https://img.shields.io/badge/{urllib.parse.quote(label)}-161b22?style=for-the-badge&logoColor={G}" + (
        f"&logo={logo_svg}" if logo_svg else "")


def parse_minutes(s):
    s = s.lower()
    h = re.search(r"(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours)\b", s)
    m = re.search(r"(\d+)\s*(m|min|mins|minute|minutes)\b", s)
    total = (float(h.group(1)) * 60 if h else 0) + (int(m.group(1)) if m else 0)
    if not h and not m and re.fullmatch(r"\s*\d+\s*", s):
        total = int(s)
    return total


def read_entries():
    out = []
    for f in sorted((ROOT / "entries").rglob("*.md")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})", f.stem)
        if not m:
            continue
        text = f.read_text(encoding="utf-8")
        title = re.search(r"^#\s+(.+)$", text, re.M)
        field = lambda name: (re.search(rf"\*\*{name}:\*\*\s*(.+)", text) or [None, ""])[1].strip()
        out.append({
            "date": dt.date.fromisoformat(m.group(1)),
            "path": f.relative_to(ROOT).as_posix(),
            "title": title.group(1).strip() if title else f.stem,
            "topic": field("Topic") or "Other",
            "minutes": parse_minutes(field("Time spent")),
        })
    return sorted(out, key=lambda e: (e["date"], e["path"]), reverse=True)


def streak(dates, today):
    days = set(dates)
    d = today if today in days else today - dt.timedelta(days=1)
    n = 0
    while d in days:
        n += 1
        d -= dt.timedelta(days=1)
    return n


def main():
    today = dt.datetime.now(CENTRAL).date()
    entries = read_entries()
    template = (ROOT / "TEMPLATE.md").read_text(encoding="utf-8").replace("{{DATE}}", today.isoformat())
    taken = {e["path"] for e in entries}
    name = f"entries/{today.year}/{today.isoformat()}.md"
    k = 2
    while name in taken:
        name = f"entries/{today.year}/{today.isoformat()}-{k}.md"
        k += 1
    new_url = (f"https://github.com/{REPO}/new/main?"
               + urllib.parse.urlencode({"filename": name, "value": template}, quote_via=urllib.parse.quote))

    hours = sum(e["minutes"] for e in entries) / 60
    cur = streak([e["date"] for e in entries], today)
    topics = collections.Counter(e["topic"] for e in entries)
    days_active = len({e["date"] for e in entries})

    pen = "data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTEyIDV2MTRNNSAxMmgxNCIgc3Ryb2tlPSIjMzlGRjg4IiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjwvc3ZnPg=="
    lines = [
        '<div align="center">',
        "",
        '<img src="assets/banner.svg" alt="LEARNING LOG" width="640">',
        "",
        "**Daily notes on what I'm learning in cybersecurity.**",
        "",
        f'<a href="{new_url}"><img src="{badge("write today" + chr(39) + "s entry", pen)}" alt="Write today\'s entry"></a>',
        "",
        f"`{len(entries)} ENTRIES` &nbsp; `{cur}-DAY STREAK` &nbsp; `{days_active} DAYS LOGGED` &nbsp; `{hours:.1f} HOURS`",
        "",
        "</div>",
        "",
        "### `$ ls -t entries/`",
        "",
    ]
    if entries:
        lines += ["| Date | What I learned | Topic | Time |", "| :-- | :-- | :-- | --: |"]
        for e in entries[:20]:
            t = f"{e['minutes']:.0f} min" if e["minutes"] else ""
            title = e["title"].replace("|", "\\|")
            lines.append(f"| {e['date']:%b %d} | [{title}]({e['path']}) | `{e['topic']}` | {t} |")
        if len(entries) > 20:
            lines += ["", f"<sub>Older entries: [entries/](entries/)</sub>"]
    else:
        lines.append("> No entries yet. Click **Write today's entry** above to log the first one.")
    lines += ["", "### `$ sort topics | uniq -c`", ""]
    if topics:
        lines.append(" &nbsp; ".join(f"`{t} · {n}`" for t, n in topics.most_common()))
    else:
        lines.append("> Topics show up here as you log entries.")
    lines += [
        "",
        "### `$ cat HOW_TO.md`",
        "",
        "1. Click **Write today's entry**. GitHub opens a new file with today's date and the template filled in.",
        "2. Replace the example text, keep it short, and click **Commit changes**.",
        "3. This page updates itself within a minute: index, topics, streak and hours.",
        "",
        "<sub>Template: [TEMPLATE.md](TEMPLATE.md) · README rebuilt by `build_readme.py`</sub>",
        "",
    ]
    (ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"README: {len(entries)} entries, streak {cur}, {hours:.1f} h, link -> {name}")


if __name__ == "__main__":
    main()
