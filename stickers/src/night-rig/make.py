"""Kanau sticker, design F "Night rig", print finish (from f-wildcard-v2).

The idea is v2's and is not touched: the app icon built for real, at night. Five capsules stand in still
water; ONE of them is on (amber, at full); one small gaffer with a phone stands in front of it; and the
moon in the sky is the QR.
  key   the amber column is the only source. Tight bloom, short haze, hot core, darker limb.
  fill  none. The four other columns are off: dusk-dim body colour, lit only where they face the key
        (grey's right flank, green's left flank, pink's left flank above green's shadow, blue: nothing).
  rim   the moon: a cool disc carrying a clean code, a hair of cool light on every upper-right shoulder,
        a cool line on the horizon and a short path of soft glints on the water under it.

What the finish changed (numbers in check.py):
  moon     flat ground to 0.94 R, now a cool off-white (v2's was warm, b* +5; a cool halo round a warm disc reads as
           a glow painted round a label), limb only in the last 6 %, halo .15 -> .30 in two parts (set on the
           CMYK proof), 16.0 -> 16.6 mm so the code's 2-module quiet square fits inside the disc, corners too.
  figure   side-on with the phone in front of the chest and the head back (POSE=B). POSE=A is v2's figure,
           POSE=C the alternative that lost.
  water    horizon 52.46 -> 51.0: 9 mm of water instead of 7.5. The horizon is now chosen, not solved.
  colour   the four unlit columns +4 to +6 L*, a little more chroma; grey rebuilt near-neutral.
  details  cool horizon line .4 -> .7; glints drawn at a known thickness instead of noise hairs (see the repair).
  margin   M 4.2 -> 5.0 mm.
  finders  the kit's new default (0.8 module radius); nothing to do here but rebuild.

What the repair after the two reviews changed (numbers in check.py, pictures in _repair/):
  glints   26 hard dashes (a ladder, proof peak L* 85, seven of them within 1.5 mm of the cut) -> 9 soft ellipses,
           one per row, 0.20-0.27 mm thick, opacity .47 -> .18, proof peak L* 62, the last one 2.4 mm inside the
           cut. GSEED 56 instead of 5: 5 drew a diagonal trail with one stray, 56 alternates either side of the axis.
  halo     the two outer stops raised (.37 -> .45 at 1.8 mm, .15 -> .24 at 4.1 mm; HALO stays .30) so that the
           print keeps an aureole and not only a 1.5 mm corona.
  finders  unchanged (round, the kit's default). FINDERS=square builds the reviewer's optional square finders;
           see _repair/finder_test*.py for why it is not the default.

One measure u = pill radius: pill width 2u, gap between pills u, the blue axis under the moon's centre.
One margin M: grey's left edge, the amber cap, the moon's top and the moon's right edge.
(v2 also had "moon clear of the pink cap by u". With the larger moon, the wider margin and the higher horizon
that clearance is 0.64 u = 2.06 mm; it is printed at the end of a run.)

Layers: art = everything photographic + the moon disc (rasterised for print).  fg = QR modules only.
Run:  python3 make.py                                   regenerates everything in this folder
      POSE=A OUT=alt-figure-v2 python3 make.py          alternate: v2's figure in the finished picture
      MOON=v2 OUT=alt-moon-v2-ground python3 make.py    alternate: v2's warm off-white as the moon's ground (MOON=cream: brand cream)
      FINDERS=square OUT=alt-finders-square python3 make.py   alternate: square finders (strict decoders read them a little better)
      python3 check.py                                  the measurements
"""
import os, sys, json, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kit'))
import kit
from kit import P, L, CAN, FADER_LEVELS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT') or HERE
if not os.path.isabs(OUT):
    OUT = os.path.join(HERE, OUT)
FIGURE_ON = os.environ.get('FIGURE', '1') != '0'
def opt(name, default):
    return float(os.environ.get(name, default))

# ---- geometry (mm, finished coordinates) -----------------------------------------------------
M = opt('M', 5.0)                         # the one margin (was 4.2: a 1.5 mm cut drift now reads 3.5 / 6.5, not 2.7 / 5.7)
MOON_D = opt('MOON_D', 16.6)              # 16.6: the code plus 2 quiet modules, corners included (16.33 mm diagonal), fits in the disc
MOON_MOD = 0.35
MOON_R = MOON_D / 2
MOON_X = 60 - M - MOON_R                  # moon tangent to the margin on the right ...
MOON_Y = M + MOON_R                       # ... and on the top, level with the amber cap
U1 = (MOON_X - M) / 13.0                  # pill radius: 5 pills of 2u with 4 gaps of u put the
BW = 2 * U1                               #   blue axis (M + 13u) exactly under the moon
PITCH = 3 * U1                            # width / pitch = 0.667 (the icon: 19 / 28.75 = 0.66)
X0 = M
TOP = M
AX = [X0 + U1 + i * PITCH for i in range(5)]
# v2 solved the horizon from "pink cap clears the moon by one gap u" and got 7.5 mm of water, too short to
# carry the reflections. The horizon is now chosen (9 mm of water) and the clearance is reported instead.
HORIZON = opt('HORIZON', 51.0)
H = HORIZON - TOP
TOPS = [HORIZON - H * v for v in FADER_LEVELS]
PINK_GAP = math.hypot(MOON_X - AX[3], MOON_Y - (TOPS[3] + U1)) - MOON_R - U1
YH = P(HORIZON)
SINK = opt('SINK', 0.55)                  # the capsules dip a toe: the round foot of the icon's pill stays
FIG_H = opt('FIG_H', 7.0)                 # the columns are 6.6 people tall
POSE = os.environ.get('POSE', 'B')
FINDERS_ROUND = os.environ.get('FINDERS', 'round') != 'square'   # round = the kit's default (FINDER_A = 0.8 modules)

# ---- colour ----------------------------------------------------------------------------------
def _lab(hx):
    r, g, b = (int(hx[j:j + 2], 16) / 255 for j in (1, 3, 5))
    r, g, b = ((c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for c in (r, g, b))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047; y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    fx, fy, fz = ((t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116) for t in (x, y, z))
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)

def _hex(L_, a_, b_):
    fy = (L_ + 16) / 116; fx = fy + a_ / 500; fz = fy - b_ / 200
    x, y, z = ((t ** 3 if t ** 3 > 0.008856 else (t - 16 / 116) / 7.787) for t in (fx, fy, fz))
    x *= 0.95047; z *= 1.08883
    r = 3.2406 * x - 1.5372 * y - 0.4986 * z; g = -0.9689 * x + 1.8758 * y + 0.0415 * z; b = 0.0557 * x - 0.2040 * y + 1.0570 * z
    out = []
    for c in (r, g, b):
        c = 12.92 * c if c <= 0.0031308 else 1.055 * max(c, 0) ** (1 / 2.4) - 0.055
        out.append(min(255, max(0, round(c * 255))))
    return '#%02x%02x%02x' % tuple(out)

def tune(hx, dL=0.0, chroma=1.0):
    """Shift a colour in CIE Lab: lightness by dL points, chroma by a factor."""
    L_, a_, b_ = _lab(hx)
    return _hex(L_ + dL, a_ * chroma, b_ * chroma)

def mixc(c1, c2, t):
    """Mix two colours in Lab."""
    a_, b_ = _lab(c1), _lab(c2)
    return _hex(*(a_[i] + (b_[i] - a_[i]) * t for i in range(3)))

SKY = '#05060a'
GROUND = '#030407'
FIGURE = '#060505'
# the four that are off: the icon's hues at dusk level. v2 = icon x 0.72 x 1.08. The CMYK proof takes them
# down again (pink most), so each is lifted in L* with a little more chroma (dL, chroma per column below).
# Grey is rebuilt as a near-neutral grey: v2's warm grey plus the amber kick printed as khaki.
_V2 = [('#ada8a1', '#7f7c77'), None, ('#87c397', '#5d9a70'), ('#d995a7', '#ad6d81'), ('#769bd5', '#597ab3')]
_DL = [opt('DL0', 5.0), 0, opt('DL2', 4.0), opt('DL3', 5.8), opt('DL4', 5.0)]
_CH = [opt('CH0', 0.30), 0, opt('CH2', 1.10), opt('CH3', 1.12), opt('CH4', 1.10)]
BODY = [None if c is None else tuple(tune(h, _DL[i], _CH[i]) for h in c) for i, c in enumerate(_V2)]
# what the amber light looks like where it lands on each of them (light colour x surface colour)
KICKC = [os.environ.get('KICK0C', '#f8a35a'), None, '#e0b750', '#ff9c66', None]
A_HOT, A_TOP, A_MID, A_BOT, A_LIMB = '#fff1c6', '#ffc24a', '#f9a326', '#f1931a', '#cc6206'
MOONLIGHT = '#cfdcf4'
# the moon: one flat ground out to 0.94 R, only the last 6 % turns away (limb). MOON=cream uses the brand cream.
_MOONS = {'cool': ('#dce1e8', '#b4bdcc'),            # a cool off-white: the same colour family as its halo, rim and glints
          'cream': (kit.CREAM, '#d0ccc3'),            # the brand cream
          'v2': ('#e4e0d6', '#c2bfb6')}               # v2's ground (a warm grey-cream, L* 88)
MOON_C, MOON_LIMB = _MOONS[os.environ.get('MOON', 'cool')]
HALO_C = '#93a4c6'


def f(v): return f'{v:.2f}'

def tube(i, extra='', grow=0.0):
    """Capsule i at its level, grown by `grow` mm on every side."""
    h = H * FADER_LEVELS[i] + SINK
    return (f'<rect x="{f(P(AX[i] - U1 - grow))}" y="{f(P(TOPS[i] - grow))}" width="{f(L(BW + 2 * grow))}" '
            f'height="{f(L(h + 2 * grow))}" rx="{f(L(U1 + grow))}" {extra}/>')

def blur(id_, mm, mm_y=None):
    sd = f(L(mm)) if mm_y is None else f'{f(L(mm))} {f(L(mm_y))}'
    return (f'<filter id="{id_}" filterUnits="userSpaceOnUse" x="-96" y="-96" width="448" height="448" '
            f'color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{sd}"/></filter>')

def lin(id_, stops, x1=0, y1=0, x2=0, y2=1, units=None):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    u = f' gradientUnits="{units}"' if units else ''
    return f'<linearGradient id="{id_}"{u} x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'

FULL = f'width="{CAN:g}" height="{CAN:g}"'


# ---- the gaffer -------------------------------------------------------------------------------
# All poses are drawn in a box 100 units tall (feet at y = 100, x = 0 under the hips). At 7.0 mm one unit is
# 0.07 mm, so 0.25 mm = 3.6 units: no limb thinner, no gap narrower (check.py measures both on the render).
_A_BODY = ('M-2.5,11.2 C-2.7,13.4 -4.8,14.6 -8.2,15.8 C-11.6,16.9 -13.6,18.6 -14.2,21.6 '
           'C-14.9,26.5 -15.3,32.0 -15.2,37.5 C-15.0,42.5 -14.4,47.0 -13.8,50.6 '
           'C-13.9,53.4 -13.4,55.8 -12.2,55.8 C-11.0,55.8 -10.7,54.0 -10.6,52.0 L-10.5,54.0 '
           'C-10.7,61.0 -10.3,67.5 -9.9,73.5 C-10.4,79.0 -10.3,85.0 -9.2,94.4 '
           'C-10.0,96.2 -11.6,97.8 -11.8,100 L-4.2,100 C-4.1,98.0 -4.5,96.4 -4.7,94.4 '
           'C-4.2,86.0 -3.6,80.0 -3.5,73.5 C-2.6,66.5 -1.4,60.0 -0.2,54.6 L0.2,54.6 '
           'C1.4,60.0 2.6,66.5 3.5,73.5 C3.6,80.0 4.2,86.0 4.7,94.4 C4.5,96.4 4.1,98.0 4.2,100 '
           'L11.8,100 C11.6,97.8 10.0,96.2 9.2,94.4 C10.3,85.0 10.4,79.0 9.9,73.5 '
           'C10.3,67.5 10.7,61.0 10.5,54.0 L10.6,49.0 C10.9,45.5 11.4,43.0 12.2,41.0 '
           'C13.6,41.6 15.4,41.4 16.6,40.2 L15.5,34.0 C15.3,29.0 14.9,25.0 14.2,21.6 '
           'C13.6,18.6 11.6,16.9 8.2,15.8 C4.8,14.6 2.7,13.4 2.5,11.2 Z')

def _pose_a():
    """v2: seen from behind, phone raised beside the shoulder. Reviewers read it as a visitor taking a picture."""
    return (f'<ellipse cx="0.2" cy="6.4" rx="4.6" ry="6.1"/><path d="{_A_BODY}"/>'
            f'<path d="M15.4,38.4 L23.4,30.6" fill="none" stroke="{FIGURE}" stroke-width="4.7" stroke-linecap="round"/>'
            f'<rect x="21.5" y="19.4" width="5.1" height="11.0" rx="0.9"/>')

# The side-on poses share one body, turned a quarter towards us so that the near shoulder and the hanging near
# arm give it the mass of v2's figure: a planted stance (the gap between the legs is open to the ground and ends
# in a round crotch of r = 2 units = 0.14 mm), a jacket, and the head tilted back.
_LEGS = ('M-9.2,50 C-9.5,58 -9.0,66 -8.6,73.5 C-9.2,80 -9.2,88 -8.6,93.6 L-10.0,96.4 L-10.0,100 L-1.6,100 '
         'C-1.6,98.2 -2.4,96.6 -4.0,95.6 L-4.3,93.6 C-3.8,87 -3.4,80 -3.1,73.5 C-2.9,68 -2.7,62.5 -2.4,58.2 '
         'A2,2 0 0 1 1.6,58.2 C1.9,62.5 2.3,68 2.7,73.5 C3.0,80 3.6,87 4.3,93.6 L3.9,96 L3.9,100 L14.2,100 '
         'C14.2,98.2 13.6,96.9 12.6,96.1 L9.0,93.4 C9.2,88 9.0,80 8.6,73.5 C8.4,66 8.0,58 7.2,50 Z')
_TORSO = ('M-6.0,13.4 C-8.8,14.8 -12.0,16.8 -13.0,21.0 C-13.9,26.5 -14.1,32.5 -13.6,38.5 C-13.3,43.5 -13.1,47.5 -13.1,51.0 '
          'C-13.2,53.6 -12.5,56.0 -11.1,56.0 C-9.9,56.0 -9.3,54.8 -9.2,53.6 L7.5,53.6 '
          'C7.6,50.4 7.1,46.8 6.9,43.2 C7.1,38.2 8.1,32 7.8,26.6 C7.6,22.4 6.2,19.4 2.7,16.0 Z')

def _head_up(tilt=-36):
    """Head in profile, tilted back: one oval whose crown-to-chin axis leans 36 degrees, on a short neck."""
    return (f'<ellipse cx="-0.9" cy="6.3" rx="4.8" ry="6.3" transform="rotate({tilt} -0.9 6.3)"/>'
            f'<path d="M-4.4,9.8 L1.7,11.4 C1.9,13.2 2.2,14.8 2.8,16.4 L-6.6,16.4 C-5.8,14.4 -5.0,12.2 -4.4,9.8 Z"/>')

def _pose_b():
    """The brief's pose. Side-on, facing into the picture: phone in front of the chest, forearm bent, head
    back, eyes on the light. Hand on the fader, eyes on the lamp: someone running it, not photographing it."""
    return (_head_up() + f'<path d="{_TORSO}"/><path d="{_LEGS}"/>'
            f'<path d="M3.0,41.0 L15.4,34.0" fill="none" stroke="{FIGURE}" stroke-width="4.9" stroke-linecap="round"/>'
            f'<rect x="-2.1" y="-10.4" width="4.2" height="11.6" rx="0.9" transform="translate(16.2 34.5) rotate(24)"/>')

def _pose_c():
    """My alternative, "bring it up": the same body, phone low in the near hand, the far hand lifted, palm up.
    Lost the comparison: at 7 mm two raised limbs read as waving."""
    return (_head_up(-40) + f'<path d="{_TORSO}"/><path d="{_LEGS}"/>'
            f'<path d="M3.0,42.0 L14.4,38.2" fill="none" stroke="{FIGURE}" stroke-width="4.9" stroke-linecap="round"/>'
            f'<rect x="-2.1" y="-10.0" width="4.2" height="11.2" rx="0.9" transform="translate(15.4 38.8) rotate(30)"/>'
            f'<path d="M1.5,22.0 L13.6,19.6 L19.0,8.6" fill="none" stroke="{FIGURE}" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<ellipse cx="20.2" cy="5.6" rx="2.5" ry="3.6" transform="rotate(24 20.2 5.6)"/>')

POSES = {'A': _pose_a, 'B': _pose_b, 'C': _pose_c}
POSE_DX = {'A': -0.2, 'B': -0.4, 'C': -0.45}      # where the hips stand relative to the amber axis, mm

def figure(cx, feet_y, height, pose=None):
    """The gaffer, feet on (cx, feet_y) mm."""
    s = L(height) / 100.0
    return (f'<g transform="translate({P(cx):.2f} {P(feet_y):.2f}) scale({s:.4f}) translate(0 -100)" fill="{FIGURE}">'
            + POSES[pose or POSE]() + '</g>')


def glints():
    """The moon on the water: a path of glints under it. v2 made them from thresholded noise, hairs of
    0.05-0.1 mm that a press drops; the first finish over-corrected with 26 hard dashes that read as a ladder,
    were the brightest marks in the lower half and ran through the cut. Now: ONE soft lens of light per row
    (an ellipse 0.19 mm thick at the horizon to 0.27 mm in front, a hair of blur so no edge is hard), about ten
    of them, small and close at the horizon, longer and further apart towards the viewer, fading as they come.
    The path ends at GEND = 57.6 mm, 2.4 mm inside the cut, so a drifted cut never slices a glint."""
    rnd = random.Random(int(opt('GSEED', 56))); s = ''
    depth = opt('GEND', 57.6) - HORIZON; y = HORIZON + 0.45
    while True:
        t = (y - HORIZON) / depth
        if t > 1: break
        th = 0.19 + 0.08 * t
        spread = 0.30 + 1.9 * t ** 0.85
        half = (0.24 + 0.58 * t) * rnd.uniform(0.55, 1.35)
        x = MOON_X + rnd.uniform(-1, 1) * spread
        op = (0.62 - 0.42 * t) * rnd.uniform(0.6, 1.0) * opt('GLINT', 0.0)
        s += (f'<ellipse cx="{f(P(x))}" cy="{f(P(y))}" rx="{f(L(half))}" ry="{f(L(th / 2))}" '
              f'fill="{MOONLIGHT}" opacity="{op:.2f}"/>')
        y += th + 0.24 + 0.42 * t + rnd.uniform(0, 0.20)
    return f'<g filter="url(#gl)">{s}</g>'


def build():
    defs = ''
    for i, c in enumerate(BODY):
        if c: defs += lin(f'pf{i}', [(0, c[0], 1), (1, c[1], 1)])
    defs += lin('amb', [(0, A_TOP, 1), (0.45, A_MID, 1), (1, A_BOT, 1)])
    # warm light arriving from the amber column, on the flank that faces it; it dies before the far side
    K = [(0, .94), (.09, .68), (.24, .32), (.42, .10), (.6, 0)]
    for i, side in ((0, +1), (2, -1), (3, -1)):
        st = [(f'{1 - o:.2f}', KICKC[i], a) for o, a in reversed(K)] if side > 0 else [(o, KICKC[i], a) for o, a in K]
        defs += lin(f'kick{i}', st, 0, 0, 1, 0)
    # and the flank that looks away from it goes down
    defs += lin('awayL', [(0, '#03040a', 1), (0.25, '#03040a', 0.5), (0.62, '#03040a', 0)], 0, 0, 1, 0)
    defs += lin('awayR', [(0.38, '#03040a', 0), (0.75, '#03040a', 0.5), (1, '#03040a', 1)], 0, 0, 1, 0)
    defs += lin('both', [(0, '#03040a', 1), (0.3, '#03040a', 0.2), (0.5, '#03040a', 0), (0.7, '#03040a', 0.2), (1, '#03040a', 1)], 0, 0, 1, 0)
    for i in range(5):
        defs += f'<clipPath id="c{i}">{tube(i)}</clipPath>'
    defs += (blur('g1', 0.5) + blur('g2', opt('G2S', 1.7)) + blur('g3', opt('G3S', 5.0)) + blur('edge', 0.6)
             + blur('core', 0.95) + blur('rimb', 0.07) + blur('soft', 1.2) + blur('gl', 0.09, 0.025))
    # pink only sees the amber column over the top of green: a long, soft penumbra down its flank
    t_g = (TOPS[2] - TOPS[3]) / (HORIZON - TOPS[3])
    defs += lin('pen', [(0, '#fff', .9), (f'{t_g:.3f}', '#fff', .62), (1, '#fff', .12)],
                0, f(P(TOPS[3])), 0, f(YH), 'userSpaceOnUse')
    defs += (f'<mask id="penm" maskUnits="userSpaceOnUse" x="0" y="0" {FULL}>'
             f'<rect x="0" y="0" {FULL} fill="url(#pen)"/></mask>')
    # moon rim: a hair of cool light on the upper-right shoulder of every cap, fading round the arc
    for i in (0, 2, 3, 4):
        rx = P(AX[i] + U1 * 0.74); ry = P(TOPS[i] + U1 - U1 * 0.74); rr = L(U1 * opt('RIMR', 1.4))
        defs += (f'<radialGradient id="rim{i}" gradientUnits="userSpaceOnUse" cx="{f(rx)}" cy="{f(ry)}" r="{f(rr)}">'
                 f'<stop offset="0" stop-color="{MOONLIGHT}" stop-opacity="1"/>'
                 f'<stop offset=".45" stop-color="{MOONLIGHT}" stop-opacity=".55"/>'
                 f'<stop offset="1" stop-color="{MOONLIGHT}" stop-opacity="0"/></radialGradient>')
    # reflections: near the horizon almost a mirror, further out streaked and broken by ripples
    RIP = opt('RIPPLE', 7)
    defs += blur('rfA', 0.12, 0.5)
    defs += ('<filter id="rfB" filterUnits="userSpaceOnUse" x="-96" y="-96" width="448" height="448" '
             'color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="1.1 7" result="s"/>'
             '<feTurbulence type="fractalNoise" baseFrequency="0.006 0.45" numOctaves="2" seed="4" result="t"/>'
             f'<feDisplacementMap in="s" in2="t" scale="{RIP}" xChannelSelector="R" yChannelSelector="G" result="d"/>'
             '<feGaussianBlur in="d" stdDeviation="0.5 0.35"/></filter>')
    defs += f'<clipPath id="gclip"><rect x="-10" y="{f(YH)}" width="{CAN + 20}" height="{CAN}"/></clipPath>'
    defs += (lin('mA', [(0, '#fff', .82), (1, '#fff', 0)], 0, f(YH), 0, f(YH + L(opt('MIRROR', 6.6))), 'userSpaceOnUse')
             + f'<mask id="maskA" maskUnits="userSpaceOnUse" x="-10" y="0" width="{CAN + 20}" height="{CAN + 20}">'
               f'<rect x="-10" y="{f(YH)}" width="{CAN + 20}" height="{CAN}" fill="url(#mA)"/></mask>')
    defs += (lin('mB', [(0, '#fff', 0), (.4, '#fff', .55), (1, '#fff', .4)], 0, f(YH), 0, CAN, 'userSpaceOnUse')
             + f'<mask id="maskB" maskUnits="userSpaceOnUse" x="-10" y="0" width="{CAN + 20}" height="{CAN + 20}">'
               f'<rect x="-10" y="{f(YH)}" width="{CAN + 20}" height="{CAN}" fill="url(#mB)"/></mask>')
    # light lying on the wet ground: a sliver along the horizon, strongest at the foot of the column
    defs += ('<radialGradient id="sliver"><stop offset="0" stop-color="#fff" stop-opacity="1"/>'
             '<stop offset=".3" stop-color="#fff" stop-opacity=".5"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
             '</radialGradient><mask id="slm" maskContentUnits="objectBoundingBox"><rect width="1" height="1" fill="url(#sliver)"/></mask>')
    # moon: one flat ground out to 0.94 R; only the outer 6 % darkens (limb). Around it a cool halo in two
    # parts: a tight corona that still separates from the sky after the press has crushed the darks, and a
    # wide, faint aureole. Opacities are set on the CMYK proof, not on screen (halos fade in print).
    R = L(MOON_R); mx = P(MOON_X); my = P(MOON_Y); HR = R * opt('HALO_R', 2.1)
    HALO = opt('HALO', .30)
    q = R / HR
    hs = [(q, HALO), (q + (1 - q) * .07, HALO * .66), (q + (1 - q) * .2, HALO * opt('HALO_S2', .45)),
          (q + (1 - q) * .45, HALO * opt('HALO_S3', .24)), (q + (1 - q) * .72, HALO * .04), (1, 0)]
    defs += (f'<radialGradient id="halo" gradientUnits="userSpaceOnUse" cx="{mx}" cy="{my}" r="{HR:.2f}">'
             + ''.join(f'<stop offset="{o:.3f}" stop-color="{HALO_C}" stop-opacity="{a_:.3f}"/>' for o, a_ in hs)
             + '</radialGradient>'
             f'<radialGradient id="moon" gradientUnits="userSpaceOnUse" cx="{mx}" cy="{my}" r="{R:.2f}">'
             f'<stop offset="0" stop-color="{MOON_C}"/><stop offset=".94" stop-color="{MOON_C}"/>'
             + ''.join(f'<stop offset="{o}" stop-color="{mixc(MOON_C, MOON_LIMB, t)}"/>' for o, t in ((.97, .10), (.988, .36), (1, 1)))
             + '</radialGradient>')
    # film grain, weighted to the shadows (amplitude ~ 1 - 0.65 x value): it dithers the dark falloffs
    # for the press and leaves the bright faces almost clean. out = S + a (n - .5)(1 - .65 S)
    # (two noise fields with different, anisotropic lattices are averaged so no grid shows; the filter is
    # applied unrotated on purpose: a rotated filter group makes the browser resample the whole picture)
    a = opt('GRAIN', 0.105); gw = opt('GRW', 0.8)
    defs += (f'<filter id="grain" filterUnits="userSpaceOnUse" x="-4" y="-4" width="264" height="264" color-interpolation-filters="sRGB">'
             '<feTurbulence type="fractalNoise" baseFrequency="1.9 1.55" numOctaves="2" seed="11" result="t1"/>'
             '<feTurbulence type="fractalNoise" baseFrequency="1.27 2.1" numOctaves="2" seed="5" result="t2"/>'
             '<feComposite in="t1" in2="t2" operator="arithmetic" k1="0" k2="0.5" k3="0.5" k4="0" result="t"/>'
             '<feColorMatrix in="t" type="matrix" values="1 0 0 0 0  1 0 0 0 0  1 0 0 0 0  0 0 0 0 1" result="n"/>'
             f'<feComposite in="SourceGraphic" in2="n" operator="arithmetic" k1="{-gw * a:.4f}" '
             f'k2="{1 + 0.5 * gw * a:.4f}" k3="{a:.4f}" k4="{-0.5 * a:.4f}"/></filter>')
    # ---- the scene above the horizon (reused, mirrored, as the reflection) ---------------------
    sc = ''
    # the key: tight bloom on the lens, near spill, then a short haze that is gone 8 mm out
    sc += (tube(1, f'fill="#ffb24a" opacity="{opt("G1", .9)}" filter="url(#g1)"', 0.25)
           + tube(1, f'fill="#f38a22" opacity="{opt("G2", .56)}" filter="url(#g2)"', 0.8)
           + tube(1, f'fill="#c65a0c" opacity="{opt("G3", .36)}" filter="url(#g3)"', 1.6))

    def unlit(i, side, k=1.0, pen=False, rim=1.0):
        """A column that is off. side: -1 = the key is on its left, +1 = on its right, 0 = it sees none."""
        s = tube(i, f'fill="url(#pf{i})"')
        # a capsule, not a flat pill: the limb turns away
        s += tube(i, f'fill="none" stroke="#070506" stroke-width="{f(L(1.7))}" opacity="{opt("ROUND", .2)}" filter="url(#edge)"')
        if side:
            aw = 'awayR' if side < 0 else 'awayL'
            s += tube(i, f'fill="url(#{aw})" opacity="{opt("SHADE", .5)}"')
            kick = tube(i, f'fill="url(#kick{i})" opacity="{k}"')
            if pen: kick = f'<g mask="url(#penm)">{kick}</g>'
            s += kick
        else:
            s += tube(i, f'fill="url(#both)" opacity="{opt("SHADE0", .3)}"')
        # the moon is high, behind and to the right
        s += (f'<g style="mix-blend-mode:screen" opacity="{rim}">'
              + tube(i, f'fill="none" stroke="url(#rim{i})" stroke-width="{f(L(opt("RIMW", .76)))}" filter="url(#rimb)"') + '</g>')
        return f'<g clip-path="url(#c{i})">{s}</g>'

    KICK = opt('KICK', 1.0)
    sc += unlit(0, +1, KICK, rim=.55)
    sc += unlit(2, -1, KICK, rim=.9)
    sc += unlit(3, -1, KICK * opt('KICK3', .85), pen=True)
    sc += unlit(4, 0)
    # the lit column: saturated at the limb, hot along its axis (print has only lightness to say "on")
    sc += (f'<g clip-path="url(#c1)">' + tube(1, 'fill="url(#amb)"')
           + tube(1, f'fill="none" stroke="{A_LIMB}" stroke-width="{f(L(0.9))}" opacity=".5" filter="url(#edge)"')
           + f'<g style="mix-blend-mode:screen">' + tube(1, f'fill="{A_HOT}" opacity="{opt("CORE", .64)}" filter="url(#core)"', -2.0)
           + '</g></g>')
    fig = figure(AX[1] + opt('FIG_DX', POSE_DX[POSE]), HORIZON, FIG_H) if FIGURE_ON else ''
    scene = f'<g id="scene">{sc}{fig}</g>'

    art = f'<rect x="-4" y="-4" width="{CAN + 8:g}" height="{CAN + 8:g}" fill="{SKY}"/>'
    art += f'<circle cx="{mx}" cy="{my}" r="{HR:.2f}" fill="url(#halo)"/>'
    art += scene
    # wet ground
    art += f'<rect x="-4" y="{f(YH)}" width="{CAN + 8:g}" height="{CAN - YH + 4:.2f}" fill="{GROUND}"/>'
    mirror = f'<use href="#scene" transform="translate(0 {2 * YH:.2f}) scale(1 -1)"/>'
    art += f'<g clip-path="url(#gclip)"><g mask="url(#maskA)"><g filter="url(#rfA)">{mirror}</g></g></g>'
    art += f'<g clip-path="url(#gclip)"><g mask="url(#maskB)"><g filter="url(#rfB)">{mirror}</g></g></g>'
    # the key grazes the water: a long sliver along the horizon
    cxp = P(AX[1]); rx, ry = L(opt('SLIVER', 21)), L(0.5)
    art += (f'<rect x="{cxp - rx:.2f}" y="{YH - ry:.2f}" width="{2 * rx:.2f}" height="{2 * ry:.2f}" fill="#ffab2e" '
            f'opacity=".85" mask="url(#slm)"/>')
    # ... and the moon grazes it too: a cool hair of light on the horizon under it, then broken glints
    rx2, ry2 = L(opt('MSLIVER', 11)), L(0.3)
    art += (f'<rect x="{mx - rx2:.2f}" y="{YH - ry2:.2f}" width="{2 * rx2:.2f}" height="{2 * ry2:.2f}" fill="{MOONLIGHT}" '
            f'opacity="{opt("MSLIVER_OP", .7)}" mask="url(#slm)"/>')
    art += glints()
    # grain over the whole photograph; then the moon, kept clean for the scanner
    art = f'<g filter="url(#grain)">{art}</g>'
    art += f'<circle cx="{mx}" cy="{my}" r="{R:.2f}" fill="url(#moon)"/>'

    fg, n = kit.qr_round(MOON_X, MOON_Y, MOON_D, MOON_MOD, fill=0.0, rounded_finders=FINDERS_ROUND)
    return art, fg, defs


if __name__ == '__main__':
    art, fg, defs = build()
    kit.save(OUT, art, fg, defs)
    rep = kit.preview(OUT)
    print(json.dumps(rep))
    print(f'M {M}  u {U1:.3f}  pill {BW:.2f}  pitch {PITCH:.2f}  horizon {HORIZON:.2f} (water {60 - HORIZON:.2f})  H {H:.2f}  '
          f'tops {[round(t, 2) for t in TOPS]}  moon d {MOON_D} at ({MOON_X:.2f}, {MOON_Y:.2f})  pink-moon gap {PINK_GAP:.2f} '
          f'({PINK_GAP / U1:.2f} u)  axes {[round(a, 2) for a in AX]}  pose {POSE} {FIG_H} mm')
