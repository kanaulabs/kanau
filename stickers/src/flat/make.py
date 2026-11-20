"""Kanau sticker, direction d-graphic ("Flat and bold").

Idea: the icon taken out of its black square and printed like a poster on paper: four black fader
slots, and the lit one filled with amber right through the top of the sticker, all standing on one
baseline that ends in the QR, a white dot exactly as tall as the lowest fader: a full stop.

Run:  python3 make.py            -> writes the design + previews into this folder
      python3 make.py --study    -> also writes comparison variants and a cut-drift check into ./_explore
Everything is flat colour: no gradients, no filters, no opacity, no strokes.
"""
import os, re, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kit'))
import kit
from kit import P, L, CAN

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- palette (flat) -------------------------------------------------------------------------
PAPER = '#e8e1d3'                  # warm paper ground (a light tint: about C7 M9 Y16 K0)
WHITE = '#fbfaf6'                  # the dot: bare paper white, the QR ground (print: no ink)
SLOT = '#0b0b0d'                   # empty fader slot: the icon's near-black
COL = ['#a9a49a', '#f4a424', '#93c69f', '#e7a9b6', '#88aada']   # grey, amber, green, pink, blue
LEVELS = kit.FADER_LEVELS          # 74/135, 1, 59/135, 92/135, 40/135: the icon's own levels

# ---- geometry (mm, finished-sticker coordinates) -------------------------------------------
M = 4.2                            # one margin on all four sides (straight slot edges stay > 4 mm from the cut)
MOD = 0.35                         # QR module
GAP = 0.21                         # gap as a share of the slot pitch
WORD = 2.2                         # font-size of the wordmark inside the amber fader (>= 1.8 mm)


def pill(x, top, w, bottom, fill):
    return (f'<rect x="{P(x):.3f}" y="{P(top):.3f}" width="{L(w):.3f}" height="{L(bottom - top):.3f}" '
            f'rx="{L(w / 2):.3f}" fill="{fill}"/>')


def round_qr(cx, cy, D, fill=0.42, ink=kit.QR_INK, seeds=range(1, 300)):
    """kit.qr_round, with the filler seed chosen so the dot cloud has an evenly populated rim
    (no bald sectors, no lonely stragglers) and therefore sits concentric in the disc."""
    best = None; X, Y, m = P(cx), P(cy), L(MOD)
    for s in seeds:
        svg, n = kit.qr_round(cx, cy, D, MOD, fg=ink, fill=fill, seed=s)
        pts = [((float(a) - X) / m, (float(b) - Y) / m)
               for a, b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)"', svg)]
        far = [0.0] * 24
        for gx, gy in pts:
            r = math.hypot(gx, gy)
            a = int((math.atan2(gy, gx) + math.pi) / (2 * math.pi) * 24) % 24
            far[a] = max(far[a], r)
        score = min(far) - 0.35 * (max(far) - min(far))
        if best is None or score > best[0]:
            best = (score, s, svg, n)
    return best[2], best[3], best[1]


def build(ground=PAPER, dot=WHITE, slot=SLOT, cols=COL, amber_through=True, word=WORD, fill=0.42):
    """Returns (art, fg, info). Positions in mm from the finished top-left corner."""
    top = M; base = 60 - M; T = base - top
    D = T * LEVELS[4]                            # the dot is exactly as tall as the lowest (blue) level
    pitch = (60 - 2 * M - D) / 5                 # row = 5 slots + 5 equal gaps + the dot
    g = pitch * GAP; w = pitch - g
    xs = [M + i * pitch for i in range(5)]
    art = f'<rect width="{CAN:g}" height="{CAN:g}" fill="{ground}"/>'
    for i in range(5):
        lt = base - T * LEVELS[i]                # top of the coloured level
        if LEVELS[i] > 0.999:                    # the lit one: no slot left, and it leaves the sticker
            art += pill(xs[i], -8.0 if amber_through else top, w, base, cols[i])
            continue
        if slot:                                 # slot stops just inside the level: no black fringe
            art += pill(xs[i], top, w, lt + w, slot)
        art += pill(xs[i], lt, w, base, cols[i])
    cx = 60 - M - D / 2; cy = base - D / 2
    art += f'<circle cx="{P(cx):.3f}" cy="{P(cy):.3f}" r="{L(D / 2):.3f}" fill="{dot}"/>'
    fg, n, seed = round_qr(cx, cy, D, fill=fill)
    if word:
        # the one word, set small up the lit fader, centred on the dot's equator
        ax = xs[1] + w / 2
        fg += (f'<text transform="translate({P(ax + word * 0.318):.3f} {P(cy):.3f}) rotate(-90)" '
               f'font-family="Manrope" font-weight="700" font-size="{L(word):.3f}" letter-spacing="0.12" '
               f'text-anchor="middle" fill="{kit.QR_INK}">Kanau</text>')
    info = dict(slot_w=round(w, 3), gap=round(g, 3), dot_D=round(D, 3), module=MOD, n=n, seed=seed,
                dot_centre=(round(cx, 3), round(cy, 3)), margin=M, amber_axis=round(xs[1] + w / 2, 3))
    return art, fg, info


BLACK = dict(ground=SLOT, slot=None, cols=['#c4c0b8', '#f4a62a', '#9ccfa6', '#eab3be', '#8fb0de'])


def _quick(out, **cfg):
    from PIL import Image
    a, f, _ = build(**cfg)
    kit.save(out, a, f, ''); kit.render(os.path.join(out, 'full.svg'), os.path.join(out, 'full.png'), 1280)
    im = Image.open(os.path.join(out, 'full.png')).convert('RGB'); c = round(im.width * 2 / 64)
    fin = im.crop((c, c, im.width - c, im.height - c)).resize((1200, 1200), Image.LANCZOS)
    fin.save(os.path.join(out, 'finish.png')); fin.resize((240, 240), Image.LANCZOS).save(os.path.join(out, 'thumb.png'))


if __name__ == '__main__':
    art, fg, info = build()
    kit.save(HERE, art, fg, '')
    rep = kit.preview(HERE)
    print(info); print(rep)
    # same drawing on the icon's own black, kept as a fallback if paper-cream is a step too far
    if '--study' in sys.argv:
        from PIL import Image
        EX = os.path.join(HERE, '_explore'); os.makedirs(EX, exist_ok=True); items = [('final', HERE)]
        studies = {
            'v-calm': dict(amber_through=False),
            'v-noword': dict(word=0),
        }
        for name, cfg in studies.items():
            _quick(os.path.join(EX, name), **cfg); items.append((name, os.path.join(EX, name)))
        kit.contact_sheet(items, os.path.join(EX, 'sheet-v.png'), tile=640, cols=2)
        # cut-drift check: the same print trimmed 1.5 mm off in four diagonal directions
        full = Image.open(os.path.join(HERE, 'full.png')).convert('RGB'); k = full.width / 64
        sheet = Image.new('RGB', (4 * 420 + 5 * 20, 460), (120, 116, 108))
        for j, (dx, dy) in enumerate([(-1.5, -1.5), (1.5, -1.5), (-1.5, 1.5), (1.5, 1.5)]):
            box = tuple(round(v * k) for v in (2 + dx, 2 + dy, 62 + dx, 62 + dy))
            sheet.paste(full.crop(box).resize((420, 420), Image.LANCZOS), (20 + j * 440, 20))
        sheet.save(os.path.join(EX, 'drift.png'))
