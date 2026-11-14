"""Render animated dark-terminal SVG cards for the profile README.

STATIC=1 renders the final frame with no animation (for screenshots).
"""
import base64, calendar, datetime as dt, json, os
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape as esc

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cards"
STATIC = os.environ.get("STATIC") == "1"

BG, PANEL, LINE = "#0d1117", "#161b22", "#30363d"
FG, DIM, MUTE = "#e6edf3", "#8b949e", "#484f58"
GREEN, AMBER, CYAN, PINK = "#3fb950", "#e3b341", "#58a6ff", "#f778ba"
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
SITE = "https://prashx1908.github.io/devPrash/"
CW = 0.6  # monospace advance in em


def font_css():
    out = ""
    for w in (400, 700):
        b64 = base64.b64encode((ROOT / "fonts" / f"mono-{w}.woff2").read_bytes()).decode()
        out += (f"@font-face{{font-family:'JB';font-weight:{w};"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return out


KEYFRAMES = """
@keyframes rise{from{opacity:0;transform:translateY(10px)}}
@keyframes fade{from{opacity:0}}
@keyframes grow{from{transform:scaleY(0)}}
@keyframes pop{from{opacity:0;transform:scale(.2)}}
@keyframes swing{0%{opacity:0;transform:translateY(40px) rotate(-3deg)}
 60%{opacity:1;transform:translateY(-5px) rotate(.6deg)}100%{transform:none}}
@keyframes blink{50%{opacity:0}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
@keyframes ring{from{opacity:.7;transform:scale(.4)}to{opacity:0;transform:scale(2.6)}}
@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(4px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def anim(name, delay, dur=0.6, ease="ease-out", extra=""):
    if STATIC:
        return ""
    return (f'style="animation:{name} {dur}s {ease} {delay:.2f}s backwards;'
            f'transform-box:fill-box;transform-origin:{extra or "center"}"')


def wrap(w, h, body, defs=""):
    css = font_css() + (("" if STATIC else KEYFRAMES))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="JB,monospace">'
            f'<defs><style>{css} text{{white-space:pre}}</style>{defs}</defs>{body}</svg>')


def window(w, h, title, delay=0.0):
    return (f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{BG}" stroke="{LINE}"/>'
            f'<path d="M.5 40H{w-.5}" stroke="{LINE}"/>'
            f'<circle cx="24" cy="21" r="6" fill="#ff5f56"/><circle cx="44" cy="21" r="6" fill="#ffbd2e"/>'
            f'<circle cx="64" cy="21" r="6" fill="#27c93f"/>'
            f'<text x="86" y="26" font-size="12" fill="{DIM}">{esc(title)}</text>')


def text(x, y, s, size=14, fill=FG, weight=400, delay=None, extra=""):
    a = anim("rise", delay, 0.5, extra="left center") if delay is not None else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" {extra} {a}>{s}</text>'


# ---------- data ----------
def load():
    d = json.loads((ROOT / "data" / "contributions.json").read_text())["days"]
    return [(dt.date.fromisoformat(x["date"]), x["count"]) for x in d]


def stats(days):
    total = sum(c for _, c in days)
    active = sum(1 for _, c in days if c)
    best = max(days, key=lambda x: x[1])
    longest = cur = 0
    for _, c in days:
        cur = cur + 1 if c else 0
        longest = max(longest, cur)
    cur = 0
    for _, c in reversed(days):
        if c:
            cur += 1
        elif cur or _ != days[-1][0]:
            break
    return total, active, best, longest, cur


# ---------- cards ----------
def hero():
    w, h = 830, 330
    b = window(w, h, "prashanth@jpmc: ~ — zsh")
    b += text(28, 78, f'<tspan fill="{GREEN}">$</tspan> whoami', 14, DIM, delay=0.1)
    grad = ('<linearGradient id="sh" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="260" y2="0">'
            f'<stop offset="0" stop-color="{FG}"/><stop offset=".45" stop-color="{FG}"/>'
            f'<stop offset=".5" stop-color="{GREEN}"/><stop offset=".55" stop-color="{FG}"/>'
            f'<stop offset="1" stop-color="{FG}"/>'
            + ("" if STATIC else
               '<animateTransform attributeName="gradientTransform" type="translate" '
               'from="-300 0" to="400 0" dur="3.5s" begin="2s;sh.end+3s" repeatCount="indefinite"/>')
            + '</linearGradient>')
    b += text(28, 138, "Prashanth G", 52, "url(#sh)", 700, delay=0.3)
    b += text(28, 172, f'Software Engineer I <tspan fill="{GREEN}">@ JPMorgan Chase</tspan>', 17, FG, delay=0.6)
    b += text(28, 200, "since Aug 2026 · Bangalore, India", 13, DIM, delay=0.8)
    lines = ["B.Tech CSE · SRM IST · CGPA 9.85",
             "Machine learning, full-stack, UI/UX design",
             "Ex-President @ DSC SRM Ramapuram (1500+ members)",
             "Photographer on the side"]
    for i, l in enumerate(lines):
        b += text(28, 240 + i * 22, f'<tspan fill="{MUTE}">›</tspan> {esc(l)}', 13, DIM, delay=1.0 + i * 0.2)
    cur_a = "" if STATIC else f'style="animation:blink 1s steps(1) infinite"'
    b += f'<rect x="{28 + (len(lines[-1]) + 2) * 13 * CW + 4}" y="{240 + 3*22 - 12}" width="8" height="15" fill="{GREEN}" {cur_a}/>'
    # neofetch panel
    px, py = 520, 62
    b += f'<rect x="{px}" y="{py}" width="286" height="246" rx="8" fill="{PANEL}" stroke="{LINE}" {anim("fade", 0.9)}/>'
    rows = [("role", "SWE I, JPMorgan Chase", GREEN), ("focus", "ML · full-stack · UI/UX", CYAN),
            ("stack", "Python · React · Django", AMBER), ("repos", "66 public", FG),
            ("award", "1st · WTM She Innovates", PINK), ("also", "MIT Square research", FG),
            ("status", "shipping", GREEN)]
    for i, (k, v, c) in enumerate(rows):
        y = py + 38 + i * 29
        b += text(px + 18, y, f'<tspan fill="{DIM}">{k:<7}</tspan><tspan fill="{c}">{esc(v)}</tspan>', 12.5, FG, delay=1.1 + i * 0.12)
    dot = "" if STATIC else 'style="animation:pulse 1.6s ease-in-out infinite"'
    b += f'<circle cx="{px+18+7*CW*12.5+ len("shipping")*CW*12.5 + 10}" cy="{py+38+6*29-4}" r="4" fill="{GREEN}" {dot}/>'
    return wrap(w, h, b, grad)


def graph(days):
    w, h = 830, 200
    total = sum(c for _, c in days)
    b = window(w, h, "git log --graph --since='1 year ago'")
    b += text(28, 70, f'<tspan fill="{GREEN}">{total}</tspan> contributions in the last year', 13, DIM, delay=0.2)
    mx = max(c for _, c in days) or 1
    start = days[0][0]
    first_sun = start - dt.timedelta(days=(start.weekday() + 1) % 7)
    x0, y0, pitch = 30, 88, 14
    for d, c in days:
        col = (d - first_sun).days // 7
        row = (d.weekday() + 1) % 7
        lvl = 0 if c == 0 else min(4, 1 + int(c * 3.99 / mx))
        delay = 0.4 + col * 0.03
        b += (f'<rect x="{x0 + col*pitch}" y="{y0 + row*pitch}" width="11" height="11" rx="2" '
              f'fill="{LEVELS[lvl]}" {anim("pop", delay, 0.35)}/>')
    return wrap(w, h, b)


def activity(days):
    w, h = 830, 270
    total, active, best, longest, cur = stats(days)
    b = window(w, h, "contributions --by-month")
    per = defaultdict(int)
    for d, c in days:
        per[(d.year, d.month)] += c
    last = days[-1][0]
    months = []
    y, m = last.year, last.month
    for _ in range(12):
        months.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    months.reverse()
    vals = [per[k] for k in months]
    mx = max(vals) or 1
    top = vals.index(mx)
    base, maxh, bw, pitch = 200, 100, 36, 50
    b += f'<path d="M28 {base}H{28+12*pitch}" stroke="{LINE}"/>'
    for i, (k, v) in enumerate(zip(months, vals)):
        x = 34 + i * pitch
        bh = max(3, v / mx * maxh) if v else 3
        col = GREEN if i == top and v else "#1f3a2a"
        b += (f'<rect x="{x}" y="{base-bh}" width="{bw}" height="{bh}" rx="3" fill="{col}" '
              f'{anim("grow", 0.3 + i*0.07, 0.6, extra="bottom")}/>')
        b += f'<text x="{x+bw/2}" y="{base+18}" font-size="11" fill="{DIM}" text-anchor="middle">{calendar.month_abbr[k[1]]}</text>'
        if v and i == top:
            b += (f'<text x="{x+bw/2}" y="{base-bh-8}" font-size="13" font-weight="700" fill="{GREEN}" '
                  f'text-anchor="middle" {anim("pop", 1.4, 0.4)}>{v}</text>')
    sx = 660
    items = [("current streak", f"{cur}d"), ("longest streak", f"{longest}d"), ("active days", str(active)),
             ("busiest day", f"{best[1]} · {best[0].strftime('%b %d')}")]
    for i, (k, v) in enumerate(items):
        y = 78 + i * 46
        b += text(sx, y, k, 11, DIM, delay=0.8 + i * 0.15)
        b += text(sx, y + 22, esc(v), 20, FG, 700, delay=0.9 + i * 0.15)
    return wrap(w, h, b)


def tile(name, color, count, label, sub, arrow_delay=0):
    w, h = 270, 190
    c = f'<g {anim("swing", 0.2 + arrow_delay, 0.9, "cubic-bezier(.2,.8,.3,1)")}>'
    c += f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{PANEL}" stroke="{color}" stroke-opacity=".5"/>'
    c += f'<rect x="20" y="22" width="8" height="8" rx="2" fill="{color}"/>'
    c += f'<text x="36" y="30" font-size="12" font-weight="700" letter-spacing="2" fill="{color}">{name}</text>'
    ring = "" if STATIC else (f'style="animation:ring 1.4s ease-out {0.9+arrow_delay:.2f}s backwards;'
                              f'transform-box:fill-box;transform-origin:center"')
    c += f'<circle cx="{w-30}" cy="26" r="12" fill="none" stroke="{color}" {ring}/>'
    # count-up via SMIL frames
    if STATIC:
        c += f'<text x="20" y="104" font-size="54" font-weight="700" fill="{FG}">{count}</text>'
    else:
        steps = 12
        t0 = 0.9 + arrow_delay
        for i in range(steps + 1):
            v = round(count * i / steps)
            last = i == steps
            begin = t0 + i * 0.06
            c += (f'<text x="20" y="104" font-size="54" font-weight="700" fill="{FG}" opacity="0">{v}'
                  f'<set attributeName="opacity" to="1" begin="{begin:.2f}s" fill="freeze"/>'
                  + ("" if last else f'<set attributeName="opacity" to="0" begin="{begin+0.06:.2f}s" fill="freeze"/>')
                  + '</text>')
    c += f'<text x="20" y="132" font-size="14" fill="{FG}">{esc(label)}</text>'
    c += f'<text x="20" y="154" font-size="11.5" fill="{DIM}">{esc(sub)}</text>'
    arr = "" if STATIC else 'style="animation:nudge 1.6s ease-in-out infinite"'
    c += f'<text x="{w-34}" y="164" font-size="20" fill="{color}" {arr}>→</text></g>'
    return wrap(w, h, c)


def repo(name, desc, tags, color, lang, delay=0):
    w, h = 410, 170
    c = f'<g {anim("rise", 0.2 + delay, 0.7)}>'
    c += f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    c += f'<text x="20" y="34" font-size="15" font-weight="700" fill="{CYAN}">{esc(name)}</text>'
    for i, line in enumerate(desc):
        c += f'<text x="20" y="{62 + i*19}" font-size="12" fill="{DIM}">{esc(line)}</text>'
    x = 20
    for t in tags:
        tw = len(t) * 7.2 + 18
        c += (f'<rect x="{x}" y="{h-50}" width="{tw}" height="22" rx="11" fill="{BG}" stroke="{LINE}"/>'
              f'<text x="{x+tw/2}" y="{h-35}" font-size="11" fill="{FG}" text-anchor="middle">{esc(t)}</text>')
        x += tw + 8
    c += f'<circle cx="26" cy="{h-18}" r="5" fill="{color}"/><text x="38" y="{h-14}" font-size="11" fill="{DIM}">{esc(lang)}</text>'
    c += '</g>'
    return wrap(w, h, c)


def stack():
    w, h = 830, 150
    b = window(w, h, "cat stack.txt")
    groups = [("lang", ["Python", "Java", "JavaScript", "TypeScript", "C++"], GREEN),
              ("web", ["React", "Node", "Django", "Flask", "FastAPI", "Tailwind"], CYAN),
              ("ml", ["PyTorch", "TensorFlow", "scikit-learn", "Pandas", "NumPy"], AMBER)]
    for gi, (k, items, col) in enumerate(groups):
        y = 64 + gi * 28
        b += text(28, y + 15, k, 12, DIM, delay=0.2 + gi * 0.2)
        x = 80
        for i, t in enumerate(items):
            tw = len(t) * 7.4 + 18
            b += (f'<g {anim("pop", 0.4 + gi*0.2 + i*0.07, 0.4)}><rect x="{x}" y="{y}" width="{tw}" height="22" rx="11" fill="{PANEL}" stroke="{col}" stroke-opacity=".5"/>'
                  f'<text x="{x+tw/2}" y="{y+15}" font-size="11" fill="{FG}" text-anchor="middle">{esc(t)}</text></g>')
            x += tw + 8
    return wrap(w, h, b)


def main():
    OUT.mkdir(exist_ok=True)
    days = load()
    cards = {
        "hero": hero(), "graph": graph(days), "activity": activity(days),
        "build": tile("BUILD", GREEN, 6, "projects shipped", "ML apps, Django, APIs"),
        "hackathons": tile("COMPETE", AMBER, 6, "hackathons", "1 win · 4 finalist · 1 top 20", 0.25),
        "learn": tile("LEARN", CYAN, 12, "certificates", "ML, NLP, design, cloud", 0.5),
        "balancepro": repo("BalancePro", ["Work-life balance prediction with a",
                           "Random Forest model, 91% accuracy,", "served through a Flask web app."],
                           ["Flask", "scikit-learn", "Python"], "#e34c26", "HTML"),
        "finlit": repo("FinLit_Entropy", ["AI-powered financial literacy platform:",
                       "expense tracking, investment picks and", "an AI chatbot. Entropy'24 top 20."],
                       ["Django", "PostgreSQL", "AI"], "#f1e05a", "JavaScript", 0.2),
        "stack": stack(),
    }
    for k, v in cards.items():
        (OUT / f"{k}.svg").write_text(v)
    print("rendered", ", ".join(cards), "STATIC" if STATIC else "")


if __name__ == "__main__":
    main()
