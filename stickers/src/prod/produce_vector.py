"""Flat design -> all-vector CMYK PDF with defined ink builds.
Usage: python3 produce_vector.py <design_dir> <out_base>
Uses full.svg; text outlined by Ghostscript; each sRGB fill colour is replaced by a fixed CMYK build."""
import sys, os, re, subprocess, json
import pikepdf
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'kit')); import kit

# sRGB hex -> (C, M, Y, K) in %, overprint?
BUILDS = {
    '#e8e1d3': ((8, 10, 18, 0), False),     # paper-cream ground
    '#fbfaf6': ((0, 0, 0, 0), False),       # QR disc: bare paper
    '#0b0b0d': ((40, 30, 30, 100), False),  # empty slot: rich black, 200 %
    '#050505': ((0, 0, 0, 100), True),      # QR + wordmark: K only, overprint
    '#a9a49a': ((30, 28, 35, 5), False),    # grey
    '#f4a424': ((0, 40, 95, 0), False),     # amber
    '#93c69f': ((45, 5, 45, 0), False),     # green
    '#e7a9b6': ((5, 40, 15, 0), False),     # pink
    '#88aada': ((50, 25, 0, 0), False),     # blue
}

def produce(design, out_base):
    design = os.path.abspath(design); out_base = os.path.abspath(out_base)
    svg = open(os.path.join(design, 'full.svg'), encoding='utf8').read()
    used = {c.lower() for c in re.findall(r'fill="(#[0-9a-fA-F]{6})"', svg)}
    missing = used - set(BUILDS); assert not missing, f'no CMYK build for {missing}'
    html = out_base + '-v.html'
    open(html, 'w').write(f'<html><body style="margin:0">{svg}</body></html>')
    rgb = out_base + '-vRGB.pdf'; out = out_base + '-vOUT.pdf'
    subprocess.run(['node', os.path.join(HERE, 'pdf.js'), html, rgb], check=True)
    subprocess.run(['gs', '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=pdfwrite', '-dNoOutputFonts',
                    '-sColorConversionStrategy=RGB', '-dCompatibilityLevel=1.6', '-o', out, rgb], check=True)
    pdf = pikepdf.open(out); pg = pdf.pages[0]
    pg.contents_coalesce(); body = pg.Contents.read_bytes()
    table = {}
    for hx, (c, op) in BUILDS.items():
        r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)); table[(r, g, b)] = (c, op)
    seen = {}
    def near(r, g, b):
        best = min(table, key=lambda k: (k[0] - r) ** 2 + (k[1] - g) ** 2 + (k[2] - b) ** 2)
        assert sum((best[i] - v) ** 2 for i, v in enumerate((r, g, b))) < 0.0004, (r, g, b)
        return table[best]
    def fix(m):
        r, g, b = (float(m.group(i)) for i in (1, 2, 3)); op = m.group(4).decode()
        (c, mm, y, k), ov = near(r, g, b)
        key = f'{c} {mm} {y} {k}' + (' OP' if ov else ''); seen[key] = seen.get(key, 0) + 1
        gs_ = '/GSop gs ' if ov else '/GSno gs '
        return f'{gs_}{c/100:g} {mm/100:g} {y/100:g} {k/100:g} {"k" if op == "rg" else "K"}'.encode()
    body2 = re.sub(rb'(?<![\d.])([\d.]+) ([\d.]+) ([\d.]+) (rg|RG)\b', fix, body)
    assert not re.search(rb'(?<![\d.])[\d.]+ (g|G)\b', body2), 'grey ops left'
    assert not re.search(rb'\b(cs|CS|scn|SCN|sh)\b', body2), 'colour spaces / shadings left'
    pg.Contents.write(body2)
    res = pg.Resources
    if '/ExtGState' not in res: res.ExtGState = pikepdf.Dictionary()
    res.ExtGState['/GSop'] = pikepdf.Dictionary(Type=pikepdf.Name.ExtGState, OP=True, op=True, OPM=1)
    res.ExtGState['/GSno'] = pikepdf.Dictionary(Type=pikepdf.Name.ExtGState, OP=False, op=False, OPM=0)
    mb = [float(v) for v in pg.MediaBox]
    pg.MediaBox = [mb[0], mb[3] - 181.417, mb[0] + 181.417, mb[3]]
    PT = 181.417; d = mb[3] - PT
    if abs(d) > 1e-6:
        pg.Contents.write(b'q 1 0 0 1 0 %s cm\n' % f'{-d:.6f}'.encode() + pg.Contents.read_bytes() + b'\nQ\n')
    pg.MediaBox = [0, 0, PT, PT]; pg.BleedBox = [0, 0, PT, PT]; pg.TrimBox = [5.669, 5.669, 175.748, 175.748]
    if '/CropBox' in pg: del pg['/CropBox']
    cmyk = out_base + '-CMYK.pdf'; pdf.save(cmyk); pdf.close()
    for f in (html, rgb, out): os.remove(f)
    print(json.dumps({'pdf': cmyk, 'fills': seen}, indent=1))

if __name__ == '__main__':
    produce(sys.argv[1], sys.argv[2])
