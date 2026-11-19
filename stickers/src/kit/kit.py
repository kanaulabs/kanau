"""Kanau sticker kit: shared geometry, QR generators, rendering, scan tests, phone mockup.

Coordinate system
  Canvas = 64 x 64 mm (60 x 60 mm finished sticker + 2 mm bleed on every side).
  SVG user units: U = 4 units per mm, so the canvas is 256 x 256 units.
  P(v): position in mm measured from the FINISHED top-left corner -> user units (adds the bleed).
  L(v): length in mm -> user units.
  Anything that must survive cutting stays inside P(2)..P(58) (the safe zone); backgrounds must
  run to the canvas edge (0..256).
"""
import os, sys, json, math, random, subprocess
import segno

KIT = os.path.dirname(os.path.abspath(__file__))
U = 4.0
BLEED = 2.0
FIN = 60.0
CAN = (FIN + 2 * BLEED) * U
URL = 'https://apps.apple.com/app/id6800003312'

def P(v): return (BLEED + v) * U
def L(v): return v * U

# ---- brand ---------------------------------------------------------------------------------
BG = '#09090b'            # icon background (near black)
TRACK = '#151519'         # unlit fader track
CREAM = '#eeeae2'         # warm off-white used for type / QR ground
QR_INK = '#050505'        # QR dark modules (becomes 100% K in print)
AMBER = '#f39a1e'         # glow colour of the lit fader
# five faders, left to right: warm grey, amber (full, glowing), green, pink, blue
FADER_LEVELS = [74 / 135, 1.0, 59 / 135, 92 / 135, 40 / 135]
FADER_COLORS = [('#cfcbc3', '#a29e96'), ('#fcc04a', '#dc7f14'), ('#acd8b4', '#84bb92'),
                ('#f3c3cc', '#d99ba9'), ('#98b8e2', '#82a4d4')]   # (top, bottom) of each pill
FADER_FLAT = ['#c4c0b8', '#f4a62a', '#9ccfa6', '#eab3be', '#8fb0de']
# original app icon, measured on a 180 px icon: pills 19 wide, pitch ~28.75, tracks y 22..157
ICON_180 = dict(bar_x=[23, 51, 80, 109, 138], bar_w=19, track_top=22, track_bottom=157,
                bar_top=[83, 22, 98, 65, 117], corner_radius_ratio=0.2237)

def fader_defs(prefix='fd'):
    """<linearGradient> defs for the five brand pills: ids fd0..fd4."""
    return ''.join(
        f'<linearGradient id="{prefix}{i}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
        for i, (a, b) in enumerate(FADER_COLORS))

def faders(x, y, w, h, ratio=0.56, levels=None, track=TRACK, fills=None, prefix='fd'):
    """Five pills in a box (x, y, w, h in mm, finished coords). ratio = pill width / pitch.
    fills: list of 5 paint strings; default = brand gradients from fader_defs()."""
    levels = levels or FADER_LEVELS
    pitch = w / (4 + ratio); bw = pitch * ratio; r = bw / 2; s = ''
    for i in range(5):
        px = x + i * pitch
        if track:
            s += (f'<rect x="{P(px):.2f}" y="{P(y):.2f}" width="{L(bw):.2f}" height="{L(h):.2f}" '
                  f'rx="{L(r):.2f}" fill="{track}"/>')
    for i in range(5):
        px = x + i * pitch; lh = max(h * levels[i], bw); t = y + h - lh
        paint = fills[i] if fills else f'url(#{prefix}{i})'
        s += (f'<rect x="{P(px):.2f}" y="{P(t):.2f}" width="{L(bw):.2f}" height="{L(lh):.2f}" '
              f'rx="{L(r):.2f}" fill="{paint}"/>')
    return s

# ---- QR ------------------------------------------------------------------------------------
def qr_matrix(ec='m'):
    """Module matrix for the App Store URL. ec 'm' -> 29x29, 'q' -> 33x33, 'h' -> 37x37."""
    q = segno.make(URL, error=ec, micro=False, boost_error=False)
    return [[bool(c) for c in row] for row in q.matrix]

def _is_finder(x, y, n):
    return (x < 7 and y < 7) or (x >= n - 7 and y < 7) or (x < 7 and y >= n - 7)

FINDER_A = 0.8      # outer corner radius of a rounded finder, in modules. 0.8 keeps strict decoders happy (1.6 = old look, OpenCV reads only ~20-50%)

def _finder(X, Y, m, fg, rounded):
    """One 7x7 finder pattern at user-unit position X, Y with module size m (user units)."""
    if not rounded:
        return (f'<path fill-rule="evenodd" fill="{fg}" d="M{X},{Y}h{7*m}v{7*m}h{-7*m}z '
                f'M{X+m},{Y+m}v{5*m}h{5*m}v{-5*m}z"/>'
                f'<rect x="{X+2*m}" y="{Y+2*m}" width="{3*m}" height="{3*m}" fill="{fg}"/>')
    a = FINDER_A * m; b = max(FINDER_A - 1.0, 0.0) * m; s = 7 * m - 2 * a; t = 5 * m - 2 * b
    inner = (f'M{X+m+b},{Y+m} a{b},{b} 0 0 0 {-b},{b} v{t} a{b},{b} 0 0 0 {b},{b} h{t} '
             f'a{b},{b} 0 0 0 {b},{-b} v{-t} a{b},{b} 0 0 0 {-b},{-b} z') if b > 0 else \
            f'M{X+m},{Y+m}v{5*m}h{5*m}v{-5*m}z'
    return (f'<path fill-rule="evenodd" fill="{fg}" d="M{X+a},{Y} h{s} a{a},{a} 0 0 1 {a},{a} v{s} '
            f'a{a},{a} 0 0 1 {-a},{a} h{-s} a{a},{a} 0 0 1 {-a},{-a} v{-s} a{a},{a} 0 0 1 {a},{-a} z '
            f'{inner}"/>'
            f'<rect x="{X+2*m}" y="{Y+2*m}" width="{3*m}" height="{3*m}" rx="{FINDER_A*0.5*m}" fill="{fg}"/>')

def _module(X, Y, m, fg, style):
    if style == 'dots':
        return f'<circle cx="{X+m/2:.3f}" cy="{Y+m/2:.3f}" r="{m*0.46:.3f}" fill="{fg}"/>'
    return f'<rect x="{X:.3f}" y="{Y:.3f}" width="{m+0.02:.3f}" height="{m+0.02:.3f}" fill="{fg}"/>'

def qr_square(x, y, size, fg=QR_INK, ec='m', style='square', rounded_finders=True):
    """Plain QR, no quiet zone, top-left at (x, y) mm, edge = size mm. Draw your own light ground
    under it with at least 2 modules of clear margin. Returns (svg, module_mm, n_modules)."""
    M = qr_matrix(ec); n = len(M); mod = size / n; m = L(mod); ox = P(x); oy = P(y); s = ''
    for gy in range(n):
        for gx in range(n):
            if M[gy][gx] and not _is_finder(gx, gy, n):
                s += _module(ox + gx * m, oy + gy * m, m, fg, style)
    for fx, fy in [(0, 0), (n - 7, 0), (0, n - 7)]:
        s += _finder(ox + fx * m, oy + fy * m, m, fg, rounded_finders)
    return s, mod, n

def qr_round(cx, cy, D, module, fg=QR_INK, ec='m', style='dots', gap=2, fill=0.42, seed=7,
             rounded_finders=True, edge_margin=0.9):
    """Round-badge QR: the real code centred at (cx, cy) mm, decorative filler modules on the same
    grid out to a circle of diameter D mm, leaving a clear ring of `gap` modules around the real
    code. Does NOT draw the disc; draw a light disc of diameter D under it first.
    Needs n*module*1.42 < D. Returns (svg, n_modules)."""
    M = qr_matrix(ec); n = len(M); rnd = random.Random(seed); s = ''
    q = n * module; ox = cx - q / 2; oy = cy - q / 2; R = D / 2 - edge_margin * module
    ext = int((2 * R) / module) + 4; start = -(ext - n) // 2; m = L(module)
    for gy in range(start, start + ext):
        for gx in range(start, start + ext):
            px = ox + gx * module; py = oy + gy * module
            if 0 <= gx < n and 0 <= gy < n:
                if M[gy][gx] and not _is_finder(gx, gy, n):
                    s += _module(P(px), P(py), m, fg, style)
                continue
            if -gap <= gx < n + gap and -gap <= gy < n + gap:
                continue
            if math.hypot(px + module / 2 - cx, py + module / 2 - cy) > R - module * 0.5:
                continue
            if rnd.random() < fill:
                s += _module(P(px), P(py), m, fg, style)
    for fx, fy in [(0, 0), (n - 7, 0), (0, n - 7)]:
        s += _finder(P(ox + fx * module), P(oy + fy * module), m, fg, rounded_finders)
    return s, n

# ---- files ---------------------------------------------------------------------------------
def _wrap(body, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {CAN:g} {CAN:g}" width="64mm" height="64mm"><defs>{defs}</defs>{body}</svg>')

GUIDES = (f'<rect x="{P(0)}" y="{P(0)}" width="{L(60)}" height="{L(60)}" fill="none" stroke="#ff00ff" stroke-width="0.8"/>'
          f'<rect x="{P(2)}" y="{P(2)}" width="{L(56)}" height="{L(56)}" fill="none" stroke="#00c8ff" '
          f'stroke-width="0.6" stroke-dasharray="3 2"/>')

def save(outdir, art, fg, defs=''):
    """Write the design as two layers.
      art: everything that may be rasterised for print (background, faders, glows, shadows, the
           light ground under the QR). Any SVG feature Chromium renders is allowed.
      fg:  crisp vector layer drawn on top: QR modules and type ONLY. Flat opaque fills, no
           opacity, no filters, no gradients, no strokes thinner than 0.1 mm.
    Files: art.svg, fg.svg, full.svg, guides.svg in outdir."""
    os.makedirs(outdir, exist_ok=True)
    for name, body in [('art', art), ('fg', fg), ('full', art + fg), ('guides', art + fg + GUIDES)]:
        open(os.path.join(outdir, name + '.svg'), 'w').write(_wrap(body, defs))

def render(svg, png, px=1280):
    subprocess.run(['node', os.path.join(KIT, 'render.js'), svg, png, str(px)], check=True)

SCAN_MUST = ['full', 'w600', 'w400', 'blur', 'perspective', 'dim', 'rot12']
def scan(png):
    """Decode the QR in a picture of the finished sticker under several stresses.
    Returns {test: bool}. All of SCAN_MUST should be True; 'w300' is a harsh bonus test."""
    import cv2, numpy as np, zxingcpp
    im = cv2.imread(png); h, w = im.shape[:2]
    def ok(a): return any(r.text == URL for r in zxingcpp.read_barcodes(a))
    def rs(px): return cv2.resize(im, (px, px), interpolation=cv2.INTER_AREA)
    pt = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]),
                                     np.float32([[w*.07, h*.04], [w*.97, 0], [w, h], [0, h*.93]]))
    rot = cv2.getRotationMatrix2D((w / 2, h / 2), 12, 0.85)
    tests = {'full': im, 'w600': rs(600), 'w400': rs(400), 'w300': rs(300),
             'blur': cv2.GaussianBlur(rs(800), (5, 5), 0),
             'perspective': cv2.warpPerspective(im, pt, (w, h), borderValue=(120, 120, 120)),
             'dim': (rs(800) * 0.45 + 35).astype('uint8'),
             'rot12': cv2.warpAffine(im, rot, (w, h), borderValue=(120, 120, 120))}
    return {k: bool(ok(v)) for k, v in tests.items()}

def preview(outdir):
    """Render everything a reviewer needs and test the QR. Writes into outdir:
      finish.png  the finished 60x60 mm sticker, 1200 px (bleed cropped off)
      thumb.png   the same at 240 px, roughly life size on a screen
      guides.png  full canvas with the cut line (magenta) and safe zone (cyan dashes)
      phone.png   the sticker inside a clear case on a dark and a light phone
      report.json QR scan results
    Returns the report dict."""
    from PIL import Image
    full = os.path.join(outdir, 'full.png')
    render(os.path.join(outdir, 'full.svg'), full, 1280)
    render(os.path.join(outdir, 'guides.svg'), os.path.join(outdir, 'guides.png'), 900)
    im = Image.open(full).convert('RGB'); c = round(im.width * BLEED / (FIN + 2 * BLEED))
    fin = im.crop((c, c, im.width - c, im.height - c)).resize((1200, 1200), Image.LANCZOS)
    fin.save(os.path.join(outdir, 'finish.png'))
    fin.resize((240, 240), Image.LANCZOS).save(os.path.join(outdir, 'thumb.png'))
    subprocess.run(['node', os.path.join(KIT, 'mock.js'), os.path.join(outdir, 'full.svg'),
                    os.path.join(outdir, 'phone.png')], check=True)
    res = scan(os.path.join(outdir, 'finish.png'))
    rep = {'scan': res, 'must_pass_all': all(res[k] for k in SCAN_MUST),
           'failed': [k for k, v in res.items() if not v]}
    json.dump(rep, open(os.path.join(outdir, 'report.json'), 'w'), indent=1)
    return rep

def contact_sheet(items, out, tile=560, cols=3, key='finish.png'):
    """items: list of (label, dir). Side-by-side comparison picture."""
    from PIL import Image, ImageDraw, ImageFont
    rows = math.ceil(len(items) / cols); pad = 24; lab = 40
    sheet = Image.new('RGB', (cols * (tile + pad) + pad, rows * (tile + pad + lab) + pad), (214, 210, 202))
    d = ImageDraw.Draw(sheet)
    try: f = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', 24)
    except Exception: f = ImageFont.load_default()
    for i, (label, dr) in enumerate(items):
        x = pad + (i % cols) * (tile + pad); y = pad + (i // cols) * (tile + pad + lab)
        sheet.paste(Image.open(os.path.join(dr, key)).convert('RGB').resize((tile, tile), Image.LANCZOS), (x, y))
        d.text((x, y + tile + 8), label, fill=(40, 38, 34), font=f)
    sheet.save(out)

if __name__ == '__main__':
    print(json.dumps(preview(sys.argv[1]), indent=1))
