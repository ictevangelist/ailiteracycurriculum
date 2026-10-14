// Renders images/social-card.png (1200x630) for link previews. Run: node tools/social/render.js
const path = require('path');
const {execSync} = require('child_process');
const {chromium} = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const spki = execSync("openssl x509 -in /root/.ccr/agent-proxy-ca.crt -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | openssl enc -base64").toString().trim();
  const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--ignore-certificate-errors-spki-list=' + spki]});
  const p = await b.newPage({viewport: {width: 1200, height: 630}});
  await p.goto('file://' + path.join(__dirname, 'card.html'));
  await p.waitForLoadState('networkidle');
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({path: path.join(__dirname, '../../images/social-card.png')});
  await b.close();
})();
