"""Normalise page boxes to start at 0,0 (pixel-identical render) and re-verify a produce.py PDF.
Usage: python3 finalize.py <pdf>"""
import sys, os, re, json, subprocess, tempfile
import numpy as np, cv2, zxingcpp, pikepdf
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kit'))
import kit
PT = 181.417
def ppm(pdf, dpi, base):
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-singlefile', pdf, base], check=True); return base + '.png'
def run(PDF):
    tmp = tempfile.mkdtemp(dir=os.path.dirname(PDF)); rep = {'pdf': PDF}
    before = cv2.imread(ppm(PDF, 600, tmp + '/b'))
    pdf = pikepdf.open(PDF, allow_overwriting_input=True); pg = pdf.pages[0]
    mb = [float(v) for v in pg.MediaBox]; d = mb[1]
    if abs(d) > 1e-6:
        pg.contents_coalesce(); body = pg.Contents.read_bytes()
        pg.Contents.write(b'q 1 0 0 1 0 %s cm\n' % (f'{-d:.6f}'.rstrip('0').rstrip('.')).encode() + body + b'\nQ\n')
        pg.MediaBox = [0, 0, PT, PT]; pg.BleedBox = [0, 0, PT, PT]; pg.TrimBox = [5.669, 5.669, 175.748, 175.748]
        if '/CropBox' in pg: del pg['/CropBox']
        pdf.save(PDF)
    pdf.close()
    after = cv2.imread(ppm(PDF, 600, tmp + '/a'))
    rep['render_max_diff_after_box_fix'] = int(np.abs(before.astype(int) - after.astype(int)).max()) if before.shape == after.shape else 'shape changed'
    pdf = pikepdf.open(PDF); pg = pdf.pages[0]
    rep['boxes'] = {k[1:]: [round(float(v), 3) for v in pg[k]] for k in ('/MediaBox', '/BleedBox', '/TrimBox')}
    body = b''.join(c.read_bytes() for c in (pg.Contents if isinstance(pg.Contents, pikepdf.Array) else [pg.Contents]))
    rep['fill_ops'] = sorted({(a.decode() + ' ' + b.decode()) for a, b in re.findall(rb'(?<![\d.])([\d.]+ [\d.]+ [\d.]+ [\d.]+) ([kK])\b', body)})
    rep['rgb_or_gray_ops'] = len(re.findall(rb'(?<![\d.])[\d.]+ [\d.]+ [\d.]+ (?:rg|RG)\b|(?<![\d.])[\d.]+ [gG]\b', body))
    rep['overprint_gs'] = {str(k): {str(a): str(b) for a, b in v.items()} for k, v in pg.Resources.ExtGState.items()}
    rep['gsop_before_fill'] = body.count(b'/GSop gs 0 0 0 1 k')
    rep['vector_subpaths'] = body.count(b'\nh\n') + body.count(b' h\n')
    rep['fonts'] = subprocess.run(['pdffonts', PDF], capture_output=True, text=True).stdout.strip().splitlines()[2:]
    rep['images'] = subprocess.run(['pdfimages', '-list', PDF], capture_output=True, text=True).stdout.strip().splitlines()[2:]
    sc = {}
    for dpi in (120, 150, 200, 300):
        im = cv2.imread(ppm(PDF, dpi, tmp + f'/s{dpi}'))
        sc[dpi] = any(r.text == kit.URL for r in zxingcpp.read_barcodes(im))
        sc[f'{dpi}blur'] = any(r.text == kit.URL for r in zxingcpp.read_barcodes(cv2.GaussianBlur(im, (3, 3), 0)))
        t, _, _ = cv2.QRCodeDetector().detectAndDecode(im); sc[f'{dpi}opencv'] = (t == kit.URL)
    rep['scan'] = sc
    tif = tmp + '/ink.tif'
    subprocess.run(['gs', '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=tiff32nc', '-r150', '-o', tif, PDF], check=True)
    tac = (np.asarray(Image.open(tif)).astype(float) / 255 * 100).sum(axis=2)
    rep['total_ink'] = {'median': round(float(np.median(tac))), 'max': round(float(tac.max()))}
    subprocess.run(['rm', '-rf', tmp]); print(json.dumps(rep, indent=1)); return rep
if __name__ == '__main__':
    run(os.path.abspath(sys.argv[1]))
