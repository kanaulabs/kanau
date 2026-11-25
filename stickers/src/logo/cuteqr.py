"""Friendlier QR drawings for the badge. All dark parts in one ink (K100 in print)."""
import math
import kit
from kit import P, L

def _fin(gx, gy, n):
    return (gx < 7 and gy < 7) or (gx >= n - 7 and gy < 7) or (gx < 7 and gy >= n - 7)

def draw(cx, cy, module, ec='m', modules='liquid', eyes='round', hole=0, hole_svg=None, ink=kit.QR_INK, dot=0.86):
    """modules: 'liquid' (neighbours melt together), 'dots'. eyes: 'round' (circles), 'soft' (rounded squares).
    hole: side (modules, odd) of a cleared square in the middle, filled by hole_svg(x, y, size_mm)."""
    M = kit.qr_matrix(ec); n = len(M); m = module; ox = cx - n * m / 2; oy = cy - n * m / 2
    c0 = (n - hole) // 2; c1 = c0 + hole
    def on(x, y):
        return 0 <= x < n and 0 <= y < n and M[y][x] and not _fin(x, y, n) and not (c0 <= x < c1 and c0 <= y < c1)
    s = ''; U = L(m)
    for y in range(n):
        for x in range(n):
            if not on(x, y): continue
            X, Y = P(ox + x * m), P(oy + y * m)
            if modules == 'dots':
                s += f'<circle cx="{X + U / 2:.3f}" cy="{Y + U / 2:.3f}" r="{U * dot / 2:.3f}" fill="{ink}"/>'
                continue
            s += f'<circle cx="{X + U / 2:.3f}" cy="{Y + U / 2:.3f}" r="{U / 2:.3f}" fill="{ink}"/>'
            if on(x + 1, y): s += f'<rect x="{X + U / 2:.3f}" y="{Y:.3f}" width="{U:.3f}" height="{U:.3f}" fill="{ink}"/>'
            if on(x, y + 1): s += f'<rect x="{X:.3f}" y="{Y + U / 2:.3f}" width="{U:.3f}" height="{U:.3f}" fill="{ink}"/>'
    for fx, fy in [(0, 0), (n - 7, 0), (0, n - 7)]:
        X, Y = P(ox + fx * m), P(oy + fy * m); c = (X + 3.5 * U, Y + 3.5 * U)
        if eyes == 'round':
            s += (f'<path fill-rule="evenodd" fill="{ink}" d="M{c[0] - 3.5 * U:.3f},{c[1]:.3f} a{3.5 * U:.3f},{3.5 * U:.3f} 0 1 0 {7 * U:.3f},0 '
                  f'a{3.5 * U:.3f},{3.5 * U:.3f} 0 1 0 {-7 * U:.3f},0 z M{c[0] - 2.5 * U:.3f},{c[1]:.3f} a{2.5 * U:.3f},{2.5 * U:.3f} 0 1 1 {5 * U:.3f},0 '
                  f'a{2.5 * U:.3f},{2.5 * U:.3f} 0 1 1 {-5 * U:.3f},0 z"/>'
                  f'<circle cx="{c[0]:.3f}" cy="{c[1]:.3f}" r="{1.55 * U:.3f}" fill="{ink}"/>')
        else:
            a, b = 2.2 * U, 1.3 * U
            s += (f'<path fill-rule="evenodd" fill="{ink}" d="M{X + a:.3f},{Y:.3f} h{7 * U - 2 * a:.3f} a{a:.3f},{a:.3f} 0 0 1 {a:.3f},{a:.3f} v{7 * U - 2 * a:.3f} '
                  f'a{a:.3f},{a:.3f} 0 0 1 {-a:.3f},{a:.3f} h{-(7 * U - 2 * a):.3f} a{a:.3f},{a:.3f} 0 0 1 {-a:.3f},{-a:.3f} v{-(7 * U - 2 * a):.3f} a{a:.3f},{a:.3f} 0 0 1 {a:.3f},{-a:.3f} z '
                  f'M{X + U + b:.3f},{Y + U:.3f} a{b:.3f},{b:.3f} 0 0 0 {-b:.3f},{b:.3f} v{5 * U - 2 * b:.3f} a{b:.3f},{b:.3f} 0 0 0 {b:.3f},{b:.3f} h{5 * U - 2 * b:.3f} '
                  f'a{b:.3f},{b:.3f} 0 0 0 {b:.3f},{-b:.3f} v{-(5 * U - 2 * b):.3f} a{b:.3f},{b:.3f} 0 0 0 {-b:.3f},{-b:.3f} z"/>'
                  f'<rect x="{X + 2 * U:.3f}" y="{Y + 2 * U:.3f}" width="{3 * U:.3f}" height="{3 * U:.3f}" rx="{1.1 * U:.3f}" fill="{ink}"/>')
    art = ''
    if hole and hole_svg:
        art = hole_svg(ox + c0 * m, oy + c0 * m, hole * m)
    return s, art, n
