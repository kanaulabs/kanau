// node mock.js <full.svg> <out.png> : sticker inside a clear case on a dark and a light phone
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [,,src,out]=process.argv;const b=await chromium.launch();const p=await b.newPage({deviceScaleFactor:2});
await p.setViewportSize({width:960,height:820});const k=4.4;
const raw=fs.readFileSync(src,'utf8').replace('width="64mm" height="64mm"',`width="${64*k}" height="${64*k}"`);
const uniq=(s,t)=>s.replace(/id="([^"]+)"/g,`id="$1${t}"`).replace(/url\(#([^)]+)\)/g,`url(#$1${t})`).replace(/href="#([^"]+)"/g,`href="#$1${t}"`);
const sticker=(t)=>`<div style="position:absolute;left:${(71.6-60)/2*k}px;top:${70*k}px;width:${60*k}px;height:${60*k}px;overflow:hidden;transform:rotate(-1.2deg);box-shadow:0 1px 2px rgba(0,0,0,.35)"><div style="position:absolute;left:${-2*k}px;top:${-2*k}px">${uniq(raw,t)}</div></div>`;
const phone=(t,body,rot)=>`<div style="position:relative;width:${71.6*k}px;height:${147.6*k}px;border-radius:${11*k}px;background:${body};transform:rotate(${rot}deg);box-shadow:0 30px 60px rgba(0,0,0,.35),inset 0 0 0 1.5px rgba(255,255,255,.08)">
 <div style="position:absolute;left:${5*k}px;top:${5*k}px;width:${33*k}px;height:${35*k}px;border-radius:${8*k}px;background:${body};filter:brightness(1.12);box-shadow:inset 0 0 0 1px rgba(255,255,255,.12),0 2px 6px rgba(0,0,0,.25)">
  ${[[8,8],[8,24],[23,16]].map(([x,y])=>`<div style="position:absolute;left:${(x-5)*k}px;top:${(y-5)*k}px;width:${12*k}px;height:${12*k}px;border-radius:50%;background:radial-gradient(circle at 40% 40%,#3a3f4a,#07080a 60%);box-shadow:0 0 0 ${1.2*k}px #2a2c30"></div>`).join('')}
 </div>${sticker(t)}
 <div style="position:absolute;inset:-${1.6*k}px;border-radius:${12.5*k}px;border:${1.6*k}px solid rgba(255,255,255,.35);background:linear-gradient(125deg,rgba(255,255,255,.22) 0%,rgba(255,255,255,0) 28%,rgba(255,255,255,0) 62%,rgba(255,255,255,.10) 75%,rgba(255,255,255,0) 90%);box-shadow:inset 0 0 0 1px rgba(255,255,255,.4)"></div></div>`;
await p.setContent(`<body style="margin:0;height:820px;display:flex;gap:110px;align-items:center;justify-content:center;background:linear-gradient(160deg,#c9c3b8,#9e9789)">${phone('_a','#2b2d31',-6)}${phone('_b','#dcd7ce',5)}</body>`);
await p.waitForTimeout(250);await p.screenshot({path:out});await b.close();})();
