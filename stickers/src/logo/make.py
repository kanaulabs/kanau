"""Kanau sticker: the logo itself is the sticker. python3 make.py <l1|l2>"""
import os, sys, re, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kit'))
import kit
from kit import P, L, CAN
from PIL import ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
I = kit.ICON_180
BG, TRACK = '#09090b', '#212126'          # track lifted from #151519 so it survives CMYK
WHITE, INK, CREAM = '#fbfaf6', '#050505', '#e8e1d3'
FONT = '/usr/share/fonts/truetype/manrope/Manrope-SemiBold.ttf'
MOD = 0.35

def icon(ox, oy, S, tile=False):
    """The app icon at (ox, oy) mm, edge S mm. tile=True draws its own rounded black square."""
    k = S / 180; s = ''
    if tile:
        s += (f'<rect x="{P(ox):.3f}" y="{P(oy):.3f}" width="{L(S):.3f}" height="{L(S):.3f}" '
              f'rx="{L(S * I["corner_radius_ratio"]):.3f}" fill="{BG}"/>')
    w = I['bar_w'] * k
    for i in range(5):
        x = ox + I['bar_x'][i] * k; t0 = oy + I['track_top'] * k; b = oy + I['track_bottom'] * k
        s += f'<rect x="{P(x):.3f}" y="{P(t0):.3f}" width="{L(w):.3f}" height="{L(b - t0):.3f}" rx="{L(w / 2):.3f}" fill="{TRACK}"/>'
    for i in range(5):
        x = ox + I['bar_x'][i] * k; t = oy + I['bar_top'][i] * k; b = oy + I['track_bottom'] * k
        s += f'<rect x="{P(x):.3f}" y="{P(t):.3f}" width="{L(w):.3f}" height="{L(b - t):.3f}" rx="{L(w / 2):.3f}" fill="url(#fd{i})"/>'
    return s

def qr(cx, cy, D, fill=0.42):
    best = None; X, Y, m = P(cx), P(cy), L(MOD)
    for sd in range(1, 160):
        svg, n = kit.qr_round(cx, cy, D, MOD, fill=fill, seed=sd)
        pts = [((float(a) - X) / m, (float(b) - Y) / m) for a, b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)"', svg)]
        far = [0.0] * 24
        for gx, gy in pts:
            a = int((math.atan2(gy, gx) + math.pi) / (2 * math.pi) * 24) % 24; far[a] = max(far[a], math.hypot(gx, gy))
        sc = min(far) - 0.35 * (max(far) - min(far))
        if best is None or sc > best[0]: best = (sc, svg)
    return f'<circle cx="{P(cx):.3f}" cy="{P(cy):.3f}" r="{L(D / 2):.3f}" fill="{WHITE}"/>', best[1]

def word(x, base, cap, fill, anchor='start'):
    f = ImageFont.truetype(FONT, 1000); x0, y0, x1, y1 = f.getbbox('Kanau', anchor='ls')
    size = cap / (-y0 / 1000)
    if anchor == 'middle': x = x - (x1 + x0) / 2000 * size
    else: x = x - x0 / 1000 * size
    return (f'<text x="{P(x):.3f}" y="{P(base):.3f}" font-family="Manrope" font-weight="600" '
            f'font-size="{L(size):.3f}" fill="{fill}">Kanau</text>')

def build(v):
    defs = kit.fader_defs('fd')
    if v == 'l1':   # full-bleed icon, round QR bottom-right, small name in the bottom margin
        art = f'<rect width="{CAN:g}" height="{CAN:g}" fill="{BG}"/>' + icon(0, 0, 60)
        D = 15.3; c = 60 - 3.6 - D / 2
        d, q = qr(c, c, D); art += d
        k = 60 / 180; base = I['track_bottom'] * k + (60 - I['track_bottom'] * k) / 2 + 1.25
        fg = q + word(I['bar_x'][0] * k, base, 2.5, '#d9d5cd')
    else:           # the icon as it sits on a home screen: tile, QR as its badge, name as its label
        S = 38.0; ox = (60 - S) / 2; oy = 9.0
        art = f'<rect width="{CAN:g}" height="{CAN:g}" fill="{CREAM}"/>' + icon(ox, oy, S, tile=True)
        D = 15.3; cx = ox + S - 2.2; cy = oy + 2.2
        d, q = qr(cx, cy, D, fill=0.42); art += d
        fg = q + word(30, oy + S + 7.2, 3.4, INK, anchor='middle')
    return art, fg, defs

if __name__ == '__main__':
    v = sys.argv[1]; out = os.path.join(HERE, v); os.makedirs(out, exist_ok=True)
    a, f, d = build(v); kit.save(out, a, f, d); print(v, kit.preview(out)['must_pass_all'])
