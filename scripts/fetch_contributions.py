"""Scrape the public contribution calendar into data/contributions.json."""
import json, re, sys, urllib.request
from pathlib import Path

USER = "prashx1908"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

html = urllib.request.urlopen(
    urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                           headers={"User-Agent": "profile-readme-cards"})
).read().decode()

days = {}
for m in re.finditer(r'data-date="(\d{4}-\d\d-\d\d)"[^>]*?id="([^"]+)"', html):
    days[m.group(2)] = {"date": m.group(1), "count": 0}
for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>\s*([^<]*?)\s*</tool-tip>', html):
    n = re.match(r"(\d+) contribution", m.group(2))
    if m.group(1) in days and n:
        days[m.group(1)]["count"] = int(n.group(1))

rows = sorted(days.values(), key=lambda d: d["date"])
if not rows:
    sys.exit("no contribution data found")
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({"user": USER, "days": rows}, indent=1))
print(f"{len(rows)} days, {sum(d['count'] for d in rows)} contributions")
