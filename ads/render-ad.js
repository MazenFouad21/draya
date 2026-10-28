// Renders an ad page to an MP4 (1080x1920, 30fps), optionally with a soundtrack.
// Usage: node ads/render-ad.js [page.html] [seconds] [audio.wav]   (needs Playwright + ffmpeg)
const {chromium}=require('playwright');
const {execFileSync}=require('child_process');
const fs=require('fs'),path=require('path'),os=require('os');

const FPS=30, DURATION=Number(process.argv[3]||26);
const html=path.resolve(process.argv[2]||path.join(__dirname,'programming-course-ad.html'));
const audio=process.argv[4]&&path.resolve(process.argv[4]);
const out=html.replace(/\.html$/,'.mp4');

(async()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'ad-frames-'));
  const browser=await chromium.launch();
  const page=await browser.newPage({viewport:{width:1080,height:1920}});
  await page.goto('file://'+html+'#render');
  await page.evaluate(()=>document.fonts.ready);
  for(let f=0;f<FPS*DURATION;f++){
    await page.evaluate(t=>window.seek(t),f/FPS);
    await page.screenshot({path:path.join(dir,`f${String(f).padStart(5,'0')}.jpg`),type:'jpeg',quality:92});
  }
  await browser.close();
  execFileSync('ffmpeg',['-y','-loglevel','error','-framerate',String(FPS),'-i',path.join(dir,'f%05d.jpg'),
    ...(audio?['-i',audio,'-c:a','aac','-b:a','192k','-shortest']:[]),
    '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',out]);
  fs.rmSync(dir,{recursive:true});
  console.log('wrote',out);
})();
