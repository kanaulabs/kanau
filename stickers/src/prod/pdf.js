const {chromium}=require('playwright');
(async()=>{const [,,html,out]=process.argv;const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+html);await p.waitForTimeout(300);
await p.pdf({path:out,width:'64mm',height:'64mm',printBackground:true,pageRanges:'1'});await b.close();})();
