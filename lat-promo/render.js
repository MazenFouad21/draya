// Render promo.html → MP4 (1080x1920, 30fps).
// If audio/b1.wav … audio/b11.wav exist (from tts_gemini.py or downloaded from Google AI Studio),
// scene timing follows the real voice-over lengths and the VO is muxed in. No music is added.
//
//   node render.js                 → out/lat-reel.mp4
//   node render.js --frames 0,90   → PNG stills only (quick check)
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');

const DIR = __dirname, FPS = 30, W = 1080, H = 1920;
const script = JSON.parse(fs.readFileSync(path.join(DIR, 'script.json'), 'utf8'));
const OUT = path.join(DIR, 'out'); fs.mkdirSync(OUT, { recursive: true });
const audioOf = id => path.join(DIR, 'audio', id + '.wav');
const dur = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());

// ---- timings: real VO durations when available, estimates otherwise
const hasVO = script.beats.every(b => fs.existsSync(audioOf(b.id)));
const T = {}; let t = script.lead;
for (const b of script.beats) {
  const d = hasVO ? dur(audioOf(b.id)) : b.est;
  T[b.id] = [t, d]; t += d + script.gap;
}
T.total = t - script.gap + script.tail;
console.log(hasVO ? 'Using real voice-over timings' : 'No VO found → estimated timings (silent video)', 'total', T.total.toFixed(2) + 's');

// ---- voice-over track: each beat placed at its start time, nothing else in the mix
function buildVO() {
  const vo = path.join(OUT, 'vo.wav');
  const args = ['-y', '-v', 'error'];
  script.beats.forEach(b => args.push('-i', audioOf(b.id)));
  const f = script.beats.map((b, i) => { const ms = Math.round(T[b.id][0] * 1000); return `[${i}]aresample=48000,aformat=channel_layouts=mono,adelay=${ms}|${ms}[a${i}]`; });
  f.push(script.beats.map((_, i) => `[a${i}]`).join('') + `amix=inputs=${script.beats.length}:normalize=0,apad,atrim=0:${T.total.toFixed(3)},loudnorm=I=-16:TP=-1.5:LRA=11[out]`);
  args.push('-filter_complex', f.join(';'), '-map', '[out]', '-ar', '48000', vo);
  execFileSync('ffmpeg', args);
  return vo;
}

(async () => {
  const stills = process.argv.includes('--frames') ? process.argv[process.argv.indexOf('--frames') + 1].split(',').map(Number) : null;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  const CAPS = script.beats.map(b => ({ id: b.id, html: (b.cap || b.text).replace(/\{([^}]+)\}/g, '<b>$1</b>') }));
  await page.addInitScript(([tm, caps]) => { window.RENDER = true; window.TIMINGS = tm; window.CAPS = caps; }, [T, CAPS]);
  await page.goto('file://' + path.join(DIR, 'promo.html'));
  await page.evaluate(() => window.ready);
  await page.waitForTimeout(400);
  const stage = await page.$('#stage');

  if (stills) {
    for (const fr of stills) {
      await page.evaluate(s => window.seek(s), fr / FPS);
      await stage.screenshot({ path: path.join(OUT, `still-${String(fr).padStart(4, '0')}.png`) });
    }
    await browser.close(); console.log('stills done'); return;
  }

  const frames = Math.ceil(T.total * FPS);
  const vo = hasVO ? buildVO() : null;
  const outFile = path.join(OUT, hasVO ? 'lat-reel.mp4' : 'lat-reel-silent.mp4');
  const args = ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-'];
  if (vo) args.push('-i', vo);
  args.push('-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS), '-movflags', '+faststart');
  if (vo) args.push('-c:a', 'aac', '-b:a', '192k', '-shortest');
  args.push(outFile);
  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });

  for (let i = 0; i < frames; i++) {
    await page.evaluate(s => window.seek(s), i / FPS);
    const buf = await stage.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stdout.write(`\rframe ${i}/${frames}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('\n→', outFile);
})();
