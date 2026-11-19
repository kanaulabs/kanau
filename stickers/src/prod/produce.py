"""Turn a kit design folder (art.svg + fg.svg) into a print-ready CMYK PDF.
  art layer -> 600 dpi image; fg layer (QR, type) -> vector on top, text outlined,
  neutral darks forced to 100% K. Usage: python3 produce.py <design_dir> <out_base>"""
import sys, os, re, subprocess, json, base64
SP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SP + '/kit')
import kit, pikepdf

def produce(design, out_base, px=1512):
    design = os.path.abspath(design); out_base = os.path.abspath(out_base)
    art_png = out_base + '-art600.png'
    kit.render(os.path.join(design, 'art.svg'), art_png, px)            # 1512 px = 64 mm at 600 dpi
    fg = open(os.path.join(design, 'fg.svg'), encoding='utf8').read()
    b64 = base64.b64encode(open(art_png, 'rb').read()).decode()
    img = f'<image href="data:image/png;base64,{b64}" x="0" y="0" width="{kit.CAN:g}" height="{kit.CAN:g}" preserveAspectRatio="none"/>'
    assert '</defs>' in fg
    head, body = fg.split('</defs>', 1)
    if 'url(#' not in body and 'href="#' not in body:      # fg does not use the shared defs: drop them
        head = head[:head.index('<defs>')] + '<defs>'
    combo = head + '</defs>' + img + body
    html = out_base + '-combo.html'
    open(html, 'w', encoding='utf8').write(f'<html><body style="margin:0">{combo}</body></html>')
    rgb = out_base + '-RGB.pdf'
    subprocess.run(['node', SP + '/prod/pdf.js', html, rgb], check=True)
    cmyk = out_base + '-CMYK.pdf'
    subprocess.run(['gs', '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=pdfwrite', '-dNoOutputFonts',
                    '-sColorConversionStrategy=CMYK', '-sProcessColorModel=DeviceCMYK', '-dCompatibilityLevel=1.6',
                    '-dAutoFilterColorImages=false', '-dColorImageFilter=/FlateEncode', '-dDownsampleColorImages=false',
                    '-o', cmyk, rgb], check=True)
    pdf = pikepdf.open(cmyk, allow_overwriting_input=True); pg = pdf.pages[0]
    cs = pg.Contents if isinstance(pg.Contents, pikepdf.Array) else [pg.Contents]
    seen = {}
    def fix(m):
        c, mm_, y, k = (float(m.group(i)) for i in range(1, 5)); op = m.group(5).decode()
        key = f'{c:g} {mm_:g} {y:g} {k:g} {op}'
        if k >= 0.7 and max(c, mm_, y) - min(c, mm_, y) < 0.12 and (c, mm_, y) != (0, 0, 0):
            seen[key] = seen.get(key, 0) + 1
            return f'/GSop gs 0 0 0 1 {op}'.encode()        # solid K, overprinting the art below
        seen.setdefault('keep ' + key, 0); seen['keep ' + key] += 1
        return m.group(0)
    pat = re.compile(rb'(?<![\d.])([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([kK])\b')
    for c in cs:
        c.write(pat.sub(fix, c.read_bytes()))
    res = pg.Resources
    if '/ExtGState' not in res: res.ExtGState = pikepdf.Dictionary()
    res.ExtGState['/GSop'] = pikepdf.Dictionary(Type=pikepdf.Name.ExtGState, OP=True, op=True, OPM=1)
    mb = [float(v) for v in pg.MediaBox]; d = mb[3] - 181.417
    pg.MediaBox = [0, d, 181.417, mb[3]]; pg.BleedBox = [0, d, 181.417, mb[3]]
    pg.TrimBox = [5.669, d + 5.669, 175.748, mb[3] - 5.669]
    pdf.save(cmyk)
    for f in (rgb, html, art_png):
        os.remove(f)
    # verify
    import cv2, zxingcpp
    fonts = subprocess.run(['pdffonts', cmyk], capture_output=True, text=True).stdout.strip().splitlines()[2:]
    imgs = subprocess.run(['pdfimages', '-list', cmyk], capture_output=True, text=True).stdout.strip().splitlines()[2:]
    scans = {}
    for dpi in (100, 120, 150, 300):
        base = f'{out_base}-chk{dpi}'
        subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-singlefile', cmyk, base], check=True)
        im = cv2.imread(base + '.png')
        scans[dpi] = any(r.text == kit.URL for r in zxingcpp.read_barcodes(im))
        scans[f'{dpi}blur'] = any(r.text == kit.URL for r in zxingcpp.read_barcodes(cv2.GaussianBlur(im, (3, 3), 0)))
        if dpi != 300: os.remove(base + '.png')
    os.replace(f'{out_base}-chk300.png', out_base + '-proof300.png')
    # total ink (C+M+Y+K) of the finished page
    import numpy as np
    from PIL import Image
    tif = out_base + '-ink.tif'
    subprocess.run(['gs', '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=tiff32nc', '-r150', '-o', tif, cmyk], check=True)
    a = np.asarray(Image.open(tif)).astype(float) / 255 * 100; tac = a.sum(axis=2); os.remove(tif)
    ink = {'median': round(float(np.median(tac))), 'p99': round(float(np.percentile(tac, 99))), 'max': round(float(tac.max())),
           'share_over_300': round(float((tac > 300).mean()), 3)}
    rep = {'pdf': cmyk, 'fonts_left': len(fonts), 'images': imgs, 'color_ops': seen, 'scan_by_dpi': scans, 'total_ink_pct': ink}
    print(json.dumps(rep, indent=1)); return rep

if __name__ == '__main__':
    produce(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1512)
