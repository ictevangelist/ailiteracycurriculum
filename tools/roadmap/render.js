// node render.js <road.html> <out dir>  -> IDEAL Thinkers Road Map (A3).pdf and preview.png, with an overflow check
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { execSync } = require('child_process');
const path = require('path');
(async () => {
  const [src, out] = process.argv.slice(2);
  const spki = execSync("openssl x509 -in /root/.ccr/agent-proxy-ca.crt -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | openssl enc -base64").toString().trim();
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--ignore-certificate-errors-spki-list=' + spki] });
  const pg = await b.newPage({ viewport: { width: 1588, height: 1123 }, deviceScaleFactor: 2 });
  await pg.goto('file://' + path.resolve(src), { waitUntil: 'networkidle' });
  await pg.evaluate(() => document.fonts.ready);
  const bad = await pg.evaluate(() => [...document.querySelectorAll('.card,.sign,.dest,.panel,.routine')]
    .filter(e => e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1)
    .map(e => (e.querySelector('.ctitle,.st,.ph,b') || e).textContent.slice(0, 40) + ' ' + e.scrollHeight + '/' + e.clientHeight));
  const fonts = await pg.evaluate(() => [...new Set([...document.querySelectorAll('*')].map(e => getComputedStyle(e).fontFamily))]);
  console.log('overflow:', JSON.stringify(bad));
  console.log('fonts:', JSON.stringify(fonts));
  const spots = await pg.evaluate(() => { const W = 1588, H = 1123, o = {};
    document.querySelectorAll('[data-spot]').forEach(e => { const r = e.getBoundingClientRect();
      o[e.dataset.spot] = [r.left / W * 100, r.top / H * 100, r.width / W * 100, r.height / H * 100].map(v => Math.round(v * 1000) / 1000); });
    return o; });
  require('fs').writeFileSync(path.join(out, 'spots.json'), JSON.stringify(spots, null, 1));
  await pg.screenshot({ path: path.join(out, 'map-3176.png') });
  await pg.pdf({ path: path.join(out, 'IDEAL Thinkers Road Map (A3).pdf'), width: '420mm', height: '297mm', printBackground: true });
  await pg.screenshot({ path: path.join(out, 'preview.png') });
  await b.close();
})();
