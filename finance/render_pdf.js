// Renders finance/bright-gum-cost-study.html to PDF, and reports any page whose content overflows.
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 816, height: 1056 } });
  await page.goto('file://' + path.join(__dirname, 'bright-gum-cost-study.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const overflow = await page.evaluate(() => [...document.querySelectorAll('section.page')].map((s, i) => {
    const footTop = s.querySelector('footer').getBoundingClientRect().top;
    const last = [...s.children].filter((c) => c.tagName !== 'FOOTER').pop().getBoundingClientRect().bottom;
    return { page: i + 1, spare_px: Math.round(footTop - last) };
  }));
  console.log(JSON.stringify(overflow));
  await page.pdf({ path: path.join(__dirname, 'bright-gum-cost-study.pdf'), preferCSSPageSize: true, printBackground: true });
  await browser.close();
})();
