#!/usr/bin/env python3
"""
Hive stats generator for Amiere's GitHub profile.

Runs inside GitHub Actions (see .github/workflows/hive-stats.yml), pulls your
public GitHub stats through the GraphQL API, and draws two animated SVGs that
match the Traffic Hive theme:

  assets/hive-stats.svg     stat hexes + "traffic by language" lanes
  assets/hive-activity.svg  your contribution calendar as a glowing honeycomb

No third-party services, no pip installs: Python standard library only.
Local preview without a token:  python3 scripts/hive_stats.py --mock
"""
import json, math, os, random, sys, urllib.request
from datetime import date

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

FONT = "'SF Mono','JetBrains Mono','Cascadia Code',Consolas,'Liberation Mono',Menlo,monospace"
SANS = "-apple-system,'Segoe UI','Helvetica Neue',Arial,sans-serif"
GOLD = "#F9AB00"; HONEY = "#FFD166"; GREEN = "#34A853"
BG = "#0D1117"; PANEL = "#161B22"; LINE = "#30363D"; MUTED = "#8B949E"; TEXT = "#E6EDF3"; ROAD = "#1C2230"
LEVELS = [PANEL, "#5C4300", "#9A6F00", GOLD, HONEY]

QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    followers { totalCount }
    pullRequests { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}
"""


# ------------------------------------------------------------------ data
def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "hive-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors") or not (body.get("data") or {}).get("user"):
        sys.exit(f"GitHub API error: {body.get('errors') or body}")
    return body["data"]["user"]


def mock():
    random.seed(7)
    days, d0 = [], date.fromordinal(date.today().toordinal() - 370)
    weeks = []
    for w in range(53):
        wk = []
        for d in range(7):
            day = date.fromordinal(d0.toordinal() + w * 7 + d)
            busy = 0.35 + 0.5 * math.sin(w / 6) ** 2
            wk.append({"contributionCount": random.choice([0, 0, 1, 2, 3, 5, 8]) if random.random() < busy else 0,
                       "date": day.isoformat()})
        weeks.append({"contributionDays": wk})
    langs = [("Python", "#3572A5", 620000), ("Java", "#b07219", 240000), ("TypeScript", "#3178c6", 150000),
             ("HTML", "#e34c26", 90000), ("CSS", "#563d7c", 40000), ("Shell", "#89e051", 9000)]
    return {"login": "amiere", "followers": {"totalCount": 48}, "pullRequests": {"totalCount": 37},
            "repositories": {"totalCount": 21, "nodes": [
                {"stargazerCount": 12, "languages": {"edges": [{"size": s, "node": {"name": n, "color": c}} for n, c, s in langs]}}]},
            "contributionsCollection": {"totalCommitContributions": 642, "restrictedContributionsCount": 0,
                                        "contributionCalendar": {"totalContributions": 803, "weeks": weeks}}}


def summarize(u):
    repos = u["repositories"]["nodes"]
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or GOLD])[0] += e["size"]
    tot = sum(v[0] for v in langs.values()) or 1
    top = sorted(((n, v[0] / tot, v[1]) for n, v in langs.items()), key=lambda x: -x[1])[:5]
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    # streaks (today with 0 contributions doesn't break the current streak yet)
    cur = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            cur += 1
        elif i == 0:
            continue
        else:
            break
    best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        best = max(best, run)
    return {
        "login": u["login"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": u["repositories"]["totalCount"],
        "prs": u["pullRequests"]["totalCount"],
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "total": cc["contributionCalendar"]["totalContributions"],
        "weeks": cc["contributionCalendar"]["weeks"],
        "langs": top, "streak": cur, "best": best,
    }


# ------------------------------------------------------------------ svg helpers
def k(n):
    return f"{n/1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def hexpts(cx, cy, r):
    return " ".join(f"{cx + r*math.cos(math.radians(60*i+30)):.1f},{cy + r*math.sin(math.radians(60*i+30)):.1f}"
                    for i in range(6))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def frame(w, h, title, body, sweep=10):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<defs>
  <pattern id="honey" width="34.64" height="60" patternUnits="userSpaceOnUse">
    <path d="M17.32 0L34.64 10V30L17.32 40L0 30V10Z M17.32 40V60" fill="none" stroke="{GOLD}" stroke-width="1" stroke-opacity="0.07"/></pattern>
  <pattern id="honeyBright" width="34.64" height="60" patternUnits="userSpaceOnUse">
    <path d="M17.32 0L34.64 10V30L17.32 40L0 30V10Z M17.32 40V60" fill="none" stroke="{HONEY}" stroke-width="1.2" stroke-opacity="0.5"/></pattern>
  <radialGradient id="spot"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <mask id="sweep"><rect width="{w}" height="{h}" fill="#000"/>
    <circle cy="{h*0.5:.0f}" r="{max(170, h*0.6):.0f}" fill="url(#spot)">
      <animate attributeName="cx" values="-300;{w+300}" dur="{sweep}s" repeatCount="indefinite"/></circle></mask>
</defs>
<rect width="{w}" height="{h}" rx="18" fill="{BG}"/>
<rect width="{w}" height="{h}" rx="18" fill="url(#honey)"/>
<rect width="{w}" height="{h}" rx="18" fill="url(#honeyBright)" mask="url(#sweep)"/>
<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="18" fill="none" stroke="{LINE}"/>
{body}</svg>
'''


def heading(text, sub):
    return (f'<polygon points="{hexpts(54,46,11)}" fill="{GOLD}" filter="url(#glow)"/>'
            f'<text x="76" y="53" font-family="{FONT}" font-size="15" font-weight="700" fill="{GOLD}" letter-spacing="2">{text}</text>'
            f'<text x="76" y="74" font-family="{FONT}" font-size="12" fill="{MUTED}">{esc(sub)}</text>\n')


# ------------------------------------------------------------------ stats card
def stats_svg(s):
    W, H = 1200, 330
    body = heading("HIVE ACTIVITY", f"@{s['login']} · refreshed {date.today():%b %d, %Y}")
    cells = [("CONTRIBUTIONS", s["total"], "this year"), ("COMMITS", s["commits"], "this year"),
             ("PULL REQUESTS", s["prs"], "all time"), ("STARS", s["stars"], f"across {s['repos']} repos")]
    for i, (lab, val, sub) in enumerate(cells):
        cx, cy, r = 118 + i * 140, 200, 64
        b = 0.15 + i * 0.18
        body += f'''<g opacity="0">
  <animate attributeName="opacity" values="0;1" dur="0.6s" begin="{b:.2f}s" fill="freeze"/>
  <animateTransform attributeName="transform" type="translate" values="0 16;0 0" dur="0.6s" begin="{b:.2f}s" fill="freeze"/>
  <g transform="translate({cx},{cy})"><polygon points="{hexpts(0,0,r)}" fill="none" stroke="{GOLD}" stroke-width="1.5" opacity="0">
    <animate attributeName="opacity" values="0.6;0" dur="3s" begin="{b+0.8:.2f}s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="scale" values="1;1.25" dur="3s" begin="{b+0.8:.2f}s" repeatCount="indefinite"/>
  </polygon></g>
  <polygon points="{hexpts(cx,cy,r)}" fill="{PANEL}" stroke="{GOLD}" stroke-opacity="0.7" stroke-width="2"/>
  <text x="{cx}" y="{cy+8}" text-anchor="middle" font-family="{SANS}" font-size="30" font-weight="800" fill="{TEXT}">{k(val)}</text>
  <text x="{cx}" y="{cy-22}" text-anchor="middle" font-family="{FONT}" font-size="9.5" fill="{GOLD}" letter-spacing="1">{lab}</text>
  <text x="{cx}" y="{cy+30}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{MUTED}">{esc(sub)}</text>
</g>
'''
    # language lanes
    lx, lw, ly = 690, 440, 112
    body += (f'<text x="{lx}" y="{ly-12}" font-family="{FONT}" font-size="11" fill="{MUTED}" letter-spacing="1">'
             f'TRAFFIC BY LANGUAGE</text>\n')
    langs = s["langs"] or [("No public code yet", 1.0, GOLD)]
    top_share = langs[0][1]
    for i, (name, share, color) in enumerate(langs):
        y = ly + 14 + i * 40
        bar = max(14, lw * share / top_share)
        b = 0.4 + i * 0.15
        pid = f"lane{i}"
        body += f'''<g font-family="{FONT}">
  <text x="{lx}" y="{y}" font-size="12" fill="{TEXT}">{esc(name)}</text>
  <text x="{lx+lw}" y="{y}" text-anchor="end" font-size="12" fill="{MUTED}">{share*100:.1f}%</text>
  <rect x="{lx}" y="{y+8}" width="{lw}" height="12" rx="6" fill="{ROAD}"/>
  <rect x="{lx}" y="{y+8}" height="12" rx="6" fill="{GOLD}" fill-opacity="0.85" width="0">
    <animate attributeName="width" values="0;{bar:.1f}" dur="1.1s" begin="{b:.2f}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect>
  <path id="{pid}" d="M{lx+6} {y+14} H{lx+bar-6:.1f}" fill="none"/>
  <g filter="url(#glow)"><circle r="3.5" fill="{color}" stroke="{BG}" stroke-width="1"/>
    <animateMotion dur="{2.2 + (1 - share) * 3:.1f}s" begin="{b+1.1:.2f}s" repeatCount="indefinite"><mpath xlink:href="#{pid}"/></animateMotion></g>
</g>
'''
    return frame(W, H, f"Hive activity for @{s['login']}", body)


# ------------------------------------------------------------------ contribution honeycomb
def activity_svg(s):
    W, H = 1200, 300
    weeks = s["weeks"][-53:]
    counts = sorted(d["contributionCount"] for w in weeks for d in w["contributionDays"] if d["contributionCount"] > 0)
    q = [counts[int(len(counts) * f)] if counts else 1 for f in (0.25, 0.5, 0.75)]

    def level(c):
        if c <= 0: return 0
        return 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4

    r = 11.4
    dx, dy = math.sqrt(3) * r, 1.5 * r
    gw = dx * len(weeks) + dx / 2
    x0 = (W - gw) / 2 + dx / 2
    y0 = 114
    base, lit = "", ""
    for wi, w in enumerate(weeks):
        for di, d in enumerate(w["contributionDays"]):
            cx = x0 + wi * dx + (dx / 2 if di % 2 else 0)
            cy = y0 + di * dy
            lv = level(d["contributionCount"])
            pts = hexpts(cx, cy, r - 1.1)
            b = 0.2 + wi * 0.025
            tip = f'{d["contributionCount"]} on {d["date"]}'
            if lv == 0:
                base += f'<polygon points="{pts}" fill="#1A2029" stroke="#2A313B" stroke-width="0.8"><title>{tip}</title></polygon>\n'
            else:
                base += (f'<polygon points="{pts}" fill="{LEVELS[lv]}" opacity="0"><title>{tip}</title>'
                         f'<animate attributeName="opacity" values="0;1" dur="0.4s" begin="{b:.2f}s" fill="freeze"/></polygon>\n')
                if lv >= 3:
                    lit += f'<polygon points="{pts}" fill="{HONEY}"/>\n'
    # a bee hops between your busiest days
    hot = [(x0 + wi * dx + (dx / 2 if di % 2 else 0), y0 + di * dy)
           for wi, w in enumerate(weeks) for di, d in enumerate(w["contributionDays"]) if level(d["contributionCount"]) == 4]
    random.seed(len(hot))
    path = random.sample(hot, min(7, len(hot))) if hot else []
    path.sort()
    bee = ""
    if len(path) >= 2:
        pts = ";".join(f"{x:.1f} {y:.1f}" for x, y in path + [path[0]])
        bee = f'''<g><animateTransform attributeName="transform" type="translate" values="{pts}" dur="{len(path)*1.6:.1f}s" begin="2s" repeatCount="indefinite" calcMode="spline" keySplines="{";".join(["0.4 0 0.2 1"]*len(path))}"/>
  <circle r="14" fill="{GOLD}" opacity="0.25" filter="url(#glow)"/>
  <polygon points="{hexpts(0,0,5)}" fill="{BG}" stroke="{HONEY}" stroke-width="2"/></g>
'''
    body = heading("THE HONEYCOMB", "every cell is a day of building · the brighter, the busier")
    body += f'<g>{base}</g>\n'
    body += (f'<mask id="combsweep"><rect width="{W}" height="{H}" fill="#000"/><rect x="-220" y="0" width="220" height="{H}" fill="url(#spot)">'
             f'<animate attributeName="x" values="-260;{W+40}" dur="5s" begin="2s" repeatCount="indefinite"/></rect></mask>\n'
             f'<g mask="url(#combsweep)" filter="url(#glow)" opacity="0.9">{lit}</g>\n')
    body += bee
    # footer numbers
    stats = [(k(s["total"]), "contributions in the last year"), (str(s["streak"]), "day current streak"),
             (str(s["best"]), "day longest streak")]
    for i, (v, lab) in enumerate(stats):
        x = 72 + i * 300
        body += (f'<text x="{x}" y="262" font-family="{SANS}" font-size="22" font-weight="800" fill="{GOLD if i == 1 else TEXT}">{v}'
                 f'<tspan font-family="{FONT}" font-size="12" font-weight="400" fill="{MUTED}" dx="8">{lab}</tspan></text>\n')
    lx = W - 72 - 5 * 20
    body += f'<text x="{lx-10}" y="258" text-anchor="end" font-family="{FONT}" font-size="11" fill="{MUTED}">less</text>'
    for i, c in enumerate(LEVELS):
        body += f'<polygon points="{hexpts(lx + i*20 + 8, 254, 7)}" fill="{c}" stroke="{LINE if i == 0 else c}" stroke-width="0.8"/>'
    body += f'<text x="{lx + 5*20 + 4}" y="258" font-family="{FONT}" font-size="11" fill="{MUTED}">more</text>\n'
    return frame(W, H, f"Contribution honeycomb for @{s['login']}", body, sweep=12)


def main():
    if "--mock" in sys.argv:
        u = mock()
    else:
        login = os.environ.get("HIVE_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER")
        token = os.environ.get("HIVE_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not login or not token:
            sys.exit("Set GITHUB_REPOSITORY_OWNER/HIVE_USER and GITHUB_TOKEN/HIVE_TOKEN, or run with --mock")
        u = fetch(login, token)
    s = summarize(u)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "hive-stats.svg"), "w") as f:
        f.write(stats_svg(s))
    with open(os.path.join(OUT, "hive-activity.svg"), "w") as f:
        f.write(activity_svg(s))
    print(f"wrote hive-stats.svg and hive-activity.svg for @{s['login']}: "
          f"{s['total']} contributions, streak {s['streak']}, langs {[l[0] for l in s['langs']]}")


if __name__ == "__main__":
    main()
