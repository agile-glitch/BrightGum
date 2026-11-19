// Renders packaging/bright-cartons.html to a print-ready PDF and PNG previews.
// Usage: python3 packaging/build_cartons.py && node packaging/render.js
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const dir = __dirname;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 816, height: 1056 }, deviceScaleFactor: 3 });
  await page.goto('file://' + path.join(dir, 'bright-cartons.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  console.log('Lato loaded:', await page.evaluate(() => document.fonts.check('900 12px Lato')));
  await page.pdf({ path: path.join(dir, 'bright-cartons.pdf'), preferCSSPageSize: true, printBackground: true });

  const ids = ['peppermint', 'spearmint', 'blue-raspberry', 'raspberry', 'pickle'];
  const pages = await page.$$('section.page');
  for (let i = 1; i < pages.length; i++) {
    const labels = await pages[i].$$('.label');
    await labels[0].screenshot({ path: path.join(dir, `preview-${ids[i - 1]}-front.png`) });
    await labels[1].screenshot({ path: path.join(dir, `preview-${ids[i - 1]}-back.png`) });
  }
  await (await pages[0].$('.stack')).screenshot({ path: path.join(dir, 'preview-lineup.png') });
  await browser.close();
})();
