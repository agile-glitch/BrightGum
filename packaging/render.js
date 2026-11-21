// Renders the carton HTML files to print-ready PDFs and PNG previews.
// Usage: python3 packaging/build_cartons.py && node packaging/render.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const VARIANTS = [
  { dir: __dirname, stem: 'bright-cartons' },                                  // main: no xylitol
  { dir: path.join(__dirname, 'xylitol'), stem: 'bright-cartons-xylitol' },  // alternative: xylitol
];
const ids = ['peppermint', 'spearmint', 'blue-raspberry', 'raspberry', 'watermelon', 'pickle', 'cotton-candy', 'peppermint-caffeinated', 'spearmint-caffeinated'];

(async () => {
  const browser = await chromium.launch();
  for (const { dir, stem } of VARIANTS) {
    const html = path.join(dir, stem + '.html');
    if (!fs.existsSync(html)) continue;
    const page = await browser.newPage({ viewport: { width: 816, height: 1056 }, deviceScaleFactor: 3 });
    await page.goto('file://' + html, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    console.log(stem, '- Lato loaded:', await page.evaluate(() => document.fonts.check('900 12px Lato')));
    await page.pdf({ path: path.join(dir, stem + '.pdf'), preferCSSPageSize: true, printBackground: true });

    const pages = await page.$$('section.page');
    for (let i = 1; i < pages.length; i++) {
      const labels = await pages[i].$$('.label');
      await labels[0].screenshot({ path: path.join(dir, `preview-${ids[i - 1]}-front.png`) });
      await labels[1].screenshot({ path: path.join(dir, `preview-${ids[i - 1]}-back.png`) });
    }
    await (await pages[0].$('.stack')).screenshot({ path: path.join(dir, 'preview-lineup.png') });
    await page.close();
  }
  await browser.close();
})();
