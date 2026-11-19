// node render.js <in.svg> <out.png> <px>  : render a 64x64mm kit SVG to a square PNG
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [,,src,out,pxs]=process.argv;const px=+pxs||1280;const b=await chromium.launch();
const p=await b.newPage({deviceScaleFactor:1});await p.setViewportSize({width:px,height:px});
const svg=fs.readFileSync(src,'utf8').replace('width="64mm" height="64mm"',`width="${px}" height="${px}"`);
await p.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);await p.waitForTimeout(250);
await p.screenshot({path:out,clip:{x:0,y:0,width:px,height:px}});await b.close();})();
