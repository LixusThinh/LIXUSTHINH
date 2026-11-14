#!/usr/bin/env python3
"""Draws the two terminal-style cards in the profile README.

    generated/banner.svg  -- ASCII-art name, `whoami` output, a ticker of repos
    generated/stats.svg   -- GitHub numbers and languages by bytes of code

Standard library only. Needs GITHUB_TOKEN in the environment (the Actions
token is enough). Edit PROFILE below to change what the banner says.
"""
import json
import os
import urllib.request
from html import escape
from pathlib import Path

USER = "LixusThinh"
LOGO = "LIXUS THINH"
TITLE = "LixusThinh : README.EXE"
STATS_TITLE = "LixusThinh : STATS.EXE"

# (tag, colour class, words). A "|" word is drawn dimmed, as a separator.
PROFILE = [
    ("[study]", "h0", "3rd-year IT student | Machine Learning & Applications | HCMC"),
    ("[research]", "h1", "Deep RL for adaptive bitrate streaming: DQN vs BOLA, content-aware rewards"),
    ("[build]", "h2", "Full-stack | Next.js | NestJS | FastAPI | PostgreSQL | Flutter"),
    ("[code]", "h7", "Python | TypeScript | C++ | Dart | C#"),
    ("[now]", "h5", "RAG for Vietnamese, semi-supervised clustering, graph neural networks"),
]
# Repos left out of the ticker (besides forks, private repos and this one).
SKIP_REPOS = {USER.lower(), "lixus-system-lead"}

OUT = Path(__file__).resolve().parent / "generated"
W = 800                 # card width
CW = 8.4                # width of one monospace cell at 14px
LH = 19                 # line height
X0 = 22.0               # left margin

# ---------------------------------------------------------------- GitHub API

TOKEN = os.environ.get("GITHUB_TOKEN", "")


def api(url, body=None):
    req = urllib.request.Request(
        url if url.startswith("http") else "https://api.github.com" + url,
        data=json.dumps(body).encode() if body else None,
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "profile-stats-script",
                 **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch():
    user = api(f"/users/{USER}")
    repos, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"] and not r["private"]]
    langs = {}
    for r in own:
        for name, size in api(r["languages_url"]).items():
            langs[name] = langs.get(name, 0) + size
    contrib = None
    if TOKEN:
        q = ("query($u:String!){user(login:$u){contributionsCollection"
             "{contributionCalendar{totalContributions}}}}")
        try:
            data = api("https://api.github.com/graphql", {"query": q, "variables": {"u": USER}})
            contrib = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        except Exception as e:  # keep drawing without it
            print("contributions:", e)
    # most stars first, then most recently pushed
    ticker = sorted((r for r in own if r["name"].lower() not in SKIP_REPOS),
                    key=lambda r: r["pushed_at"] or "", reverse=True)
    ticker.sort(key=lambda r: -r["stargazers_count"])
    return {
        "stars": sum(r["stargazers_count"] for r in own),
        "forks": sum(r["forks_count"] for r in own),
        "repos": user["public_repos"],
        "followers": user["followers"],
        "contrib": contrib,
        "langs": langs,
        "ticker": [(r["name"], r["stargazers_count"], r["language"]) for r in ticker[:12]],
    }

# ------------------------------------------------------------------- drawing

STYLE = """
text { font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace; font-size: 14px; fill: #e9e7e1; }
.screen { fill: #16161a; stroke: #34343b; }
.bar { fill: #232329; }
.dim { fill: #85847c; }
.sec { fill: #c2c0b6; }
.b { font-weight: 700; }
.other { fill: #6c6b66; }
.h0 { fill: #6eaaf2; } .h1 { fill: #f28c5e; } .h2 { fill: #3fd09c; } .h3 { fill: #eab63e; } .h4 { fill: #ef86ae; } .h5 { fill: #58c458; } .h6 { fill: #ada3f3; } .h7 { fill: #f28585; }
.s0 { fill: #3987e5; } .s1 { fill: #d95926; } .s2 { fill: #199e70; } .s3 { fill: #c98500; } .s4 { fill: #d55181; } .s5 { fill: #2f9e2f; } .s6 { fill: #9085e9; } .s7 { fill: #e66767; }
.t { animation: on .01s linear backwards; }
.fade { animation: on .5s ease-out backwards; }
@keyframes on { from { opacity: 0; } }
@keyframes off { to { opacity: 0; } }
.cur { fill: #e9e7e1; animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
.logo g { animation: hue 8s linear infinite; }
.logo text { fill: inherit; }
@keyframes hue { 0% { fill: #6eaaf2; } 12.5% { fill: #f28c5e; } 25% { fill: #3fd09c; } 37.5% { fill: #eab63e; } 50% { fill: #ef86ae; } 62.5% { fill: #58c458; } 75% { fill: #ada3f3; } 87.5% { fill: #f28585; } 100% { fill: #6eaaf2; } }
@media (prefers-reduced-motion: reduce) {
* { animation: none !important; }
.typing { display: none; }
}
"""

FONT = {  # 5x7 glyphs
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#..##", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    " ": ["....."] * 7,
}


HUES = ["#6eaaf2", "#f28c5e", "#3fd09c", "#eab63e", "#ef86ae", "#58c458", "#ada3f3", "#f28585"]


def f(v):
    return f"{v:.1f}"


def txt(col_x, y, s, cls="", extra=""):
    """One run of text, stretched to exactly len(s) cells so columns line up."""
    tl = f' textLength="{f(len(s) * CW)}"' if len(s) > 1 else ""
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{f(col_x)}" y="{y}"{c}{tl}{extra}>{escape(s)}</text>'


def frame(h, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{{label}}">\n'
            f"<style>{STYLE}{{extra_style}}</style>\n"
            f'<defs><clipPath id="window"><rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="9"/></clipPath>'
            f'<clipPath id="inside"><rect x="{X0}" y="30" width="{W-2*X0}" height="{h-30}"/></clipPath>'
            '<pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".16"/></pattern>'
            '<filter id="glow" x="-5%" y="-40%" width="110%" height="180%"><feGaussianBlur stdDeviation="2" result="blur"/>'
            '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>\n'
            f'<rect class="screen" x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="9"/>\n'
            f'<g clip-path="url(#window)"><rect class="bar" width="{W}" height="30"/></g>\n'
            '<circle cx="20" cy="15" r="5.5" fill="#e66767"/><circle cx="38" cy="15" r="5.5" fill="#c98500"/><circle cx="56" cy="15" r="5.5" fill="#199e70"/>\n'
            f'<text class="dim" x="{W/2}" y="20" text-anchor="middle">{escape(title)}</text>\n')


def close(h):
    return f'<rect x="0" y="30" width="{W}" height="{h-30}" fill="url(#scan)" clip-path="url(#window)"/>\n</svg>\n'


def prompt(y):
    return txt(X0, y, "C:\\>", "h2 b")


def logo(y_top):
    cells = len(LOGO) * 6 - 1
    scale = min(1.3, (W - 2 * X0) / (cells * CW))
    out = [f'<g class="logo" filter="url(#glow)" transform="translate({f(X0)} {f(y_top)}) scale({scale:.3f})">']
    for i, ch in enumerate(LOGO.upper()):
        if ch == " ":
            continue
        parts = []
        for row, bits in enumerate(FONT[ch]):
            c = 0
            while c < 5:
                if bits[c] == "#":
                    run = c
                    while run < 5 and bits[run] == "#":
                        run += 1
                    parts.append(txt((i * 6 + c) * CW, 11 + row * 10, "#" * (run - c)))
                    c = run
                else:
                    c += 1
        # static colour for reduced motion; the hue animation overrides it
        out.append(f'<g fill="{HUES[i % 8]}" style="animation-delay: -{i}s">' + "".join(parts) + "</g>")
    out.append("</g>")
    return "\n".join(out), 70 * scale


def banner(data):
    lines, extra = [], []
    body_h = 0
    art, art_h = logo(48)
    lines.append(art)
    y = int(48 + art_h + 32)                     # `whoami` line
    lines.append(prompt(y))
    t = 0.9
    for k, ch in enumerate("whoami"):
        lines.append(txt(X0 + (5 + k) * CW, y, ch, "t", f' style="animation-delay: {t + k * 0.11:.2f}s"'))
    lines.append(f'<g class="typing" style="animation: off .01s linear 2.01s forwards"><g style="animation: type 0.66s steps(6) {t:.2f}s forwards">'
                 f'<rect class="cur" x="{f(X0 + 5 * CW)}" y="{y-13}" width="7.4" height="16"/></g></g>')
    extra.append(f"@keyframes type {{ to {{ transform: translateX({f(6 * CW)}); }} }}")
    t = 2.11
    for tag, cls, words in PROFILE:
        y += LH
        lines.append(txt(X0 + 2 * CW, y, tag, f"t b {cls}", f' style="animation-delay: {t:.2f}s"'))
        col = 14
        for w in words.split():
            t += 0.035
            lines.append(txt(X0 + col * CW, y, w, "t dim" if w == "|" else "t", f' style="animation-delay: {t:.2f}s"'))
            col += len(w) + 1
        if col > 91:
            raise SystemExit(f"line too long for the card: {tag} {words}")
        t += 0.1
    y += LH
    t += 0.3
    lines.append(f'<g class="t" style="animation-delay: {t:.2f}s">{prompt(y)}'
                 f'<rect class="cur" x="{f(X0 + 5 * CW)}" y="{y-13}" width="7.4" height="16"/></g>')
    # ticker of repos, drawn twice so the loop is seamless
    y += 38
    tape, col = [], 0
    for rep in range(2):
        for name, stars, lang in data["ticker"]:
            tape.append(txt(X0 + col * CW, y, name, "sec")); col += len(name) + 1
            s, c = (f"*{stars}", "h3 b") if stars else (f"<{lang}>" if lang else "", "h6")
            if s:
                tape.append(txt(X0 + col * CW, y, s, c)); col += len(s) + 1
            tape.append(txt(X0 + col * CW, y, "+++", "dim")); col += 4
        if rep == 0:
            loop = col * CW
    secs = max(20, round(loop / 27))
    extra.append(f"@keyframes tape {{ to {{ transform: translateX(-{f(loop)}px); }} }}")
    lines.append(f'<g clip-path="url(#inside)"><g style="animation: tape {secs}s linear infinite">\n' + "\n".join(tape) + "\n</g></g>")
    h = y + 19
    label = f"{LOGO.title()}. " + " ".join(f"{tag.strip('[]')}: {w.replace(' | ', ', ')}." for tag, _, w in PROFILE)
    head = frame(h, TITLE).replace("{label}", escape(label, quote=True)).replace("{extra_style}", "\n".join(extra) + "\n")
    return head + "\n".join(lines) + "\n" + close(h)


def lang_classes(names):
    """Keep each language's colour stable between runs."""
    path = OUT / "languages.json"
    try:
        known = json.loads(path.read_text())
    except (OSError, ValueError):
        known = {}
    known = {k: v for k, v in known.items() if k in names}
    free = [f"s{i}" for i in range(8) if f"s{i}" not in known.values()]
    for n in names:
        if n not in known:
            known[n] = free.pop(0)
    path.write_text(json.dumps(known, indent=1) + "\n")
    return known


def stats(data):
    rows = [("Stars earned", data["stars"]), ("Forks of my repositories", data["forks"]),
            ("Public repositories", data["repos"]), ("Followers", data["followers"])]
    if data["contrib"] is not None:
        rows.append(("Contributions in the last year", data["contrib"]))
    total = sum(data["langs"].values()) or 1
    ranked = sorted(data["langs"].items(), key=lambda kv: -kv[1])
    top, rest = ranked[:7], sum(v for _, v in ranked[7:])
    cls = lang_classes([n for n, _ in top])
    langs = [(n, v / total * 100, cls[n]) for n, v in top]
    if rest:
        langs.append(("Other", rest / total * 100, "other"))

    out, y = [], 58
    out.append(prompt(y) + txt(X0 + 5 * CW, y, "stats"))
    y = 96
    L, R = 2, 44                                      # left / right column, in cells

    def words(col, yy, s, c, extra=""):
        parts = []
        for w in s.split():
            parts.append(txt(X0 + col * CW, yy, w, c, extra)); col += len(w) + 1
        return "".join(parts)
    out.append(words(L, y, "-- overview --", "h0 b"))
    out.append(words(R, y, "-- languages, by bytes of code --", "h0 b"))
    val_end = 40
    for i, (name, v) in enumerate(rows):
        yy = y + LH * (i + 1)
        s = str(v)
        dots = val_end - len(s) - (L + len(name) + 1) - 1
        out.append(f'<g class="fade" style="animation-delay: {i * 0.15:.2f}s">' + words(L, yy, name, "sec")
                   + txt(X0 + (L + len(name) + 1) * CW, yy, "." * dots, "dim")
                   + txt(X0 + (val_end - len(s)) * CW, yy, s, "b") + "</g>")
    slot, maxp = 24, max((p for _, p, _ in langs), default=1)
    for i, (name, p, c) in enumerate(langs):
        yy = y + LH * (i + 1)
        n = max(1, round(p / maxp * slot))
        pct = f"{p:.1f}%"
        bar = X0 + (R + 13) * CW
        out.append(f'<g class="fade" style="animation-delay: {i * 0.1:.2f}s">' + txt(X0 + R * CW, yy, name, "sec")
                   + txt(bar, yy, "#" * n, c)
                   + (txt(bar + n * CW, yy, "." * (slot - n), "dim") if n < slot else "")
                   + txt(X0 + (R + 13 + slot + 8 - len(pct)) * CW, yy, pct, "b") + "</g>")
    h = y + LH * (max(len(rows), len(langs)) + 1)
    label = ("; ".join(f"{n}: {v}" for n, v in rows) + ". Languages: "
             + "; ".join(f"{n} {p:.1f}%" for n, p, _ in langs))
    head = frame(h, STATS_TITLE).replace("{label}", escape(label, quote=True)).replace("{extra_style}", "")
    return head + "\n".join(out) + "\n" + close(h)


def main():
    OUT.mkdir(exist_ok=True)
    data = fetch()
    (OUT / "banner.svg").write_text(banner(data), encoding="utf-8")
    (OUT / "stats.svg").write_text(stats(data), encoding="utf-8")
    print(json.dumps({k: v for k, v in data.items() if k != "langs"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
