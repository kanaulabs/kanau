"""Kanau sticker: the logo itself is the sticker. python3 make.py <l1|l2>"""
import os, sys, re, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kit'))
import kit, cuteqr
from kit import P, L, CAN
from PIL import ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
I = kit.ICON_180
BG, TRACK = '#09090b', '#212126'          # track lifted from #151519 so it survives CMYK
WHITE, INK, CREAM = '#fbfaf6', '#050505', '#e8e1d3'
FONT = '/usr/share/fonts/truetype/manrope/Manrope-SemiBold.ttf'
MOD = 0.35

GLOW = ['#d8d3ca', '#ffb53a', '#9fd3ab', '#f2b8c4', '#9dbdf0']

def icon2(ox, oy, S):
    """The icon as the app draws it: tile, quiet tracks, pills with their own soft glow."""
    k = S / 180; w = I['bar_w'] * k; r = S * I['corner_radius_ratio']
    s = f'<clipPath id="tile"><rect x="{P(ox):.3f}" y="{P(oy):.3f}" width="{L(S):.3f}" height="{L(S):.3f}" rx="{L(r):.3f}"/></clipPath>'
    s += f'<rect x="{P(ox):.3f}" y="{P(oy):.3f}" width="{L(S):.3f}" height="{L(S):.3f}" rx="{L(r):.3f}" fill="{BG}"/>'
    s += '<g clip-path="url(#tile)">'
    for i in range(5):
        x = ox + I['bar_x'][i] * k; t0 = oy + I['track_top'] * k; b = oy + I['track_bottom'] * k
        s += f'<rect x="{P(x):.3f}" y="{P(t0):.3f}" width="{L(w):.3f}" height="{L(b - t0):.3f}" rx="{L(w / 2):.3f}" fill="#1c1c21"/>'
    for i in range(5):
        x = ox + I['bar_x'][i] * k; t = oy + I['bar_top'][i] * k; b = oy + I['track_bottom'] * k
        op, sd = (0.75, 1.1) if i == 1 else (0.42, 0.75)
        s += (f'<rect x="{P(x):.3f}" y="{P(t):.3f}" width="{L(w):.3f}" height="{L(b - t):.3f}" rx="{L(w / 2):.3f}" '
              f'fill="{GLOW[i]}" opacity="{op}" filter="url(#gl{i})"/>')
    for i in range(5):
        x = ox + I['bar_x'][i] * k; t = oy + I['bar_top'][i] * k; b = oy + I['track_bottom'] * k
        s += f'<rect x="{P(x):.3f}" y="{P(t):.3f}" width="{L(w):.3f}" height="{L(b - t):.3f}" rx="{L(w / 2):.3f}" fill="url(#fd{i})"/>'
    return s + '</g>'

def glow_defs():
    d = ''
    for i in range(5):
        sd = 1.1 if i == 1 else 0.75
        d += (f'<filter id="gl{i}" filterUnits="userSpaceOnUse" x="-40" y="-40" width="{CAN + 80:g}" height="{CAN + 80:g}">'
              f'<feGaussianBlur stdDeviation="{L(sd):.3f}"/></filter>')
    return d

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

def word(x, base, cap, fill, anchor='start', font=FONT, weight=600, ls=0.0):
    f = ImageFont.truetype(font, 1000); x0, y0, x1, y1 = f.getbbox('Kanau', anchor='ls')
    size = cap / (-y0 / 1000)
    if anchor == 'middle': x = x - (x1 + x0) / 2000 * size
    else: x = x - x0 / 1000 * size
    if ls and anchor == 'middle': x -= ls * 2
    return (f'<text x="{P(x):.3f}" y="{P(base):.3f}" font-family="Manrope" font-weight="{weight}" '
            f'font-size="{L(size):.3f}" letter-spacing="{L(ls):.3f}" fill="{fill}">Kanau</text>')

def build(v):
    defs = kit.fader_defs('fd')
    if v == 'l1':   # full-bleed icon, round QR bottom-right, small name in the bottom margin
        art = f'<rect width="{CAN:g}" height="{CAN:g}" fill="{BG}"/>' + icon(0, 0, 60)
        D = 15.3; c = 60 - 3.6 - D / 2
        d, q = qr(c, c, D); art += d
        k = 60 / 180; base = I['track_bottom'] * k + (60 - I['track_bottom'] * k) / 2 + 1.25
        fg = q + word(I['bar_x'][0] * k, base, 2.5, '#d9d5cd')
    elif v == 'l3':  # l2 refined: bigger tile, glow like the app, badge cut out of the tile, quieter label
        defs += glow_defs()
        S = 41.0; ox = (60 - S) / 2; oy = 8.4
        art = f'<rect width="{CAN:g}" height="{CAN:g}" fill="{CREAM}"/>' + icon2(ox, oy, S)
        D = 15.3; cx = ox + S - 2.9; cy = oy + 2.9; RING = 0.9
        art += f'<circle cx="{P(cx):.3f}" cy="{P(cy):.3f}" r="{L(D / 2 + RING):.3f}" fill="{CREAM}"/>'
        d, q = qr(cx, cy, D, fill=0.42); art += d
        fg = q + word(30, oy + S + 6.3, 2.75, INK, anchor='middle',
                      font='/usr/share/fonts/truetype/manrope/Manrope-Medium.ttf', weight=500, ls=0.06)
    elif v.startswith('q'):   # l3 with a friendlier QR badge
        defs += glow_defs()
        S = 41.0; ox = (60 - S) / 2; oy = 8.4
        art = f'<rect width="{CAN:g}" height="{CAN:g}" fill="{CREAM}"/>' + icon2(ox, oy, S)
        cfg = dict(q1=dict(ec='m', modules='liquid', eyes='round', D=15.3),
                   q2=dict(ec='m', modules='dots', eyes='round', D=15.3),
                   q3=dict(ec='q', modules='liquid', eyes='round', D=17.0, hole=9),
                   q4=dict(ec='m', modules='liquid', eyes='soft', D=15.3))[v]
        D = cfg['D']; cx = ox + S - 2.9; cy = oy + 2.9 + (D - 15.3) / 2
        cx -= (D - 15.3) / 2
        art += f'<circle cx="{P(cx):.3f}" cy="{P(cy):.3f}" r="{L(D / 2 + 0.9):.3f}" fill="{CREAM}"/>'
        art += f'<circle cx="{P(cx):.3f}" cy="{P(cy):.3f}" r="{L(D / 2):.3f}" fill="{WHITE}"/>'
        def mini(x, y, size):
            # the app icon in miniature, in the middle of the code
            t = size * 0.86; tx = x + (size - t) / 2; ty = y + (size - t) / 2
            return icon(tx, ty, t, tile=True)
        q, hart, n = cuteqr.draw(cx, cy, MOD, ec=cfg['ec'], modules=cfg['modules'], eyes=cfg['eyes'],
                                 hole=cfg.get('hole', 0), hole_svg=mini)
        art += hart
        fg = q + word(30, oy + S + 6.3, 2.75, INK, anchor='middle',
                      font='/usr/share/fonts/truetype/manrope/Manrope-Medium.ttf', weight=500, ls=0.06)
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
