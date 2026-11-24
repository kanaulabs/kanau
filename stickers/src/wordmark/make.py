"""Fader icon + QR + 'Kanau' wordmark, three flat layouts (D/X4 style).
python3 make.py <a|b|c> -> ./<variant>/"""
import os, sys, re, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kit'))
import kit
from kit import P, L, CAN
from PIL import ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
PAPER, WHITE, SLOT, INK = '#e8e1d3', '#fbfaf6', '#0b0b0d', '#050505'
COL = ['#a9a49a', '#f4a424', '#93c69f', '#e7a9b6', '#88aada']
LV = kit.FADER_LEVELS
M = 4.2; MOD = 0.35
FONT = [p for p in os.popen('fc-list : file family style').read().splitlines() if 'Manrope' in p and 'SemiBold' in p][0].split(':')[0]
WEIGHT = 600

def text_box(size_mm, txt='Kanau'):
    """ink bbox of txt at font-size size_mm: (x0, y0_from_baseline, x1, y1) in mm; y up negative."""
    f = ImageFont.truetype(FONT, 1000); x0, y0, x1, y1 = f.getbbox(txt, anchor='ls')
    k = size_mm / 1000; return x0 * k, y0 * k, x1 * k, y1 * k

def word(x, y_base, size, rot=0):
    """'Kanau' whose ink box left edge is at x (rot=0) — returns svg; for rot=-90 x,y is ink box bottom-left."""
    x0, y0, x1, y1 = text_box(size)
    if rot == 0:
        return (f'<text x="{P(x - x0):.3f}" y="{P(y_base):.3f}" font-family="Manrope" font-weight="{WEIGHT}" '
                f'font-size="{L(size):.3f}" fill="{INK}">Kanau</text>')
    # rotated -90: reading upward; ink box: width (x1-x0) becomes height, (y1-y0) becomes width
    return (f'<text transform="translate({P(x - y0):.3f} {P(y_base + x0):.3f}) rotate(-90)" font-family="Manrope" '
            f'font-weight="{WEIGHT}" font-size="{L(size):.3f}" fill="{INK}">Kanau</text>')

def pill(x, top, w, bottom, fill):
    return (f'<rect x="{P(x):.3f}" y="{P(top):.3f}" width="{L(w):.3f}" height="{L(bottom - top):.3f}" '
            f'rx="{L(w / 2):.3f}" fill="{fill}"/>')

def bank(x0, top, base, pitch, w):
    s = ''; T = base - top
    for i in range(5):
        x = x0 + i * pitch; lt = base - T * LV[i]
        if LV[i] < 0.999: s += pill(x, top, w, lt + w, SLOT)
        s += pill(x, lt, w, base, COL[i])
    return s

def qr(cx, cy, D):
    best = None; X, Y, m = P(cx), P(cy), L(MOD)
    for sd in range(1, 200):
        svg, n = kit.qr_round(cx, cy, D, MOD, fill=0.42, seed=sd)
        pts = [((float(a) - X) / m, (float(b) - Y) / m) for a, b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)"', svg)]
        far = [0.0] * 24
        for gx, gy in pts:
            a = int((math.atan2(gy, gx) + math.pi) / (2 * math.pi) * 24) % 24; far[a] = max(far[a], math.hypot(gx, gy))
        sc = min(far) - 0.35 * (max(far) - min(far))
        if best is None or sc > best[0]: best = (sc, svg)
    disc = f'<circle cx="{P(cx):.3f}" cy="{P(cy):.3f}" r="{L(D / 2):.3f}" fill="{WHITE}"/>'
    return disc, best[1]

def build(v):
    art = f'<rect width="{CAN:g}" height="{CAN:g}" fill="{PAPER}"/>'; fg = ''
    top, base = M, 60 - M; T = base - top
    if v in ('a', 'c'):                                  # X4 layout, word in the empty right column
        D = T * LV[4]; pitch = (60 - 2 * M - D) / 5; g = pitch * 0.21; w = pitch - g
        art += bank(M, top, base, pitch, w)
        cx = cy = 60 - M - D / 2; d, q = qr(cx, cy, D); art += d; fg += q
        colx0, colx1 = 60 - M - D, 60 - M; coly1 = cy - D / 2 - g
        if v == 'a':                                     # vertical, exactly the column's height, flush right
            H = coly1 - top; x0, y0, x1, y1 = text_box(10); size = 10 * H / (x1 - x0)
            x0, y0, x1, y1 = text_box(size); wid = y1 - y0
            fg += word(colx1 - wid, coly1, size, rot=-90)
            info = f'vertical word {size:.2f} mm font, ink {H:.1f} x {wid:.2f} mm'
        else:                                            # horizontal, column width, top aligned to slot tops
            W = colx1 - colx0; x0, y0, x1, y1 = text_box(10); size = 10 * W / (x1 - x0)
            x0, y0, x1, y1 = text_box(size); capt = -y0
            fg += word(colx0, top + capt, size)
            info = f'horizontal word {size:.2f} mm font, ink {W:.1f} x {capt:.2f} mm'
    else:                                                # b: faders across the top, word + QR on one baseline below
        D = 15.29; g = 1.9
        bank_base = base - D - g * 1.6
        pitch = (60 - 2 * M) / (5 - 0.21 * 0 - 0.24); w = pitch * 0.76
        pitch = (60 - 2 * M - w) / 4
        art += bank(M, top, bank_base, pitch, w)
        cx = 60 - M - D / 2; cy = base - D / 2; d, q = qr(cx, cy, D); art += d; fg += q
        avail = (cx - D / 2 - 2.5) - M
        x0, y0, x1, y1 = text_box(10); size = min(10 * avail / (x1 - x0), 10 * (D * 0.62) / -y0)
        x0, y0, x1, y1 = text_box(size)
        fg += word(M, base, size)
        info = f'word {size:.2f} mm font, ink {x1 - x0:.1f} x {-y0:.2f} mm; bank base {bank_base:.1f}, slot w {w:.2f}'
    return art, fg, info

if __name__ == '__main__':
    v = sys.argv[1]; out = os.path.join(HERE, v); os.makedirs(out, exist_ok=True)
    a, f, info = build(v); kit.save(out, a, f, ''); print(v, info, kit.preview(out)['must_pass_all'])
