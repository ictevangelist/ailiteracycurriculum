// node tools/posters/render.js  -> downloads/*.pdf and images/posters/*.png (A4)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { execSync } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const spki = execSync("openssl x509 -in /root/.ccr/agent-proxy-ca.crt -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | openssl enc -base64").toString().trim();
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--ignore-certificate-errors-spki-list=' + spki] });
  const pg = await b.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 2 });
  const root = path.join(__dirname, '..', '..');
  fs.mkdirSync(path.join(root, 'downloads'), { recursive: true });
  fs.mkdirSync(path.join(root, 'images', 'posters'), { recursive: true });
  for (const n of ['ai-loop', 'ideal-habits']) {
    await pg.goto('file://' + path.join(__dirname, n + '.html'), { waitUntil: 'networkidle' });
    await pg.evaluate(() => document.fonts.ready);
    await pg.pdf({ path: path.join(root, 'downloads', `ideal-thinkers-${n}-poster-a4.pdf`), format: 'A4', printBackground: true });
    await pg.screenshot({ path: path.join(root, 'images', 'posters', `${n}.png`) });
    const over = await pg.evaluate(() => { const s = document.querySelector('.sheet'); return s.scrollHeight > s.clientHeight + 1; });
    console.log(n, over ? 'OVERFLOWS' : 'fits');
  }
  await b.close();
})();
