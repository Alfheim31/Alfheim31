import math, os

OUT = "profile/assets"
os.makedirs(OUT, exist_ok=True)

FONT = "'SF Mono','JetBrains Mono','Cascadia Code',Consolas,'Liberation Mono',Menlo,monospace"
SANS = "-apple-system,'Segoe UI','Helvetica Neue',Arial,sans-serif"
GOLD = "#F9AB00"; HONEY = "#FFD166"; RED = "#EA4335"; BLUE = "#4285F4"; GREEN = "#34A853"
DASH = ' stroke-dasharray="4 4"'
BG = "#0D1117"; PANEL = "#161B22"; LINE = "#30363D"; MUTED = "#8B949E"; TEXT = "#E6EDF3"; ROAD = "#1C2230"


def hexpts(cx, cy, r):
    return " ".join(
        f"{cx + r*math.cos(math.radians(60*i+30)):.1f},{cy + r*math.sin(math.radians(60*i+30)):.1f}"
        for i in range(6))


def svg_open(w, h, title):
    title = title.replace("&", "&amp;")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">\n<title>{title}</title>\n')


def common_defs():
    return f'''<defs>
  <pattern id="honey" width="34.64" height="60" patternUnits="userSpaceOnUse">
    <path d="M17.32 0L34.64 10V30L17.32 40L0 30V10Z M17.32 40V60" fill="none" stroke="{GOLD}" stroke-width="1" stroke-opacity="0.07"/>
  </pattern>
  <pattern id="honeyBright" width="34.64" height="60" patternUnits="userSpaceOnUse">
    <path d="M17.32 0L34.64 10V30L17.32 40L0 30V10Z M17.32 40V60" fill="none" stroke="{HONEY}" stroke-width="1.2" stroke-opacity="0.55"/>
  </pattern>
  <radialGradient id="spot"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="6"/>
  </filter>
</defs>
'''


def hive_bg(w, h, sweep_dur=9):
    """Dark card + faint honeycomb + a light sweep that makes the hive shimmer."""
    return f'''<rect width="{w}" height="{h}" rx="18" fill="{BG}"/>
<rect width="{w}" height="{h}" rx="18" fill="url(#honey)"/>
<mask id="sweep"><rect width="{w}" height="{h}" fill="#000"/>
  <circle cy="{h*0.45:.0f}" r="{max(160, h*0.6):.0f}" fill="url(#spot)">
    <animate attributeName="cx" values="-300;{w+300}" dur="{sweep_dur}s" repeatCount="indefinite"/>
  </circle>
</mask>
<rect width="{w}" height="{h}" rx="18" fill="url(#honeyBright)" mask="url(#sweep)"/>
<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="18" fill="none" stroke="{LINE}"/>
'''


def car(path_id, dur, begin, color, r=4, reverse=False):
    rev = ' keyPoints="1;0" keyTimes="0;1" calcMode="linear"' if reverse else ''
    return f'''<g filter="url(#glow)"><circle r="{r}" fill="{color}"/><circle r="{r*2.2}" fill="{color}" opacity="0.18"/>
  <animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite"{rev}><mpath xlink:href="#{path_id}"/></animateMotion></g>
'''


def pulse_hex(cx, cy, r, color=GOLD, dur=2.4, begin=0, label=None):
    s = f'''<g transform="translate({cx},{cy})">
  <polygon points="{hexpts(0,0,r)}" fill="none" stroke="{color}" stroke-width="2" opacity="0">
    <animateTransform attributeName="transform" type="scale" values="1;2.4" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.8;0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
  </polygon>
  <polygon points="{hexpts(0,0,r)}" fill="{BG}" stroke="{color}" stroke-width="2" filter="url(#glow)"/>
  <polygon points="{hexpts(0,0,r*0.45)}" fill="{color}">
    <animate attributeName="opacity" values="1;0.35;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
  </polygon>
'''
    if label:
        s += f'  <text y="{r+18}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">{label}</text>\n'
    return s + "</g>\n"


# ---------------------------------------------------------------- HEADER
# Rotating taglines in the header: each one types out, holds, erases, then the next.
TAGLINES = [
    "building a hive mind of code, design & community",
    "making tech reachable for every community",
    "turning solo builders into a swarm",
]


def typed_lines(lines, x0=62, y=201, size=20, seg=5.2, delay=1.1):
    ch = size * 0.6                       # monospace advance; textLength pins it exactly
    total = seg * len(lines)
    out = ""
    cur_t, cur_x = [0.0], [x0]
    for i, ln in enumerate(lines):
        w = len(ln) * ch
        t0 = i * seg
        keys = [(t0, 0), (t0 + 2.2, w), (t0 + 4.2, w), (t0 + 4.8, 0)]
        kt, vv = ([0.0], [0.0]) if t0 > 0 else ([], [])
        for t, v in keys:
            kt.append(t / total); vv.append(v)
        kt.append(1.0); vv.append(0)
        out += (f'  <clipPath id="tc{i}"><rect x="{x0-2}" y="{y-23}" height="32" width="0">'
                f'<animate attributeName="width" values="{";".join(f"{v:.1f}" for v in vv)}" '
                f'keyTimes="{";".join(f"{t:.4f}" for t in kt)}" dur="{total:.1f}s" begin="{delay}s" repeatCount="indefinite"/>'
                f'</rect></clipPath>\n'
                f'  <text x="{x0}" y="{y}" font-size="{size}" fill="{GOLD}" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs" '
                f'clip-path="url(#tc{i})">{ln.replace("&", "&amp;")}</text>\n')
        for t, v in keys[1:]:
            cur_t.append(t / total); cur_x.append(x0 + v + 3)
        cur_t.append((t0 + seg) / total if i < len(lines) - 1 else 1.0); cur_x.append(x0)
    out += (f'  <rect x="{x0}" y="{y-17}" width="11" height="22" fill="{GOLD}">'
            f'<animate attributeName="x" values="{";".join(f"{v:.1f}" for v in cur_x)}" '
            f'keyTimes="{";".join(f"{t:.4f}" for t in cur_t)}" dur="{total:.1f}s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="0.9s" repeatCount="indefinite"/></rect>\n')
    return out


def header():
    W, H = 1200, 360
    def curve(dy):
        return f"M -60 {300+dy} C 200 {250+dy}, 400 {330+dy}, 640 {285+dy} S 1020 {215+dy}, 1260 {255+dy}"
    s = svg_open(W, H, "Hi, I'm Amiere. " + ". ".join(TAGLINES)) + common_defs()
    s += hive_bg(W, H)
    s += "<defs>" + "".join(f'<path id="lane{i}" d="{curve(dy)}"/>' for i, dy in enumerate([-18, 0, 18])) + "</defs>\n"
    # road
    s += f'<path d="{curve(0)}" fill="none" stroke="{LINE}" stroke-width="68" stroke-linecap="round"/>\n'
    s += f'<path d="{curve(0)}" fill="none" stroke="{ROAD}" stroke-width="64" stroke-linecap="round"/>\n'
    for dy in (-9, 9):
        s += (f'<path d="{curve(dy)}" fill="none" stroke="{GOLD}" stroke-opacity="0.35" stroke-width="2" stroke-dasharray="14 12">'
              f'<animate attributeName="stroke-dashoffset" values="0;-52" dur="1.1s" repeatCount="indefinite"/></path>\n')
    # cars
    cars = [(0, 7, 0, HONEY), (0, 7, -2.3, GOLD), (0, 7, -4.7, HONEY),
            (1, 5.5, -1, GOLD), (1, 5.5, -3.6, BLUE), (1, 5.5, -2.2, HONEY),
            (2, 8, 0, GOLD, True), (2, 8, -2.7, HONEY, True), (2, 8, -5.3, BLUE, True)]
    for c in cars:
        s += car(f"lane{c[0]}", c[1], c[2], c[3], reverse=len(c) > 4)
    # hive agent network (top right)
    nodes = [(760, 120), (880, 72), (1010, 118), (905, 170), (1110, 74)]
    links = [(0, 1), (1, 2), (0, 3), (3, 2), (2, 4), (1, 4)]
    for k, (a, b) in enumerate(links):
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        s += (f'<path id="link{k}" d="M{x1} {y1} L{x2} {y2}" stroke="{GOLD}" stroke-opacity="0.4" stroke-width="1.5" stroke-dasharray="4 6">'
              f'<animate attributeName="stroke-dashoffset" values="0;-20" dur="1s" repeatCount="indefinite"/></path>\n')
        s += (f'<circle r="2.5" fill="{HONEY}" filter="url(#glow)"><animateMotion dur="{1.6+0.3*k:.1f}s" begin="{-0.4*k:.1f}s" '
              f'repeatCount="indefinite"><mpath xlink:href="#link{k}"/></animateMotion></circle>\n')
    # signal beams from agents down to the road
    for k, (x, y) in enumerate([nodes[0], nodes[3], nodes[2]]):
        s += (f'<line x1="{x}" y1="{y+14}" x2="{x+10}" y2="{y+95}" stroke="{GOLD}" stroke-width="1.2" stroke-dasharray="3 5" opacity="0.5">'
              f'<animate attributeName="opacity" values="0;0.7;0" dur="2.4s" begin="{0.8*k}s" repeatCount="indefinite"/></line>\n')
    for k, (x, y) in enumerate(nodes):
        s += pulse_hex(x, y, 13, dur=2.4, begin=0.45*k)
    # text block
    s += f'''<g font-family="{FONT}">
  <text x="64" y="86" font-size="15" fill="{MUTED}" opacity="0">~/amiere $ <tspan fill="{GREEN}">whoami</tspan>
    <animate attributeName="opacity" values="0;1" dur="0.4s" begin="0.1s" fill="freeze"/></text>
  <g opacity="0">
    <animate attributeName="opacity" values="0;1" dur="0.7s" begin="0.4s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" values="0 14;0 0" dur="0.7s" begin="0.4s" fill="freeze"/>
    <text x="60" y="158" font-family="{SANS}" font-size="66" font-weight="800" fill="{TEXT}" letter-spacing="-1">Hi, I'm Amiere</text>
    <polygon points="{hexpts(548,136,14)}" fill="{GOLD}" filter="url(#glow)">
      <animateTransform attributeName="transform" type="rotate" values="0 548 136;60 548 136;60 548 136" keyTimes="0;0.25;1" dur="3s" repeatCount="indefinite"/>
    </polygon>
  </g>
{typed_lines(TAGLINES)}  <text x="64" y="238" font-size="14" fill="{MUTED}" opacity="0">CS @ PLM  ·  GDG on Campus PLM  ·  design + community + code
    <animate attributeName="opacity" values="0;1" dur="0.8s" begin="3.6s" fill="freeze"/></text>
</g>
'''
    return s + "</svg>\n"


# ---------------------------------------------------------------- TRAFFIC HIVE SHOWCASE
def showcase():
    W, H = 1200, 540
    s = svg_open(W, H, "Traffic Hive — selfish routing versus cooperative hive routing") + common_defs()
    s += hive_bg(W, H, sweep_dur=11)
    s += f'''<g font-family="{FONT}">
  <polygon points="{hexpts(58,50,13)}" fill="{GOLD}" filter="url(#glow)"/>
  <text x="84" y="58" font-family="{SANS}" font-size="26" font-weight="800" fill="{TEXT}">TRAFFIC <tspan fill="{GOLD}">HIVE</tspan></text>
  <text x="44" y="92" font-size="15" fill="{MUTED}">What if every car on EDSA cooperated instead of competing?</text>
  <text x="1156" y="58" text-anchor="end" font-size="12" fill="{MUTED}">BSCS THESIS · PLM</text>
</g>
'''
    def panel(px, mode):
        hive = mode == "hive"
        col = GOLD if hive else RED
        ox, dx, cy = px + 60, px + 490, 270
        routes = {
            "t": f"M{ox} {cy} C {ox+110} {cy-105}, {dx-110} {cy-105}, {dx} {cy}",
            "m": f"M{ox} {cy} L{dx} {cy}",
            "b": f"M{ox} {cy} C {ox+110} {cy+105}, {dx-110} {cy+105}, {dx} {cy}",
        }
        g = f'<rect x="{px}" y="118" width="550" height="300" rx="14" fill="{PANEL}" fill-opacity="0.85" stroke="{LINE}"/>\n'
        title = "HIVE ROUTING · HPDM" if hive else "SELFISH ROUTING"
        sub = "agents share the load across every route" if hive else "everyone piles onto the 'fastest' road"
        g += (f'<text x="{px+22}" y="146" font-family="{FONT}" font-size="14" font-weight="700" fill="{col}">{title}</text>\n'
              f'<text x="{px+22}" y="166" font-family="{FONT}" font-size="12" fill="{MUTED}">{sub}</text>\n')
        g += "<defs>" + "".join(f'<path id="{mode}{k}" d="{d}"/>' for k, d in routes.items()) + "</defs>\n"
        for k, d in routes.items():
            g += f'<path d="{d}" fill="none" stroke="{ROAD}" stroke-width="14" stroke-linecap="round"/>\n'
            if hive:
                g += (f'<path d="{d}" fill="none" stroke="{GOLD}" stroke-width="2" stroke-opacity="0.55" stroke-dasharray="10 8">'
                      f'<animate attributeName="stroke-dashoffset" values="0;-36" dur="0.9s" repeatCount="indefinite"/></path>\n')
            elif k == "m":
                g += (f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="14" stroke-linecap="round" opacity="0.25">'
                      f'<animate attributeName="opacity" values="0.12;0.45;0.12" dur="1.4s" repeatCount="indefinite"/></path>\n')
            else:
                g += f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="2" stroke-dasharray="4 8"/>\n'
        if hive:
            for i, k in enumerate("tmb"):
                for j in range(4):
                    g += car(f"{mode}{k}", 4.2 + 0.3*i, -(j*1.05 + i*0.35), GOLD if (i+j) % 3 else HONEY, r=4.5)
            for i, y in enumerate([cy-79, cy, cy+79]):
                g += pulse_hex((ox+dx)//2, y, 9, dur=2, begin=0.5*i)
        else:
            for j in range(12):
                # bunched traffic: tight spacing on a single road, crawling
                g += car(f"{mode}m", 11, -(j*0.55 + (j//4)*1.6), RED if j % 3 else "#FF7B72", r=4.5)
        g += pulse_hex(ox, cy, 15, color=col, dur=2.2, label="ORIGIN")
        g += pulse_hex(dx, cy, 15, color=col, dur=2.2, begin=1.1, label="DEST.")
        # congestion meter
        my = 398
        target = 0.32 if hive else 0.9
        g += (f'<text x="{px+22}" y="{my+4}" font-family="{FONT}" font-size="11" fill="{MUTED}">CONGESTION</text>'
              f'<rect x="{px+120}" y="{my-6}" width="400" height="10" rx="5" fill="{ROAD}"/>'
              f'<rect x="{px+120}" y="{my-6}" height="10" rx="5" fill="{GREEN if hive else RED}">'
              f'<animate attributeName="width" values="{400*target*0.85:.0f};{400*target:.0f};{400*target*0.85:.0f}" dur="2.6s" repeatCount="indefinite"/></rect>\n')
        return g

    s += panel(40, "selfish")
    s += panel(610, "hive")
    # arrow between panels
    s += (f'<g transform="translate(600,268)"><polygon points="-8,-10 6,0 -8,10" fill="{GOLD}" filter="url(#glow)">'
          f'<animateTransform attributeName="transform" type="translate" values="-4 0;4 0;-4 0" dur="1.4s" repeatCount="indefinite"/></polygon></g>\n')
    # stats strip
    stats = [("PRICE OF ANARCHY", "≈ 1.05", "at N = 40 · near system-optimal", GOLD),
             ("LEARNING", "MARL + GRU", "Random Forest feature selection", TEXT),
             ("SIMULATED IN", "SUMO + TraCI", "Metro Manila's EDSA corridor", TEXT)]
    for i, (lab, val, sub, col) in enumerate(stats):
        x = 40 + i*380
        s += f'''<g font-family="{FONT}">
  <rect x="{x}" y="438" width="360" height="78" rx="12" fill="{PANEL}" stroke="{LINE}"/>
  <text x="{x+20}" y="462" font-size="11" fill="{MUTED}" letter-spacing="1">{lab}</text>
  <text x="{x+20}" y="491" font-family="{SANS}" font-size="24" font-weight="800" fill="{col}"{' filter="url(#glow)"' if col == GOLD else ''}>{val}{'<animate attributeName="opacity" values="1;0.6;1" dur="2.4s" repeatCount="indefinite"/>' if col == GOLD else ''}</text>
  <text x="{x+20}" y="508" font-size="11" fill="{MUTED}">{sub}</text>
</g>
'''
    return s + "</svg>\n"


# ---------------------------------------------------------------- THE LINE (project route)
def the_line():
    W, H = 1200, 230
    xs = [110, 355, 600, 845, 1090]
    names = ["Traffic Hive", "SELAE", "GDGoC PLM Web", "Community", "Next stop"]
    subs = ["thesis · MARL", "OCR check-in", "member portal", "GDG on Campus", "stay tuned"]
    y = 112
    dur = 12
    # timeline: hold, travel, hold, travel... (5 holds, 4 travels)
    hold, travel = 1.6, 1.0
    times, vals = [], []
    t = 0
    for i, x in enumerate(xs):
        times.append(t); vals.append(x); t += hold
        times.append(t); vals.append(x)
        if i < len(xs)-1:
            t += travel
    total = t
    kt = ";".join(f"{v/total:.4f}" for v in times)
    arrive = [times[2*i]/total for i in range(len(xs))]
    s = svg_open(W, H, "The Line — Amiere's project route") + common_defs()
    s += hive_bg(W, H, sweep_dur=10)
    s += (f'<text x="40" y="46" font-family="{FONT}" font-size="13" fill="{GOLD}" letter-spacing="2">◆ THE LINE</text>'
          f'<text x="152" y="46" font-family="{FONT}" font-size="13" fill="{MUTED}">my route so far</text>\n')
    s += f'<line x1="{xs[0]}" y1="{y}" x2="{xs[-1]}" y2="{y}" stroke="{ROAD}" stroke-width="10" stroke-linecap="round"/>\n'
    s += (f'<line x1="{xs[-2]}" y1="{y}" x2="{xs[-1]}" y2="{y}" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 8"/>\n')
    wv = ";".join(str(v - xs[0]) for v in vals)
    for hgt, op in ((12, 0.25), (4, 1)):
        s += (f'<rect x="{xs[0]}" y="{y-hgt/2}" height="{hgt}" width="0" rx="{hgt/2}" fill="{GOLD}" opacity="{op}">'
              f'<animate attributeName="width" values="{wv}" keyTimes="{kt}" dur="{total}s" repeatCount="indefinite"/></rect>\n')
    for i, (x, n, sb) in enumerate(zip(xs, names, subs)):
        last = i == len(xs)-1
        on = HONEY if last else GOLD
        s += f'<g font-family="{FONT}">\n'
        s += (f'<polygon points="{hexpts(x,y,15)}" fill="{PANEL}" stroke="{LINE}" stroke-width="2"'
              f'{DASH if last else ""}>'
              f'<animate attributeName="stroke" values="{LINE};{on}" keyTimes="0;{arrive[i]:.4f}" calcMode="discrete" dur="{total}s" repeatCount="indefinite"/></polygon>\n')
        s += (f'<text x="{x}" y="{y+5}" text-anchor="middle" font-size="12" font-weight="700" fill="{MUTED}">{"?" if last else f"0{i+1}"}'
              f'<animate attributeName="fill" values="{MUTED};{on}" keyTimes="0;{arrive[i]:.4f}" calcMode="discrete" dur="{total}s" repeatCount="indefinite"/></text>\n')
        s += (f'<text x="{x}" y="{y+52}" text-anchor="middle" font-family="{SANS}" font-size="16" font-weight="700" fill="{TEXT}">{n}</text>'
              f'<text x="{x}" y="{y+72}" text-anchor="middle" font-size="12" fill="{MUTED}">{sb}</text>\n</g>\n')
    # the bee-bus marker
    tvals = ";".join(f"{v} {y}" for v in vals)
    s += f'''<g><animateTransform attributeName="transform" type="translate" values="{tvals}" keyTimes="{kt}" dur="{total}s" repeatCount="indefinite"/>
  <circle r="26" fill="{GOLD}" opacity="0.18" filter="url(#softglow)"/>
  <g transform="translate(0,-34)">
    <polygon points="{hexpts(0,0,11)}" fill="{GOLD}" filter="url(#glow)"/>
    <polygon points="{hexpts(0,0,4)}" fill="{BG}"/>
    <animateTransform attributeName="transform" type="translate" values="0 -34;0 -39;0 -34" dur="0.8s" repeatCount="indefinite"/>
  </g>
</g>
'''
    return s + "</svg>\n"


# ---------------------------------------------------------------- DIVIDER
def divider():
    W, H = 1200, 44
    s = svg_open(W, H, "road divider") + common_defs()
    s += f'<rect x="0" y="8" width="{W}" height="28" rx="14" fill="{ROAD}"/>\n'
    s += (f'<line x1="14" y1="22" x2="{W-14}" y2="22" stroke="{GOLD}" stroke-opacity="0.45" stroke-width="2" stroke-dasharray="16 14">'
          f'<animate attributeName="stroke-dashoffset" values="0;-60" dur="1s" repeatCount="indefinite"/></line>\n')
    s += '<defs><path id="dl1" d="M -20 15 H 1220"/><path id="dl2" d="M -20 29 H 1220"/></defs>\n'
    s += car("dl1", 6, 0, HONEY, r=3.5) + car("dl1", 6, -3, GOLD, r=3.5)
    s += car("dl2", 7.5, -1.5, BLUE, r=3.5, reverse=True) + car("dl2", 7.5, -5, GOLD, r=3.5, reverse=True)
    return s + "</svg>\n"


# ---------------------------------------------------------------- FOOTER
def footer():
    W, H = 1200, 190
    s = svg_open(W, H, "Next stop: wherever the next good idea is") + common_defs()
    s += hive_bg(W, H, sweep_dur=8)
    s += '<defs><path id="fl" d="M -40 150 C 300 120, 900 180, 1240 140"/></defs>\n'
    s += f'<path d="M -40 150 C 300 120, 900 180, 1240 140" fill="none" stroke="{ROAD}" stroke-width="30"/>\n'
    s += (f'<path d="M -40 150 C 300 120, 900 180, 1240 140" fill="none" stroke="{GOLD}" stroke-opacity="0.35" stroke-width="2" stroke-dasharray="14 12">'
          f'<animate attributeName="stroke-dashoffset" values="0;-52" dur="1.1s" repeatCount="indefinite"/></path>\n')
    for k in range(5):
        s += car("fl", 9, -k*1.8, GOLD if k % 2 else HONEY)
    s += (f'<text x="600" y="72" text-anchor="middle" font-family="{SANS}" font-size="26" font-weight="800" fill="{TEXT}">'
          f'Next stop: <tspan fill="{GOLD}">wherever the next good idea is.</tspan></text>\n'
          f'<text x="600" y="100" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{MUTED}">thanks for riding along · come build something with me</text>\n')
    s += pulse_hex(170, 64, 10) + pulse_hex(1030, 64, 10, begin=1.2)
    return s + "</svg>\n"


for name, fn in [("header", header), ("traffic-hive", showcase), ("the-line", the_line),
                 ("divider", divider), ("footer", footer)]:
    with open(f"{OUT}/{name}.svg", "w") as f:
        f.write(fn())
print("ok")
