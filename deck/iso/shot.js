const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
(async()=>{const [,,html,out,w,h]=process.argv;const b=await chromium.launch();const p=await b.newPage({viewport:{width:+w,height:+h},deviceScaleFactor:1.5});
await p.goto('file://'+html);await p.waitForTimeout(400);await p.screenshot({path:out,fullPage:true});await b.close();})();
