"""Kanau sticker, direction A, final: "One lamp on".

Idea: one light. The icon is five real tubes in a dark room and only the amber one is on; every
other thing on the sticker (four unlit tubes, their empty glass, the QR disc) is seen by that
light and carries its reflection on the side that faces it. No text anywhere.

Layers: art.svg = everything pictorial, including the disc under the code (rasterised for print);
        fg.svg  = the QR modules and finders only, flat kit.QR_INK.

Run: python3 make.py            regenerates art.svg / fg.svg / full.svg / guides.svg and all previews here
     python3 make.py <dir> k=v  writes a variant into ./<dir> (used while comparing options)
Print file, in this order:
     python3 ../../prod/produce.py <this folder> <this folder>/print/kanau-sticker-lit-icon
     python3 _postpress.py      page boxes to 0,0, the checks again on the final PDF, both proofs
     python3 _compare.py        compare.png
"""
import os, sys, math, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kit'))
import kit
from kit import P, L, CAN

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
OPT = dict(word=0.0,        # the final carries no text; 1 brings back the old lamp stamp (not approved)
           far=0.44,        # how far the unlit tubes fall off on the side away from the light
           round=0.15, kiss=0.74, kiss_w=0.85, wrap=0.24,
           g1=0.92, g2=0.70, g3=0.46, gs=0.30, core=0.92,
           spec=0.85, spec2=0.22, spec_w=0.38,       # reflection line in the glass: strength, second line, width mm
           grain=1.0,                                # scale of the film grain inside the glow
           blue_far=0.74, blue_amb=0.24,                # blue: far-side falloff and the soft light on its lamp side
           rimdark=1.0,
           finder=0.0, eye=0.4,                      # QR finders: outer corner radius and eye radius, in modules
           glassfar=1.0,                             # 1: tracks 4 and 5 use GLASS_FAR (press insurance), 0: GLASS everywhere
           disc=0.0)                                 # test only: 0 = the approved disc, 1 = the lighter ground the print check tried
for a in sys.argv[1:]:
    if '=' in a:
        k, v = a.split('='); OPT[k] = float(v)
    else:
        OUT = os.path.join(HERE, a)

# ---- geometry (mm, measured from the finished top-left corner) ------------------------------
M = 5.0                       # margin of the fader bank
BANK = 60 - 2 * M             # 50: the bank is a square, like the icon's
RATIO = 0.66                  # pill width / pitch: the icon's own ratio (19 / 28.75)
PITCH = BANK / (4 + RATIO)
W = PITCH * RATIO
R = W / 2
TOP, BOT = M, 60 - M
H = BOT - TOP
AX = [M + R + i * PITCH for i in range(5)]          # tube centre lines (the middle one is x = 30)
# levels: grey and pink are the icon's (74/135, 92/135). Blue is lifted from 0.30 to 0.385 so that
# a full cap of it stands above the badge, and green by 0.013 to keep its distance from blue.
LEVELS = [74 / 135, 1.0, 0.45, 92 / 135, 0.385]
TOPS = [BOT - H * v for v in LEVELS]

# QR badge: a 16.8 mm disc standing one cap radius (3.54 mm) in from the right and bottom cut.
# The code is 29 x 29 modules of 0.35 mm; its 2-module quiet zone is a 11.55 mm square whose
# corners lie 8.167 mm from the centre. The rim shading is the outer 0.18 mm of the disc
# (8.22 .. 8.40 mm), so it stays out of the quiet zone even at the corners.
D = 16.8
RIM = 0.18
QM = 0.35
NQ = 29
CX = CY = 60 - R - D / 2
QUIET = (NQ / 2 + 2) * QM                        # half side of code + quiet zone
assert 60 - CX - D / 2 >= 3.5, 'disc too close to the cut'
assert QUIET * math.sqrt(2) < D / 2 - RIM, 'rim reaches into the quiet zone'

# ---- colour ---------------------------------------------------------------------------------
BG = '#070709'
# empty glass, edge to axis: one tone for all five. Lifted 14 levels from v2 so that tracks 4
# and 5, which get no light from the lamp, still separate from the wall after the CMYK conversion.
GLASS = ['#414045', '#353439', '#2e2d30']
# Tracks 4 and 5 stand outside the lamp's light, so their glass is the weakest thing in the print:
# it is separated from the wall by the black plate alone. They get 6 levels more than the others.
# Tracks 1-3 stay as they are (they also take the amber glow and went grey-brown when lifted).
GLASS_FAR = ['#47464b', '#3b3a3f', '#343336']
# unlit tubes (top, bottom). Grey is a neutral warm grey (R-B 8, no yellow); green, pink and blue
# are 6-8 % lighter in their lit halves than v2 and slightly more saturated.
PILL = [('#dddad7', '#b9b6b3'), None, ('#bbeac3', '#93d0a3'), ('#fdccd6', '#eea6b7'), ('#a6c9fa', '#8aacdf')]
A_TOP, A_MID, A_BOT, A_LIMB, A_HOT = '#ffc04a', '#f8a42a', '#ee9118', '#d96706', '#fff6dc'
SPILL = '#ffa646'             # the amber light where it lands on something
KISS = '#ffc47a'              # its reflection on a glossy flank
SHADE = '#07060a'
AMBIENT = '#d2e3ff'           # what reaches the blue tube, which stands in pink's shadow
# the disc: warm white card. Lit from the lamp (upper left), 17 levels of luminance rim to rim.
DISC_LIT, DISC_FAR = '#e0d9cf', '#cbc8c4'
def _mix(a, b, t):
    A = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; B = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(A, B))
if OPT['disc'] > 0:           # towards '#ece8e2' / '#e0dedc' (ground L 222-233), which the print check tried for glare
    DISC_LIT, DISC_FAR = _mix(DISC_LIT, '#ece8e2', OPT['disc']), _mix(DISC_FAR, '#e0dedc', OPT['disc'])

def f(v): return f'{v:.2f}'
def pill(x, y, w, h, extra=''):
    return (f'<rect x="{f(P(x))}" y="{f(P(y))}" width="{f(L(w))}" height="{f(L(h))}" '
            f'rx="{f(L(w / 2))}" {extra}/>')
def tube(i, extra='', grow=0.0):
    """Pill i at its level; grow widens it on every side (mm)."""
    return pill(AX[i] - R - grow, TOPS[i] - grow, W + 2 * grow, BOT - TOPS[i] + 2 * grow, extra)
def track(i, extra='', grow=0.0):
    return pill(AX[i] - R - grow, TOP - grow, W + 2 * grow, H + 2 * grow, extra)
def blur(id_, mm):
    return (f'<filter id="{id_}" filterUnits="userSpaceOnUse" x="-40" y="-80" width="{CAN + 80:g}" '
            f'height="{CAN + 160:g}" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{f(L(mm))}"/></filter>')
def lin(id_, stops, x1=0, y1=0, x2=0, y2=1, user=False):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    u = ' gradientUnits="userSpaceOnUse"' if user else ''
    return f'<linearGradient id="{id_}"{u} x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'
def vmask(id_, stops):
    """Mask that varies only with height. stops: (y mm, opacity)."""
    y0, y1 = stops[0][0], stops[-1][0]
    g = lin(id_ + 'g', [(f'{(y - y0) / (y1 - y0):.3f}', '#fff', a) for y, a in stops], 0, f(P(y0)), 0, f(P(y1)), user=True)
    return g + (f'<mask id="{id_}" maskUnits="userSpaceOnUse" x="0" y="-80" width="{CAN:g}" height="{CAN + 160:g}">'
                f'<rect x="0" y="-80" width="{CAN:g}" height="{CAN + 160:g}" fill="url(#{id_}g)"/></mask>')
FULL = f'width="{CAN:g}" height="{CAN:g}"'

# ---- defs -----------------------------------------------------------------------------------
defs = ''
for i, c in enumerate(PILL):
    if c: defs += lin(f'p{i}', [(0, c[0], 1), (1, c[1], 1)])
defs += lin('amb', [(0, A_TOP, 1), (0.5, A_MID, 1), (1, A_BOT, 1)])
for gid, G in (('glass', GLASS), ('glassfar', GLASS_FAR)):
    defs += lin(gid, [(0, G[0], 1), (0.2, G[1], 1), (0.5, G[2], 1), (0.8, G[1], 1), (1, G[0], 1)], 0, 0, 1, 0)
# light arriving from the amber tube. L = it comes from the left (green, pink, blue), R = from the right (grey)
#  kiss: the narrow hot band on the flank that faces the tube;  wrap: the little that creeps round;
#  far: the side that faces away falls off;  spec: the tube's reflection as a line in empty glass
defs += lin('kissL', [(0, KISS, 1), (0.20, KISS, 0.8), (0.46, KISS, 0)], 0, 0, 1, 0)
defs += lin('kissR', [(0.54, KISS, 0), (0.80, KISS, 0.8), (1, KISS, 1)], 0, 0, 1, 0)
defs += lin('wrapL', [(0, SPILL, 1), (0.14, SPILL, 0.45), (0.34, SPILL, 0.10), (0.5, SPILL, 0)], 0, 0, 1, 0)
defs += lin('wrapR', [(0.5, SPILL, 0), (0.66, SPILL, 0.10), (0.86, SPILL, 0.45), (1, SPILL, 1)], 0, 0, 1, 0)
defs += lin('farL', [(0.10, SHADE, 0), (0.55, SHADE, 0.46), (0.88, SHADE, 0.88), (1, SHADE, 1)], 0, 0, 1, 0)
defs += lin('farR', [(0, SHADE, 1), (0.12, SHADE, 0.88), (0.45, SHADE, 0.46), (0.90, SHADE, 0)], 0, 0, 1, 0)
# blue only: the soft light that finds its lamp-side flank (no direct light reaches it)
defs += lin('ambL', [(0, AMBIENT, 0.55), (0.13, AMBIENT, 1), (0.34, AMBIENT, 0.5), (0.62, AMBIENT, 0)], 0, 0, 1, 0)
defs += lin('shR', [(0, '#000', 1), (0.5, '#000', 0.8), (1, '#000', 0)], 0, 0, 1, 0)
defs += lin('shL', [(0, '#000', 0), (0.5, '#000', 0.8), (1, '#000', 1)], 0, 0, 1, 0)
for i in range(5):
    defs += f'<clipPath id="c{i}">{tube(i)}</clipPath><clipPath id="t{i}">{track(i)}</clipPath>'
defs += f'<clipPath id="slots">{"".join(track(i) for i in (0, 2, 3, 4))}</clipPath>'
defs += f'<clipPath id="disc"><circle cx="{f(P(CX))}" cy="{f(P(CY))}" r="{f(L(D / 2))}"/></clipPath>'
defs += blur('g1', 0.55) + blur('g2', 2.0) + blur('g3', 8.0) + blur('edge', 0.6)
defs += blur('sh', 1.2) + blur('soft', 1.4) + blur('b06', 0.06) + blur('b10', 0.10) + blur('b40', 0.40) + blur('core', 0.85)
# Film grain inside the light only: its one job is to stop the long amber falloff from banding on
# press. It is made of single-octave noise layers at unequal, anisotropic frequencies, each on its
# own rotated grid, so that no lattice lines up with the pixel grid or with another layer (the old
# grain was one octave with 0.10 mm cells, 2 px at 1200 ppi: under-sampled, hence the weave). Cells
# are 0.14-0.30 mm here, 3.3-7 px at 600 dpi. All layers only take light away:
#   GRAIN  three layers over the whole glow, 2 % of the light. Their mean (18 % together) is the
#          old grain's, so the bloom and the falloff keep their level.
#   FAR    three layers on the long falloff alone (the 8 mm blur), 6 % of that light, which is what
#          the old grain gave it. Beside the tube this layer is a fifth of the light, so the grain
#          there comes to 2-2.5 levels; far out, where the gradient is slowest, it keeps the dither.
GRAIN = [('grainA', 1.07, 0.83, 11, 33, 0.064), ('grainB', 1.61, 1.27, 47, -21, 0.106), ('grainC', 1.37, 1.83, 5, 58, 0.085)]
FAR = [('grainF', 1.31, 1.71, 23, 17, 0.23), ('grainG', 1.57, 1.19, 71, -38, 0.23), ('grainH', 1.13, 1.47, 37, 74, 0.23)]
GM = 1 - (1 - 0.18) ** (1 / len(GRAIN))
FM = 0.12                     # mean of one FAR layer
GX = 70                       # the grain rectangles overshoot the canvas so that they cover it when rotated
GBOX = f'x="{-GX}" y="{-GX}" width="{CAN + 2 * GX:g}" height="{CAN + 2 * GX:g}"'
for (id_, fx, fy, seed, rot, amp), mean in [(g, GM) for g in GRAIN] + [(g, FM) for g in FAR]:
    amp *= OPT['grain']
    defs += (f'<filter id="{id_}" filterUnits="userSpaceOnUse" {GBOX} color-interpolation-filters="sRGB">'
             f'<feTurbulence type="fractalNoise" baseFrequency="{fx} {fy}" numOctaves="1" seed="{seed}"/>'
             f'<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  {amp:.4f} {amp:.4f} 0 0 {mean - amp:.4f}"/></filter>')
def grain_rects(layers):
    return ''.join(f'<rect {GBOX} fill="#000" filter="url(#{id_})" transform="rotate({rot} {CAN / 2:g} {CAN / 2:g})"/>'
                   for id_, fx, fy, seed, rot, amp in layers)
defs += f'<mask id="fargrain" maskUnits="userSpaceOnUse" {GBOX}><rect {GBOX} fill="#fff"/>{grain_rects(FAR)}</mask>'
# what each tube can see of the lit one past the tubes standing in between (long soft penumbras,
# because the source is as tall as the whole bank)
defs += vmask('occ3', [(TOPS[3] - 4, 1), (TOPS[3] + 3, 1), (TOPS[2] + 4, 0.5), (BOT - 4, 0.08), (BOT, 0)])
defs += vmask('spectop', [(TOP + R * 0.45, 0), (TOP + R * 1.5, 1), (BOT, 1)])
defs += vmask('occ4', [(TOP + R * 0.45, 0), (TOP + R * 1.5, 1), (TOPS[3] - 6, 1), (TOPS[3] + 8, 0)])
defs += vmask('foot', [(TOP - 20, 1), (BOT - R * 1.1, 1), (BOT - R * 0.1, 0.15), (BOT, 0)])
# the disc: lit from the upper left, where the amber tube is
ux, uy = -0.80, -0.60
def across(id_, stops):
    return lin(id_, stops, f(P(CX + ux * D / 2)), f(P(CY + uy * D / 2)), f(P(CX - ux * D / 2)), f(P(CY - uy * D / 2)), user=True)
defs += across('discfill', [(0, DISC_LIT, 1), (1, DISC_FAR, 1)])
defs += across('rimlit', [(0, '#ffb45a', 1), (0.16, '#ffc47c', 0.75), (0.42, '#ffd9a8', 0)])
defs += across('rimdark', [(0.5, '#6f685c', 0), (0.86, '#6f685c', 0.55), (1, '#6f685c', 0.8)])

# ---- art ------------------------------------------------------------------------------------
art = f'<rect {FULL} fill="{BG}"/>'

# empty glass: one tone for the three tracks in the lamp's light, a slightly lighter one for the two beyond it
for i in range(5):
    art += track(i, f'fill="url(#{"glassfar" if i >= 3 and OPT["glassfar"] > 0 else "glass"})"')

# the amber tube lights the room: tight bloom, near spill, then a long falloff.
# The neighbours stand in that light: behind grey (to its left) and behind green (to its right)
# the wall is in shadow below their tops, and the light carries on over them.
def shadow(i, side):
    wd = 14.0
    x = AX[i] - R * 0.3 if side > 0 else AX[i] + R * 0.3 - wd
    g = 'shR' if side > 0 else 'shL'
    return (f'<rect x="{f(P(x))}" y="{f(P(TOPS[i] + R * 0.8))}" width="{f(L(wd))}" height="{f(L(BOT - TOPS[i] + 10))}" '
            f'fill="url(#{g})" filter="url(#soft)"/>')
glow = (tube(1, f'fill="#ffb14a" opacity="{OPT["g1"]}" filter="url(#g1)"', 0.3)
        + tube(1, f'fill="#f38a22" opacity="{OPT["g2"]}" filter="url(#g2)"', 1.0)
        + '<g mask="url(#fargrain)">'          # the mask passes (1 - FM)^3 of it on average: given back in the opacity
        + tube(1, f'fill="#cf5f0c" opacity="{OPT["g3"] / (1 - FM) ** len(FAR):.4f}" filter="url(#g3)"', 2.5) + '</g>'
        + shadow(0, -1) + shadow(2, +1)
        + grain_rects(GRAIN))
art += f'<g style="mix-blend-mode:screen">{glow}</g>'
# glass takes more of the same light than the black wall behind it
art += f'<g clip-path="url(#slots)"><g style="mix-blend-mode:screen" opacity="{OPT["gs"]}">{glow}</g></g>'

# the reflection of the lit tube in the empty glass: one line on the side that faces it, curling
# over the cap and dying; weaker with distance (1, 1, 1/2, 1/4). 0.38 mm wide with soft edges.
def spec(i, side, k, mask='spectop', inset=0.82, second=True):
    # side: which side of tube i looks at the lit one. The second, fainter line (tracks 1 and 3
    # only) is the same light coming back off the inside of the far wall.
    w = OPT['spec_w']
    x1 = AX[i] + side * (R - inset) - w / 2
    x2 = AX[i] - side * (R - inset * 1.25) - 0.09
    hh = TOPS[i] + R - TOP        # it carries on behind the coloured part
    s = (f'<rect x="{f(P(x1))}" y="{f(P(TOP))}" width="{f(L(w))}" height="{f(L(hh))}" fill="#ffbd70" filter="url(#b06)"/>')
    if second and OPT['spec2'] > 0:
        s += (f'<rect x="{f(P(x2))}" y="{f(P(TOP))}" width="{f(L(0.18))}" height="{f(L(hh))}" fill="#ffbd70" '
              f'opacity="{OPT["spec2"]}" filter="url(#b10)"/>')
    return f'<g style="mix-blend-mode:screen" opacity="{k * OPT["spec"]:.3f}" mask="url(#{mask})">{s}</g>'
art += (spec(0, +1, 1.0) + spec(2, -1, 1.0) + spec(3, -1, 0.50, second=False)
        + spec(4, -1, 0.26, 'occ4', second=False))

# unlit tubes: their own colour, then the light they catch from the amber one.
# side -1: the light comes from the left. k: how much of it reaches this tube.
def unlit(i, side, k, dim=0.0, mask=None, far_k=1.0, amb=0.0):
    kiss, wrap, far = ('kissL', 'wrapL', 'farL') if side < 0 else ('kissR', 'wrapR', 'farR')
    s = tube(i, f'fill="url(#p{i})"')
    if dim: s += tube(i, f'fill="{SHADE}" opacity="{dim}"')                      # further from the light
    s += tube(i, f'fill="url(#{far})" opacity="{OPT["far"] * far_k:.3f}"')       # the side that looks away
    s += (f'<g clip-path="url(#c{i})">' + tube(i, f'fill="none" stroke="#120e0c" stroke-width="{f(L(1.5))}" '
          f'opacity="{OPT["round"]}" filter="url(#edge)"') + '</g>')            # it is round
    if amb > 0:
        s += (f'<g clip-path="url(#c{i})" style="mix-blend-mode:screen" mask="url(#foot)">'
              + tube(i, f'fill="url(#ambL)" opacity="{amb:.3f}"') + '</g>')
    if k > 0:
        m = f' mask="url(#{mask or "foot"})"'
        # the wrap lifts the tube's own colour; the kiss is the lamp's colour, the same on every tube
        s += (f'<g clip-path="url(#c{i})" style="mix-blend-mode:screen" opacity="{k:.3f}"{m}>'
              + tube(i, f'fill="url(#{wrap})" opacity="{OPT["wrap"]}"') + '</g>')
        s += (f'<g clip-path="url(#c{i})" opacity="{k ** 0.6:.3f}"{m}>'
              + tube(i, f'fill="none" stroke="url(#{kiss})" stroke-width="{f(L(OPT["kiss_w"] * 2))}" opacity="{OPT["kiss"]}" '
                        f'filter="url(#b40)"') + '</g>')
    return s
art += unlit(0, +1, 1.0)
art += unlit(2, -1, 1.0)
art += unlit(3, -1, 0.50, mask='occ3', far_k=0.85)     # pink sees the amber tube over the top of green
# blue stands in pink's shadow: no kiss from the lamp, but the same side modelling as the others
art += unlit(4, -1, 0.0, far_k=OPT['blue_far'], amb=OPT['blue_amb'])

# the lit tube: saturated at the limb, clipped to near white along its axis
art += tube(1, 'fill="url(#amb)"')
art += (f'<g clip-path="url(#c1)">'
        + tube(1, f'fill="none" stroke="{A_LIMB}" stroke-width="{f(L(1.1))}" opacity=".55" filter="url(#edge)"')
        + '</g>')
art += (f'<g clip-path="url(#c1)" style="mix-blend-mode:screen">'
        + tube(1, f'fill="{A_HOT}" opacity="{OPT["core"]}" filter="url(#core)"', -2.15) + '</g>')

# badge: a disc of warm white card standing in front of pink and blue, in the same light as
# everything else. Tight contact shadow, even ground under the code, rim shading outside the quiet
# zone. It is opaque: a see-through tint of the tubes behind it was tried again in the outer band
# only and read as stains, so there is none.
art += (f'<circle cx="{f(P(CX + 0.30))}" cy="{f(P(CY + 0.36))}" r="{f(L(D / 2 + 0.15))}" fill="#000" '
        f'opacity=".85" filter="url(#sh)"/>')
art += f'<circle cx="{f(P(CX))}" cy="{f(P(CY))}" r="{f(L(D / 2))}" fill="url(#discfill)"/>'
# its edge: warm where it looks at the tube, in shade where it looks away
art += (f'<circle cx="{f(P(CX))}" cy="{f(P(CY))}" r="{f(L(D / 2 - RIM / 2))}" fill="none" stroke="url(#rimdark)" '
        f'stroke-width="{f(L(RIM))}" opacity="{OPT["rimdark"]}"/>')
art += (f'<circle cx="{f(P(CX))}" cy="{f(P(CY))}" r="{f(L(D / 2 - RIM / 2))}" fill="none" stroke="url(#rimlit)" '
        f'stroke-width="{f(L(RIM))}"/>')

# ---- fg: the QR code, nothing else ------------------------------------------------------------
# The dots come from the kit. The finders are drawn here: strict decoders (OpenCV's two detectors)
# find a code by the outer corners of its finders and lose reads when those are rounded. Measured on
# the 600 dpi raster of the CMYK PDF, 56 fixed tests at 1000 / 700 / 500 px sticker width, OpenCV
# QRCodeDetector and QRCodeDetectorAruco:
#   outer 0.8 module, eye 0.4 (the kit's default)   31 / 27 / 18   and   18 / 20 / 16
#   outer 0.2, eye 0.4                              54 / 51 / 46   and   50 / 49 / 43
#   outer 0 (square), eye 0.4  <- this one          54 / 54 / 48   and   53 / 54 / 49
#   all square                                      54 / 54 / 48   and   53 / 54 / 49
# So the ring is square (0.07 mm of rounding would not show in print anyway) and the eye keeps the
# kit's 0.4-module rounding, which costs nothing. zxing reads 52 / 50 / 45 with every shape.
# kit.FINDER_A is not touched.
def finder(X, Y, m):
    a = OPT['finder'] * m; e = OPT['eye'] * m; s = 7 * m - 2 * a
    ring = (f'M{X + a:.4f},{Y:.4f} h{s:.4f} a{a:.4f},{a:.4f} 0 0 1 {a:.4f},{a:.4f} v{s:.4f} a{a:.4f},{a:.4f} 0 0 1 {-a:.4f},{a:.4f} '
            f'h{-s:.4f} a{a:.4f},{a:.4f} 0 0 1 {-a:.4f},{-a:.4f} v{-s:.4f} a{a:.4f},{a:.4f} 0 0 1 {a:.4f},{-a:.4f} z') if a > 0 else \
           f'M{X:.4f},{Y:.4f}h{7 * m:.4f}v{7 * m:.4f}h{-7 * m:.4f}z'
    return (f'<path fill-rule="evenodd" fill="{kit.QR_INK}" d="{ring} M{X + m:.4f},{Y + m:.4f}v{5 * m:.4f}h{5 * m:.4f}v{-5 * m:.4f}z"/>'
            f'<rect x="{X + 2 * m:.4f}" y="{Y + 2 * m:.4f}" width="{3 * m:.4f}" height="{3 * m:.4f}" rx="{e:.4f}" fill="{kit.QR_INK}"/>')
fg, n = kit.qr_round(CX, CY, D, QM, fill=0, rounded_finders=False)        # the bare code: a square of dots on a clear disc
assert n == NQ
for fx, fy in ((0, 0), (n - 7, 0), (0, n - 7)):                            # swap the kit's square finders for ours
    X, Y = P(CX - n * QM / 2 + fx * QM), P(CY - n * QM / 2 + fy * QM)
    sq = kit._finder(X, Y, L(QM), kit.QR_INK, False)
    assert fg.count(sq) == 1, 'finder not found in the kit output'
    fg = fg.replace(sq, finder(X, Y, L(QM)))
if OPT['word'] > 0:           # not part of the final
    FS = 2.3
    bx, by = P(AX[1] + FS * 0.355), P(BOT - R - 0.4)
    fg += (f'<text transform="translate({f(bx)} {f(by)}) rotate(-90)" text-anchor="start" '
           f'font-family="Manrope" font-weight="700" font-size="{f(L(FS))}" letter-spacing="{f(L(FS * 0.02))}" '
           f'fill="#2b1400">Kanau</text>')
if OUT == HERE:
    assert '<text' not in fg and 'opacity' not in fg and 'stroke' not in fg and 'url(' not in fg, 'fg must be the flat QR only'
    assert fg.count('fill="') == fg.count(f'fill="{kit.QR_INK}"'), 'fg has a fill that is not the QR ink'

# ---- rough press check ------------------------------------------------------------------------
def soft_proof_scan(outdir):
    """Scan battery on a rough CMYK soft proof (generic profile, lifted black, slight softening).
    The real proof is the one produce.py renders from the CMYK PDF; this one only stresses the code."""
    import numpy as np, cv2
    from PIL import Image, ImageCms
    srgb = ImageCms.createProfile('sRGB')
    cmyk = ImageCms.getOpenProfile('/usr/share/color/icc/ghostscript/default_cmyk.icc')
    a2b = ImageCms.buildTransform(srgb, cmyk, 'RGB', 'CMYK', renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
                                  flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
    b2a = ImageCms.buildTransform(cmyk, srgb, 'CMYK', 'RGB', renderingIntent=ImageCms.Intent.ABSOLUTE_COLORIMETRIC)
    im = Image.open(os.path.join(outdir, 'finish.png')).convert('RGB')
    pr = ImageCms.applyTransform(ImageCms.applyTransform(im, a2b), b2a)
    a = np.asarray(pr).astype('float32'); a = 10 + a * (245 - 10) / 255
    a = cv2.GaussianBlur(a, (0, 0), 1.2).clip(0, 255).astype('uint8')
    tmp = os.path.join(outdir, '_softproof_tmp.png')
    Image.fromarray(a).save(tmp)
    res = kit.scan(tmp); os.remove(tmp)
    return res

if __name__ == '__main__':
    kit.save(OUT, art, fg, defs)
    rep = kit.preview(OUT)
    rep['soft_proof_scan'] = soft_proof_scan(OUT)
    rep['finder_outer_radius_modules'] = OPT['finder']; rep['finder_eye_radius_modules'] = OPT['eye']
    rep['kit_FINDER_A_untouched'] = kit.FINDER_A
    json.dump(rep, open(os.path.join(OUT, 'report.json'), 'w'), indent=1)
    print(rep)
    print(f'pitch {PITCH:.2f}  pill {W:.2f}  gap {PITCH - W:.2f}  axes {[round(a, 2) for a in AX]}')
    print(f'tops {[round(t, 2) for t in TOPS]}  disc {D} mm, centre {CX:.2f}, left edge {CX - D / 2:.2f}  module {QM}  n {n}')
    corner = QUIET * math.sqrt(2)
    print(f'quiet-zone corner {corner:.3f} mm from the centre; rim shading starts at {D / 2 - RIM:.3f} '
          f'({(D / 2 - RIM - corner) * 1000:.0f} um clear); disc edge {D / 2:.2f}; disc to cut {60 - CX - D / 2:.2f} mm')
