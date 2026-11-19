// Builds finance/bright-gum-cost-study.pptx from finance/cost_model.json.
// Usage: python3 finance/cost_model.py && node finance/build_pptx.js
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');
const sharp = require('sharp');
const SKILL = process.env.PPTX_SKILL_DIR || '';

const M = JSON.parse(fs.readFileSync(path.join(__dirname, 'cost_model.json'), 'utf8'));
const OUT = path.join(__dirname, 'bright-gum-cost-study.pptx');

const THEME = {
  name: 'bright gum',
  headFontFace: 'Arial',
  bodyFontFace: 'Calibri',
  colors: {
    dk1: '0D1117', lt1: 'FFFFFF', dk2: '4A5263', lt2: 'F4F6FB',
    accent1: '1428DC', accent2: '0085C7', accent3: '046A4A', accent4: '9AA3B5',
    accent5: 'C2185B', accent6: 'D62839', hlink: '1428DC', folHlink: '4A5263',
  },
};
const HEX = THEME.colors;
const GRID = 'DFE3EF';

const k = (v) => (v < 1e6 ? `$${Math.round(v / 1000)}k` : `$${(v / 1e6).toFixed(1)}M`);
const d0 = (v) => '$' + Math.round(v).toLocaleString('en-US');
const r0 = (v) => '$' + (Math.round(v / 100) * 100).toLocaleString('en-US');
const d2 = (v) => '$' + v.toFixed(2);
const n0 = (v) => Math.round(v).toLocaleString('en-US');

const cg = M.cogs[M.base_recipe];
const L = cg.launch_total, S = cg.scale_total;
const tot = M.startup_total, cap = M.factory_capital_total, fb = M.factory_breakeven;
const price = M.recommended_price;
const ch = M.channels[price.toFixed(2)];
const y1 = M.scenarios['Year 1: campus launch'], y2 = M.scenarios['At scale: regional retail'];
const DIRECT = 'Direct to local stores', DIST = 'Distributor to grocery chains';
const INPERSON = 'In person (campus table, events)', ONLINE = 'Online 6-pack, shipped by you';

(async () => {
  const logo = 'image/png;base64,' + (await sharp(path.join(__dirname, '..', 'brand', 'logo', 'bright-logo-primary.svg'), { density: 300 })
    .resize({ width: 1760 }).png().toBuffer()).toString('base64');

  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5 in
  pres.title = 'bright gum cost and pricing study';
  pres.author = 'bright gum';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;
  const FOOT = 'bright gum · Cost and pricing study · November 2026 · Planning estimates, not supplier quotes';

  pres.defineSlideMaster({
    title: 'TITLE', background: { color: C.background1 },
    objects: [
      { image: { data: logo, x: 0.9, y: 1.5, w: 5.2, h: 1.714 } },
      { placeholder: { options: { name: 'title', type: 'title', x: 0.9, y: 3.7, w: 11.5, h: 1.5, fontSize: 40, bold: true, color: C.text1, align: 'left', valign: 'top', margin: 0 }, text: '' } },
      { placeholder: { options: { name: 'body', type: 'body', x: 0.9, y: 5.4, w: 11.5, h: 0.8, fontSize: 18, color: C.text2, align: 'left', valign: 'top', margin: 0 }, text: '' } },
    ],
  });
  pres.defineSlideMaster({
    title: 'CONTENT', background: { color: C.background1 },
    margin: [1.5, 0.6, 0.8, 0.6],
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.4, w: 10.6, h: 0.9, fontSize: 32, bold: true, color: C.text1, align: 'left', valign: 'middle', margin: 0 }, text: '' } },
      { image: { data: logo, x: 11.43, y: 0.52, w: 1.3, h: 0.428 } },
      { text: { text: FOOT, options: { x: 0.6, y: 6.98, w: 10.5, h: 0.3, fontSize: 10, color: C.text2, margin: 0 } } },
    ],
    slideNumber: { x: 12.13, y: 6.98, w: 0.6, h: 0.3, fontSize: 10, color: C.text2, align: 'right' },
  });

  const content = (section, title, notes) => {
    const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: section });
    s.addText(title, { placeholder: 'title' });
    s.addNotes(notes);
    return s;
  };
  const card = (s, x, y, w, h, name) => s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: C.background2, width: 0 }, objectName: name });
  const text = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, margin: 0, color: C.text1, valign: 'top', fontSize: 15 }, o));
  const bullets = (s, items, o) => s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    Object.assign({ isTextBox: true, margin: 0, color: C.text1, valign: 'top', fontSize: 15, paraSpaceAfter: 8 }, o));
  const axis = () => ({ catAxisLabelColor: HEX.dk2, valAxisLabelColor: HEX.dk2, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
    catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, dataLabelFontFace: '+mn-lt', dataLabelFontSize: 12, legendFontFace: '+mn-lt', legendFontSize: 12,
    legendColor: HEX.dk2, valGridLine: { color: GRID, size: 0.75 }, catGridLine: { style: 'none' } });

  // ---- 1. Title -------------------------------------------------------------------------------
  pres.addSection({ title: 'Summary' });
  let s = pres.addSlide({ masterName: 'TITLE', sectionTitle: 'Summary' });
  s.addText('What it costs to make bright gum, and what to charge', { placeholder: 'title' });
  s.addText('Cost and pricing study · November 2026 · Planning estimates, not supplier quotes', { placeholder: 'body' });
  s.addNotes('This study estimates what it costs to develop, test, make and package bright gum, and what price makes it profitable. Every number is a planning estimate from public price lists and listings, not a quote.');

  // ---- 2. Short answer ------------------------------------------------------------------------
  s = content('Summary', 'The short answer', `Four numbers to remember. About ${k(tot.typical)} to launch two flavors with a contract manufacturer. About ${d2(L)} to make a carton on the first run, falling to about ${d2(S)} at scale. A shelf price of ${d2(price)}. And about ${k(cap.typical)} if you built your own factory, which is not recommended yet.`);
  const stats = [
    [k(tot.typical), 'Cash to launch with a contract manufacturer', `Range ${k(tot.low)} to ${k(tot.high)}, two flavors`],
    [`${d2(L)} → ${d2(S)}`, 'Cost to make one 15-stick carton', `First run of ${n0(M.launch_run)} cartons, then at ${n0(M.scale_run)}+`],
    [d2(price), 'Suggested shelf price', 'Workable range $2.49 to $3.49'],
    [k(cap.typical), 'To build your own small factory instead', `Range ${k(cap.low)} to ${k(cap.high)}. Not recommended yet.`],
  ];
  stats.forEach(([big, label, sub], i) => {
    const x = 0.6 + (i % 2) * 6.215, y = 1.65 + Math.floor(i / 2) * 2.6;
    card(s, x, y, 5.915, 2.3, `Stat card ${i + 1}`);
    text(s, big, { x: x + 0.35, y: y + 0.3, w: 5.2, h: 0.85, fontSize: 44, bold: true, color: C.accent1, objectName: `Stat ${i + 1} value` });
    text(s, label, { x: x + 0.35, y: y + 1.2, w: 5.2, h: 0.4, fontSize: 18, bold: true, objectName: `Stat ${i + 1} label` });
    text(s, sub, { x: x + 0.35, y: y + 1.65, w: 5.2, h: 0.4, fontSize: 14, color: C.text2, objectName: `Stat ${i + 1} range` });
  });

  // ---- 3. Co-packer vs factory ----------------------------------------------------------------
  pres.addSection({ title: 'Costs' });
  s = content('Costs', 'Hire a manufacturer; don’t build a factory', `A contract manufacturer already owns the gum line, so you pay per carton. Your own line costs about ${k(cap.typical)} to set up and about ${d0(M.factory_monthly_total)} a month to run. It only pays off above roughly ${(fb.at_launch_fee / 1e6).toFixed(1)} to ${(fb.at_scale_fee / 1e6).toFixed(1)} million cartons a year, close to the most a small line can make.`);
  const cols = [
    ['Contract manufacturer', C.accent1, [`About ${k(tot.typical)} to launch two flavors`, 'No equipment to buy', `You pay about ${d2(cg.launch.Manufacturing)} a carton for making and packing, falling to about ${d2(cg.scale.Manufacturing)}`, 'Typical minimum order: 5,000 to 50,000 cartons', 'They carry the food-safety certification']],
    ['Your own factory', C.text2, [`About ${k(cap.typical)} before you make a stick`, `About ${d0(M.factory_monthly_total)} a month in rent, staff and utilities`, `Pays off above ${(fb.at_launch_fee / 1e6).toFixed(1)} to ${(fb.at_scale_fee / 1e6).toFixed(1)} million cartons a year`, `A small line tops out near ${(M.factory_capacity_year / 1e6).toFixed(1)} million cartons a year`, 'You carry the certification and the risk']],
  ];
  cols.forEach(([head, color, items], i) => {
    const x = 0.6 + i * 6.215;
    card(s, x, 1.65, 5.915, 4.2, `Option card ${i + 1}`);
    text(s, head, { x: x + 0.35, y: 1.9, w: 5.2, h: 0.5, fontSize: 22, bold: true, color, objectName: `Option ${i + 1} heading` });
    bullets(s, items, { x: x + 0.35, y: 2.6, w: 5.2, h: 3.1, fontSize: 18, paraSpaceAfter: 10, objectName: `Option ${i + 1} points` });
  });
  text(s, 'Recommendation: start with a contract manufacturer and revisit your own line once sales pass about a million cartons a year.', { x: 0.6, y: 6.1, w: 12.13, h: 0.6, fontSize: 16, bold: true, objectName: 'Recommendation' });

  // ---- 4. Startup costs -----------------------------------------------------------------------
  s = content('Costs', `Launching two flavors takes about ${d0(Math.round(tot.typical / 1000) * 1000)}`, `One-time costs to develop, test and launch two flavors. The first production run is the largest item and you earn it back as you sell. The whitening study is the largest test, and it is only needed to print Whitening on the box. Likely range: ${k(tot.low)} to ${k(tot.high)}.`);
  const short = { 'Formula development with the manufacturer': 'Formula development', 'Pilot batches (2 flavors)': 'Pilot batches', 'Lab tests: nutrition, sugar alcohols, microbes, heavy metals': 'Lab tests', 'Shelf-life study': 'Shelf-life study', 'Whitening (stain-removal) study': 'Whitening study', 'Flavor-duration and taste panel': 'Flavor and taste panel', 'Label review and nutrition panel': 'Label review', 'Trademark: name and logo': 'Trademark', 'LLC, barcodes, first-year insurance': 'LLC, barcodes, insurance', 'Printing plates and carton die': 'Plates and carton die', 'Launch marketing: samples, campus events, video': 'Launch marketing' };
  const items = M.startup_items.map((r) => [short[r.item], r.typical]);
  items.push(['First production run', M.first_run.typical]);
  items.push(['Contingency (15%)', (M.startup_subtotal.typical + M.first_run.typical) * M.contingency]);
  items.sort((a, b) => a[1] - b[1]);
  s.addChart(pres.charts.BAR, [{ name: 'Typical cost', labels: items.map((r) => r[0]), values: items.map((r) => Math.round(r[1] / 100) * 100) }], Object.assign(axis(), {
    x: 0.6, y: 1.5, w: 7.6, h: 5.3, barDir: 'bar', chartColors: [HEX.accent1], showLegend: false, showValue: true, dataLabelPosition: 'outEnd',
    dataLabelFormatCode: '$#,##0', dataLabelColor: HEX.dk1, valAxisHidden: true, valGridLine: { style: 'none' }, barGapWidthPct: 45, objectName: 'Startup cost chart',
    showTitle: true, title: 'Typical one-time cost by item', titleFontFace: '+mn-lt', titleFontSize: 13, titleColor: HEX.dk2,
  }));
  card(s, 8.5, 1.65, 4.23, 5.0, 'Startup notes card');
  text(s, `${k(tot.low)} to ${k(tot.high)}`, { x: 8.8, y: 1.9, w: 3.7, h: 0.6, fontSize: 30, bold: true, color: C.accent1, objectName: 'Startup range' });
  text(s, 'Likely range for the total', { x: 8.8, y: 2.5, w: 3.7, h: 0.35, fontSize: 14, color: C.text2, objectName: 'Startup range label' });
  bullets(s, ['About a third is the first production run, which you earn back as it sells', 'The whitening study can wait until demand is proven', 'A cheaper first step: a 1,000-box test using a maker’s existing gum in your packaging, for a few thousand dollars'],
    { x: 8.8, y: 3.1, w: 3.7, h: 3.4, fontSize: 16, paraSpaceAfter: 10, objectName: 'Startup notes' });

  // ---- 5. Cost per carton ---------------------------------------------------------------------
  s = content('Costs', `One carton costs ${d2(L)} now, ${d2(S)} at scale`, `The cost of one 15-stick carton made by a contract manufacturer. On a first run of ${n0(M.launch_run)} cartons it is about ${d2(L)}. At ${n0(M.scale_run)} cartons or more, with bulk ingredient prices, it falls to about ${d2(S)}. Likely ranges are $1.00 to $1.90 on the first run and $0.55 to $1.00 at scale.`);
  const parts = ['Ingredients', 'Manufacturing', 'Packaging'];
  const pname = { Ingredients: 'Ingredients', Manufacturing: 'Manufacturer fee and run setup', Packaging: 'Packaging' };
  const part = (o, p) => (p === 'Manufacturing' ? o.Manufacturing + o['Run setup'] : o[p]);
  s.addChart(pres.charts.BAR, parts.map((p) => ({ name: pname[p], labels: [`First run (${n0(M.launch_run)} cartons)`, `At scale (${n0(M.scale_run)}+)`], values: [part(cg.launch, p), part(cg.scale, p)].map((v) => Math.round(v * 100) / 100) })), Object.assign(axis(), {
    x: 0.6, y: 1.5, w: 7.2, h: 5.3, barDir: 'col', barGrouping: 'stacked', chartColors: [HEX.accent1, HEX.accent2, HEX.accent3],
    showLegend: true, legendPos: 'b', showValue: true, dataLabelPosition: 'ctr', dataLabelFormatCode: '$0.00', dataLabelColor: 'FFFFFF',
    valAxisLabelFormatCode: '$0.00', barGapWidthPct: 60, objectName: 'Cost per carton chart',
    showTitle: true, title: 'Cost to make one carton', titleFontFace: '+mn-lt', titleFontSize: 13, titleColor: HEX.dk2,
  }));
  card(s, 8.1, 1.65, 4.63, 5.0, 'Carton cost notes card');
  text(s, 'What drives it', { x: 8.4, y: 1.9, w: 4.0, h: 0.45, fontSize: 20, bold: true, color: C.accent1, objectName: 'Carton cost heading' });
  bullets(s, [`Ingredients are only ${d2(cg.launch.Ingredients)} of the ${d2(L)}`, 'The manufacturer’s fee and packaging are about two-thirds', 'Bigger runs cut every part: bulk ingredients, cheaper cartons, lower fee per carton', 'Electricity is well under 1 cent a carton'],
    { x: 8.4, y: 2.5, w: 4.0, h: 4.0, fontSize: 17, paraSpaceAfter: 10, objectName: 'Carton cost points' });

  // ---- 6. Xylitol -----------------------------------------------------------------------------
  s = content('Costs', 'Xylitol barely changes the cost', 'Whole-carton cost for the three recipes. The no-xylitol recipe costs about the same as the standard xylitol recipe and about 5 cents less than the long-lasting xylitol recipe. The better reasons to drop xylitol are easier manufacturing and a more stable stick, not cost.');
  const recs = Object.keys(M.cogs);
  s.addChart(pres.charts.BAR, [
    { name: 'First run', labels: recs, values: recs.map((r) => Math.round(M.cogs[r].launch_total * 100) / 100) },
    { name: 'At scale', labels: recs, values: recs.map((r) => Math.round(M.cogs[r].scale_total * 100) / 100) },
  ], Object.assign(axis(), {
    x: 0.6, y: 1.5, w: 7.2, h: 5.3, barDir: 'col', barGrouping: 'clustered', chartColors: [HEX.accent1, HEX.accent4], showLegend: true, legendPos: 'b',
    showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '$0.00', dataLabelColor: HEX.dk1, valAxisLabelFormatCode: '$0.00', valAxisMinVal: 0,
    barGapWidthPct: 70, objectName: 'Recipe cost chart', showTitle: true, title: 'Cost per carton by recipe', titleFontFace: '+mn-lt', titleFontSize: 13, titleColor: HEX.dk2,
  }));
  card(s, 8.1, 1.65, 4.63, 5.0, 'Xylitol notes card');
  text(s, 'About 5¢', { x: 8.4, y: 1.9, w: 4.0, h: 0.75, fontSize: 40, bold: true, color: C.accent1, objectName: 'Xylitol saving' });
  text(s, 'saved per carton by removing xylitol from the long-lasting recipe', { x: 8.4, y: 2.7, w: 4.0, h: 0.7, fontSize: 14, color: C.text2, objectName: 'Xylitol saving label' });
  bullets(s, ['Ingredients are a small share of the total, so swapping one changes little', 'Dropping xylitol makes the gum easier to manufacture and the stick more stable', 'Keeping it keeps the dental story for shoppers who look for xylitol'],
    { x: 8.4, y: 3.6, w: 4.0, h: 2.9, fontSize: 16, paraSpaceAfter: 10, objectName: 'Xylitol points' });

  // ---- 7. Packaging ---------------------------------------------------------------------------
  s = content('Costs', 'Packaging gets cheaper with volume', 'Printed carton prices fall steeply with order size: roughly $0.44 to $1.00 each at 1,000, down to $0.09 to $0.22 at 100,000. The chart shows the middle of each range. Wrapper material is cheap either way; the hurdles for foil are a large minimum order and printing plates.');
  s.addChart(pres.charts.BAR, [{ name: 'Price per printed carton (middle of range)', labels: ['1,000', '10,000', '50,000', '100,000'], values: [0.72, 0.35, 0.24, 0.16] }], Object.assign(axis(), {
    x: 0.6, y: 1.5, w: 6.4, h: 5.3, barDir: 'col', chartColors: [HEX.accent3], showLegend: false, showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '$0.00',
    dataLabelColor: HEX.dk1, valAxisLabelFormatCode: '$0.00', barGapWidthPct: 70, showCatAxisTitle: true, catAxisTitle: 'Cartons ordered', catAxisTitleFontFace: '+mn-lt', catAxisTitleColor: HEX.dk2, catAxisTitleFontSize: 12,
    objectName: 'Carton price chart', showTitle: true, title: 'Price per printed carton (middle of range)', titleFontFace: '+mn-lt', titleFontSize: 13, titleColor: HEX.dk2,
  }));
  const wraps = [
    ['Foil-lined wrappers', ['About 1 to 3 cents a carton in material', 'Minimum order of 300 to 500 kg, enough for about 100,000 cartons', 'Printing plates: $200 to $800 per color']],
    ['Plain paper, message inside', ['Saves a cent or two a carton at most', 'Smaller minimum orders; digital printing needs no plates', 'Best for many different messages; add one sealed inner pack per carton']],
  ];
  wraps.forEach(([head, pts], i) => {
    const y = 1.65 + i * 2.6;
    card(s, 7.3, y, 5.43, 2.4, `Wrapper card ${i + 1}`);
    text(s, head, { x: 7.6, y: y + 0.2, w: 4.9, h: 0.4, fontSize: 18, bold: true, color: C.accent1, objectName: `Wrapper ${i + 1} heading` });
    bullets(s, pts, { x: 7.6, y: y + 0.7, w: 4.9, h: 1.6, fontSize: 14, paraSpaceAfter: 5, objectName: `Wrapper ${i + 1} points` });
  });

  // ---- 8. Own factory -------------------------------------------------------------------------
  s = content('Costs', `Your own factory costs about ${r0(cap.typical)}`, `Set-up cost for a small imported gum line in rented space, with humidity control and food-safety certification. Running it costs about ${d0(M.factory_monthly_total)} a month. Equipment prices are overseas asking prices before freight and duty, so treat them as the weakest numbers in the study.`);
  const hdr = (t, align) => ({ text: t, options: { bold: true, color: C.text2, fontSize: 12, align: align || 'left', border: [{ type: 'none' }, { type: 'none' }, { type: 'solid', pt: 1, color: HEX.dk1 }, { type: 'none' }] } });
  const cell = (t, o) => ({ text: t, options: Object.assign({ color: C.text1, fontSize: 13, border: [{ type: 'none' }, { type: 'none' }, { type: 'solid', pt: 0.5, color: GRID }, { type: 'none' }] }, o || {}) });
  const rows = [[hdr('Set-up cost'), hdr('Low', 'right'), hdr('Typical', 'right'), hdr('High', 'right')]];
  M.factory_capital.forEach((r) => rows.push([cell(r.item), cell(d0(r.low), { align: 'right' }), cell(d0(r.typical), { align: 'right', bold: true }), cell(d0(r.high), { align: 'right' })]));
  rows.push([cell('Total before you make a stick', { bold: true }), cell(d0(cap.low), { align: 'right', bold: true }), cell(d0(cap.typical), { align: 'right', bold: true, color: C.accent1 }), cell(d0(cap.high), { align: 'right', bold: true })]);
  s.addTable(rows, { x: 0.6, y: 1.65, w: 7.7, colW: [4.1, 1.2, 1.2, 1.2], rowH: 0.52, valign: 'middle', margin: [0, 0.08, 0, 0], objectName: 'Factory set-up table' });
  const fstats = [[`${d0(M.factory_monthly_total)}`, 'a month to run: rent, six staff, utilities, insurance'], [`${(fb.at_launch_fee / 1e6).toFixed(1)}–${(fb.at_scale_fee / 1e6).toFixed(1)}M`, 'cartons a year needed just to cover running costs'], [`${(M.factory_capacity_year / 1e6).toFixed(1)}M`, 'cartons a year is the most a small line makes']];
  fstats.forEach(([big, label], i) => {
    const y = 1.65 + i * 1.72;
    card(s, 8.6, y, 4.13, 1.52, `Factory stat card ${i + 1}`);
    text(s, big, { x: 8.85, y: y + 0.15, w: 3.7, h: 0.6, fontSize: 30, bold: true, color: C.accent1, objectName: `Factory stat ${i + 1}` });
    text(s, label, { x: 8.85, y: y + 0.8, w: 3.7, h: 0.6, fontSize: 14, color: C.text2, objectName: `Factory stat ${i + 1} label` });
  });

  // ---- 9. Shelf prices ------------------------------------------------------------------------
  pres.addSection({ title: 'Pricing and profit' });
  s = content('Pricing and profit', `bright fits the premium tier at ${d2(price)}`, 'Shelf prices seen at US retailers in November 2026, shown per piece. Mainstream gum is 10 to 12 cents a piece. Premium and natural gums are 16 to 20 cents. Functional gums are over 30 cents. At $2.99 for 15 sticks, bright is 20 cents a piece, level with other premium gums.');
  const shelf = M.shelf.map((r) => [`${r.name} (${d2(r.price)})`, r.per_piece * 100, false]);
  shelf.push([`bright 15 (${d2(price)})`, price / 15 * 100, true]);
  shelf.sort((a, b) => a[1] - b[1]);
  s.addChart(pres.charts.BAR, [{ name: 'Cents per piece', labels: shelf.map((r) => r[0]), values: shelf.map((r) => Math.round(r[1])) }], Object.assign(axis(), {
    x: 0.6, y: 1.5, w: 7.6, h: 5.3, barDir: 'bar', chartColors: shelf.map((r) => (r[2] ? HEX.accent1 : 'AEB6C9')), showLegend: false, showValue: true, dataLabelPosition: 'outEnd',
    dataLabelFormatCode: '0"¢"', dataLabelColor: HEX.dk1, valAxisHidden: true, valGridLine: { style: 'none' }, barGapWidthPct: 45, objectName: 'Shelf price chart',
    showTitle: true, title: 'Shelf price per piece, in cents', titleFontFace: '+mn-lt', titleFontSize: 13, titleColor: HEX.dk2,
  }));
  card(s, 8.5, 1.65, 4.23, 5.0, 'Price notes card');
  text(s, '$2.49 to $3.49', { x: 8.8, y: 1.9, w: 3.7, h: 0.6, fontSize: 30, bold: true, color: C.accent1, objectName: 'Price range' });
  text(s, 'What you could charge', { x: 8.8, y: 2.5, w: 3.7, h: 0.35, fontSize: 14, color: C.text2, objectName: 'Price range label' });
  bullets(s, ['Mainstream packs: $1.39 to $1.79', 'Premium and natural packs: $2.49 to $2.99', 'Functional gum: about $3.99', 'Above $3.49, shoppers expect a stronger health benefit'],
    { x: 8.8, y: 3.1, w: 3.7, h: 3.4, fontSize: 16, paraSpaceAfter: 10, objectName: 'Price notes' });

  // ---- 10. Channels ---------------------------------------------------------------------------
  s = content('Pricing and profit', 'Where you sell decides your profit', `Profit per carton at a ${d2(price)} shelf price. A store keeps about 40 percent of the shelf price. A distributor, promotions and a broker take about another third of the rest. On the first run you only make money selling directly. Through a distributor you lose about ${d2(-ch[DIST].margin_launch)} a carton until costs fall.`);
  const names = Object.keys(ch);
  const cshort = { [INPERSON]: 'In person', [DIRECT]: 'Direct to local stores', [ONLINE]: 'Online 6-pack', 'Small shops through Faire': 'Small shops (Faire)', [DIST]: 'Distributor to chains' };
  s.addChart(pres.charts.BAR, [
    { name: 'First run', labels: names.map((n) => cshort[n]), values: names.map((n) => Math.round(ch[n].margin_launch * 100) / 100) },
    { name: 'At scale', labels: names.map((n) => cshort[n]), values: names.map((n) => Math.round(ch[n].margin_scale * 100) / 100) },
  ], Object.assign(axis(), {
    x: 0.6, y: 1.5, w: 7.9, h: 5.3, barDir: 'col', barGrouping: 'clustered', chartColors: [HEX.accent1, HEX.accent4], showLegend: true, legendPos: 'b',
    showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '$0.00;-$0.00', dataLabelColor: HEX.dk1, valAxisLabelFormatCode: '$0.00;-$0.00', catAxisLabelPos: 'low',
    barGapWidthPct: 60, objectName: 'Channel profit chart', showTitle: true, title: `Profit per carton at ${d2(price)}`, titleFontFace: '+mn-lt', titleFontSize: 13, titleColor: HEX.dk2,
  }));
  card(s, 8.8, 1.65, 3.93, 5.0, 'Channel notes card');
  text(s, 'What you need to charge', { x: 9.05, y: 1.9, w: 3.45, h: 0.45, fontSize: 18, bold: true, color: C.accent1, objectName: 'Needed price heading' });
  bullets(s, [`Direct to stores: at least ${d2(M.need[DIRECT].breakeven_launch)} to break even on the first run, ${d2(M.need[DIRECT].breakeven_scale)} at scale`, `Through a distributor: at least ${d2(M.need[DIST].breakeven_launch)} on the first run, ${d2(M.need[DIST].breakeven_scale)} at scale`, 'Single cartons don’t work online: postage costs more than the gum. Sell 6-packs.'],
    { x: 9.05, y: 2.5, w: 3.45, h: 4.0, fontSize: 16, paraSpaceAfter: 10, objectName: 'Needed price points' });

  // ---- 11. Scenarios --------------------------------------------------------------------------
  s = content('Pricing and profit', 'Profit needs volume', `Two example years at ${d2(price)}. Year one sells ${n0(y1.cartons)} cartons directly and roughly breaks even on running costs. At ${n0(y2.cartons)} cartons a year through regional retail, the business makes about ${r0(y2.profit)} before paying the founder. Neither includes the one-time launch costs.`);
  const money = (v) => (v < 0 ? '−' : '') + r0(Math.abs(v));
  const yrs = [['Year 1: campus launch', y1, '40% in person, 40% local stores, 20% online'], ['At scale: regional retail', y2, '60% distributor, 30% local stores, 10% online']];
  yrs.forEach(([head, y, mix], i) => {
    const x = 0.6 + i * 6.215;
    card(s, x, 1.65, 5.915, 5.0, `Scenario card ${i + 1}`);
    text(s, head, { x: x + 0.35, y: 1.85, w: 5.2, h: 0.45, fontSize: 20, bold: true, color: C.accent1, objectName: `Scenario ${i + 1} heading` });
    text(s, mix, { x: x + 0.35, y: 2.32, w: 5.2, h: 0.35, fontSize: 13, color: C.text2, objectName: `Scenario ${i + 1} mix` });
    const lines = [['Cartons sold', n0(y.cartons)], ['Kept per carton, on average', d2(y.avg_net)], ['Cost per carton', d2(y.unit_cost)], ['Sales', r0(y.revenue)], ['Marketing and running costs', r0(y.marketing + y.overhead)], ['Profit before paying yourself', money(y.profit)], ['Cartons needed to break even', n0(Math.round(y.breakeven_cartons / 100) * 100)]];
    const trows = lines.map(([a, b], j) => [
      { text: a, options: { color: C.text1, fontSize: 14, bold: j === 5, border: [{ type: 'none' }, { type: 'none' }, { type: 'solid', pt: 0.5, color: GRID }, { type: 'none' }] } },
      { text: b, options: { color: j === 5 ? C.accent1 : C.text1, fontSize: 14, bold: j === 5, align: 'right', border: [{ type: 'none' }, { type: 'none' }, { type: 'solid', pt: 0.5, color: GRID }, { type: 'none' }] } },
    ]);
    s.addTable(trows, { x: x + 0.35, y: 2.85, w: 5.2, colW: [3.6, 1.6], rowH: 0.5, valign: 'middle', margin: [0, 0, 0, 0], objectName: `Scenario ${i + 1} table` });
  });

  // ---- 12. Confidence and next steps ----------------------------------------------------------
  pres.addSection({ title: 'Next steps' });
  s = content('Next steps', 'How solid the numbers are, and next steps', 'Shelf prices and published fees are reliable. Ingredient and packaging prices are fair. Manufacturer fees, equipment prices and the whitening study are the weakest, because nobody publishes them. Three manufacturer quotes will replace the weakest numbers. Most supplier pages could not be opened during research, so prices came from search-result extracts.');
  const conf = [
    ['Good', C.accent3, 'Shelf prices of other gums; lab test, trademark, barcode and LLC fees'],
    ['Fair', C.accent2, 'Ingredient prices; store and distributor margins; carton and wrapper prices'],
    ['Weak', C.accent6, 'Manufacturer’s fee and minimum order; equipment prices; whitening study; factory fit-out'],
  ];
  card(s, 0.6, 1.65, 5.915, 5.0, 'Confidence card');
  text(s, 'How reliable each input is', { x: 0.95, y: 1.85, w: 5.2, h: 0.45, fontSize: 20, bold: true, color: C.accent1, objectName: 'Confidence heading' });
  conf.forEach(([lvl, color, what], i) => {
    const y = 2.55 + i * 1.3;
    s.addShape(pres.ShapeType.ellipse, { x: 0.95, y: y + 0.05, w: 0.26, h: 0.26, fill: { color }, line: { color, width: 0 }, objectName: `Confidence dot ${i + 1}` });
    text(s, lvl, { x: 1.35, y, w: 1.2, h: 0.4, fontSize: 17, bold: true, objectName: `Confidence level ${i + 1}` });
    text(s, what, { x: 1.35, y: y + 0.4, w: 4.85, h: 0.8, fontSize: 15, color: C.text2, objectName: `Confidence items ${i + 1}` });
  });
  card(s, 6.815, 1.65, 5.915, 5.0, 'Next steps card');
  text(s, 'Next steps', { x: 7.165, y: 1.85, w: 5.2, h: 0.45, fontSize: 20, bold: true, color: C.accent1, objectName: 'Next steps heading' });
  bullets(s, ['Get three manufacturer quotes at their minimum, 50,000 and 250,000 cartons', 'Ask about the development fee, formula ownership and wrapper minimum orders', 'Get a custom quote for the 3.00 x 2.40 x 0.35 in carton', 'Confirm import duty on xylitol with a customs broker', 'Put the quotes into the model and rebuild this study'],
    { x: 7.165, y: 2.55, w: 5.2, h: 3.9, fontSize: 17, paraSpaceAfter: 10, objectName: 'Next steps points' });

  await pres.writeFile({ fileName: OUT });
  if (SKILL) {
    const { applyTheme } = require(path.join(SKILL, 'scripts', 'apply_theme.js'));
    await applyTheme(OUT, THEME);
  }
  console.log('wrote', OUT);
})();
