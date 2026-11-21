"""Build the bright gum carton labels for every flavor.

Each flavor's color is used for the logo's eye, the flavor name and the
accent text, so the eye always matches the flavor.

Dark boxes mark the caffeinated line: inverted colors (white wordmark on ink),
with the flavor name allowed to use two colors (see Cotton Candy).

Two versions of the cartons, written to separate files:
  no-xylitol (main)    -> packaging/bright-cartons.html
  xylitol (alternative) -> packaging/xylitol/bright-cartons-xylitol.html

Usage:  python3 packaging/build_cartons.py [no-xylitol|xylitol|all]
Then:   node packaging/render.js   (HTML -> print PDF and PNG previews)
"""
import json
import random
import sys
from pathlib import Path

INK = "#0D1117"
OUT = Path(__file__).parent

FLAVORS = [
    {"id": "peppermint", "name": "Peppermint", "color": "#1428DC", "sodium": ("15mg", "1%")},
    {"id": "spearmint", "name": "Spearmint", "color": "#046A4A", "sodium": ("15mg", "1%")},
    {"id": "blue-raspberry", "name": "Blue Raspberry", "color": "#0085C7", "sodium": ("15mg", "1%")},
    {"id": "raspberry", "name": "Raspberry", "color": "#C2185B", "sodium": ("15mg", "1%")},
    {"id": "watermelon", "name": "Watermelon", "color": "#D62839", "sodium": ("15mg", "1%")},
    {"id": "pickle", "name": "Pickle", "color": "#5B7046", "sodium": ("25mg", "1%")},
    # Caffeinated line: dark box. Eye is sky blue; "Cotton" sky blue, "Candy" pink.
    {"id": "cotton-candy", "name": "Cotton Candy", "color": "#6EC6F5", "sodium": ("15mg", "1%"),
     "theme": "dark", "caffeine": "40 mg",
     "parts": [("Cotton", "#6EC6F5"), ("Candy", "#FF8DC7")]},
    # Caffeinated mints. Lighter blue and green than the regular boxes so they read on the dark box.
    {"id": "peppermint-caffeinated", "name": "Peppermint", "color": "#6C8CFF", "sodium": ("15mg", "1%"),
     "theme": "dark", "caffeine": "40 mg"},
    {"id": "spearmint-caffeinated", "name": "Spearmint", "color": "#3CC08E", "sodium": ("15mg", "1%"),
     "theme": "dark", "caffeine": "40 mg"},
]

DARK_BG = "#1E2126"      # graphite grey (caffeinated line)
DARK_INK = "#F4F6FB"
DARK_LINE = "#353A42"     # swirl lines on the dark box
CAFFEINE_NOTE = ("Not recommended for children, people who are pregnant or nursing, or anyone "
                 "sensitive to caffeine. Limit 5 pieces a day.")

X = "Xylitol, Gum Base, Sorbitol, Calcium Carbonate, Glycerin, "
N = "Sorbitol, Gum Base, Mannitol, Glycerin, Calcium Carbonate, "
N_END = "Sunflower Lecithin, Sucralose, Acesulfame Potassium."

MAIN = "no-xylitol"     # the main version; xylitol is kept as an alternative

VARIANTS = {
    "xylitol": {
        "dir": OUT / "xylitol", "stem": "bright-cartons-xylitol", "sheet": "product/formula-sheets-xylitol.md",
        "front_sub": "XYLITOL", "back_sub": "XYLITOL GUM",
        "back_line": "1 g+ xylitol in every piece.", "calories": "0",
        "ingredients": {
            "peppermint": X + "Natural Flavors, Sodium Tripolyphosphate, Sunflower Lecithin, Sucralose.",
            "spearmint": X + "Natural Flavors, Sodium Tripolyphosphate, Sunflower Lecithin, Sucralose.",
            "blue-raspberry": X + "Natural and Artificial Flavors, Sodium Tripolyphosphate, Malic Acid, "
                              "Sunflower Lecithin, Sucralose.",
            "raspberry": X + "Natural Flavors, Sodium Tripolyphosphate, Malic Acid, Sunflower Lecithin, Sucralose.",
            "watermelon": X + "Natural and Artificial Flavors, Sodium Tripolyphosphate, Malic Acid, "
                          "Sunflower Lecithin, Sucralose.",
            "pickle": X + "Natural Flavors, Sodium Tripolyphosphate, Sodium Bicarbonate, Salt, "
                      "Sunflower Lecithin, Sucralose.",
            "cotton-candy": X + "Natural and Artificial Flavors, Sodium Tripolyphosphate, Caffeine, "
                            "Sunflower Lecithin, Sucralose.",
            "peppermint-caffeinated": X + "Natural Flavors, Sodium Tripolyphosphate, Caffeine, Sunflower Lecithin, Sucralose.",
            "spearmint-caffeinated": X + "Natural Flavors, Sodium Tripolyphosphate, Caffeine, Sunflower Lecithin, Sucralose.",
        },
    },
    "no-xylitol": {
        "dir": OUT, "stem": "bright-cartons",
        "sheet": "product/formula-sheets.md (main)",
        "front_sub": "A MESSAGE IN<br>EVERY WRAPPER", "back_sub": "SUGAR-FREE GUM",
        "back_line": "A positive message inside every wrapper.", "calories": "5",
        "ingredients": {
            "peppermint": N + "Natural Flavors, Sodium Tripolyphosphate, Gum Arabic, " + N_END,
            "spearmint": N + "Natural Flavors, Sodium Tripolyphosphate, Gum Arabic, " + N_END,
            "blue-raspberry": N + "Natural and Artificial Flavors, Gum Arabic, Sodium Tripolyphosphate, "
                              "Malic Acid, " + N_END,
            "raspberry": N + "Natural Flavors, Gum Arabic, Sodium Tripolyphosphate, Malic Acid, " + N_END,
            "watermelon": N + "Natural and Artificial Flavors, Gum Arabic, Sodium Tripolyphosphate, "
                          "Malic Acid, " + N_END,
            "pickle": N + "Natural Flavors, Sodium Tripolyphosphate, Gum Arabic, Sodium Bicarbonate, Salt, " + N_END,
            "cotton-candy": N + "Natural and Artificial Flavors, Sodium Tripolyphosphate, Caffeine, Gum Arabic, " + N_END,
            "peppermint-caffeinated": N + "Natural Flavors, Sodium Tripolyphosphate, Caffeine, Gum Arabic, " + N_END,
            "spearmint-caffeinated": N + "Natural Flavors, Sodium Tripolyphosphate, Caffeine, Gum Arabic, " + N_END,
        },
    },
}


LOGO = json.loads((OUT.parent / "brand" / "logo" / "logo_paths.json").read_text())


def logo(eye, width_in, ink=INK):
    """The bright logo, drawn from the traced artwork in brand/logo/logo_paths.json."""
    _, _, w, h = LOGO["viewBox"]
    return (f'<svg class="logo" viewBox="0 0 {w} {h}" style="width:{width_in}in;height:{width_in / LOGO["ratio"]:.3f}in" '
            f'aria-label="bright logo"><path fill="{ink}" fill-rule="evenodd" d="{LOGO["ink"]}"/>'
            f'<path fill="{eye}" d="{LOGO["eye"]}"/></svg>')


def swirls(stroke="#E3E6EC", stroke2=None, width=0.7):
    """Sweeping background lines, like the mockup. Two colors give a flavor its own look."""
    a, b = [], []
    for i in range(7):
        o = i * 9
        a.append(f'<path d="M-10,{170 + o} C 70,{120 + o} 150,{40 + o * 0.6} 310,{10 + o * 0.5}"/>')
    for i in range(6):
        o = i * 11
        b.append(f'<path d="M{120 + o},250 C {150 + o},170 {210 + o * 0.5},90 310,{60 + o * 0.7}"/>')
    return ('<svg class="swirl" viewBox="0 0 300 240" preserveAspectRatio="none" aria-hidden="true">'
            f'<g fill="none" stroke-width="{width}"><g stroke="{stroke}">{"".join(a)}</g>'
            f'<g stroke="{stroke2 or stroke}">{"".join(b)}</g></g></svg>')


def barcode(seed):
    rnd = random.Random(seed)
    x, bars = 0, []
    while x < 95:
        w = rnd.choice([1, 1, 2, 3])
        if rnd.random() > 0.45:
            bars.append(f'<rect x="{x}" y="0" width="{w}" height="40"/>')
        x += w + rnd.choice([1, 1, 2])
    return f'<svg viewBox="0 0 100 40" class="bars" aria-hidden="true"><g fill="{INK}">{"".join(bars)}</g></svg>'


def is_dark(f):
    return f.get("theme") == "dark"


def flavor_name(f):
    """Flavor name in one color, or in several colors when the flavor defines parts."""
    if "parts" in f:
        sep = "<br>" if f.get("stack") else " "       # stack long two-word names on two lines
        return sep.join(f'<span style="color:{c}">{t}</span>' for t, c in f["parts"])
    return f["name"]


def front(f, v=None):
    v = v or VARIANTS[MAIN]
    dark = is_dark(f)
    badge = (f'<p class="caf"><b>CAFFEINATED</b><span>{f["caffeine"]} per piece</span></p>'
             if f.get("caffeine") else "")
    if dark:      # tint the lines with the flavor's color (or its two colors)
        c1, c2 = (f["parts"][0][1], f["parts"][1][1]) if "parts" in f else (f["color"], f["color"])
        bg = swirls(c1 + "66", c2 + "66", 0.8)
    else:
        bg = swirls("#E3E6EC")
    return f'''<div class="label front{' dark' if dark else ''}" style="--flavor:{f['color']}">
{bg}
<div class="f-top">
  <div class="brand">{logo(f['color'], 1.62, DARK_INK if dark else INK)}<span class="tm">TM</span></div>
  <div class="claims"><b>Whitening</b><b>Sugar-Free</b>{badge}</div>
</div>
<div class="f-bottom">
  <div class="count"><b>15 PK</b><span>{v['front_sub']}</span><em>15 STICKS · NET WT 1.43 OZ (40.5 g)</em></div>
  <div class="flavor"><b>{flavor_name(f)}</b><span>SUGAR-FREE GUM</span></div>
</div>
</div>'''


def back(f, v=None):
    v = v or VARIANTS[MAIN]
    na, na_dv = f["sodium"]
    dark = is_dark(f)
    caf = (f'<p class="xy">{f["caffeine"]} caffeine per piece.</p><p class="warn">{CAFFEINE_NOTE}</p>'
           if f.get("caffeine") else "")
    sub = ("CAFFEINATED " if f.get("caffeine") else "") + v['back_sub']
    return f'''<div class="label back{' dark' if dark else ''}" style="--flavor:{f['color']}">
<div class="b-head">
  <div class="brand small">{logo(f['color'], 0.95, DARK_INK if dark else INK)}<span class="tm">TM</span></div>
  <p class="sub">{f['name'].upper()} &nbsp;|&nbsp; {sub}</p>
</div>
<div class="b-body">
  <div class="b-left">
    <p class="h">INGREDIENTS</p>
    <p class="ing">{v['ingredients'][f['id']]}</p>
    <p class="xy">{v['back_line']}</p>
    {caf}
    <div class="b-foot"><p class="web">BrightGumCo.com</p>
    <div class="upc">{barcode(f['id'])}<span>SAMPLE 0 00000 00000 0</span></div></div>
  </div>
  <div class="nf">
    <p class="nf-t">Nutrition Facts</p>
    <p class="nf-s">Serving size <b>1 piece (2.7g)</b></p>
    <div class="nf-cal"><b>Calories</b><b>{v['calories']}</b></div>
    <p class="nf-dv">% Daily Value*</p>
    <div class="r"><span><b>Total Fat</b> 0g</span><b>0%</b></div>
    <div class="r"><span><b>Sodium</b> {na}</span><b>{na_dv}</b></div>
    <div class="r"><span><b>Total Carb.</b> 2g</span><b>1%</b></div>
    <div class="r in"><span>Total Sugars 0g</span><span></span></div>
    <div class="r in"><span>Sugar Alcohol 2g</span><span></span></div>
    <div class="r"><span><b>Protein</b> 0g</span><span></span></div>
    <div class="r thick"><span>Calcium 40mg</span><span>3%</span></div>
    <p class="nf-n">Not a significant source of saturated fat, trans fat, cholesterol, fiber, added sugars, vitamin D, iron and potassium. *%DV = %Daily Value. <b>Draft: confirm by lab analysis.</b></p>
  </div>
</div>
</div>'''


CSS = f"""
@page {{ size: 8.5in 11in; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Lato', 'Inter', Arial, sans-serif; color: {INK}; background: #fff; }}
.page {{ width: 8.5in; height: 11in; padding: 0.75in; position: relative; page-break-after: always; }}
.page:last-child {{ page-break-after: auto; }}
.pt {{ font-size: 16pt; font-weight: 900; letter-spacing: 0.01em; }}
.pt i {{ font-style: normal; }}
.ps {{ font-size: 9.5pt; margin-top: 4pt; }}
.pn {{ font-size: 8pt; color: #777; margin-top: 3pt; }}
.pair {{ display: flex; gap: 0.5in; margin-top: 2.6in; justify-content: center; }}
.stack {{ display: grid; grid-template-columns: 3in 3in; gap: 0.22in 0.4in; justify-content: center; margin-top: 0.3in; }}
.cap {{ font-size: 8.5pt; font-weight: 700; margin-top: 7pt; }}
.calib {{ position: absolute; left: 0.75in; bottom: 1.05in; display: flex; align-items: center; gap: 10pt; font-size: 8pt; font-weight: 700; }}
.calib i {{ display: block; width: 1in; height: 7pt; border-left: 1px solid {INK}; border-right: 1px solid {INK}; position: relative; }}
.calib i::after {{ content: ""; position: absolute; left: 0; right: 0; top: 3pt; border-top: 1px solid {INK}; }}
.howto {{ position: absolute; left: 0.75in; bottom: 0.6in; font-size: 8.5pt; line-height: 1.4; }}

.label {{ width: 3in; height: 2.4in; border: 0.75pt solid #777; position: relative; overflow: hidden; background: #fff; }}
.swirl {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
.brand {{ display: flex; align-items: flex-end; gap: 1pt; }}
.small .tm {{ margin-bottom: 0; font-size: 3pt; }}
.tm {{ font-size: 3.6pt; font-weight: 700; border: 0.4pt solid {INK}; border-radius: 50%; padding: 0.6pt 0.5pt; margin-bottom: -4pt; }}

.front {{ padding: 0.2in 0.17in 0.16in; display: flex; flex-direction: column; justify-content: space-between; }}
.f-top, .f-bottom {{ position: relative; display: flex; justify-content: space-between; }}
.f-top {{ align-items: flex-start; }}
.f-bottom {{ align-items: flex-end; }}
.claims {{ display: flex; flex-direction: column; align-items: flex-end; text-align: right; }}
.claims b {{ font-size: 10pt; font-weight: 900; line-height: 1.15; }}
.claims span {{ font-size: 5.5pt; line-height: 1.25; margin-top: 3pt; color: #3A4150; }}
.count b {{ display: block; font-size: 17pt; font-weight: 900; line-height: 1; }}
.count span {{ display: block; font-size: 6.5pt; font-weight: 900; margin-top: 2pt; letter-spacing: 0.04em; line-height: 1.2; }}
.count em {{ display: block; font-style: normal; font-size: 5pt; margin-top: 3pt; color: #3A4150; }}
.flavor {{ text-align: right; }}
.flavor b {{ display: block; font-size: 15pt; font-weight: 900; color: var(--flavor); line-height: 1.05; }}
.flavor > span {{ display: block; font-size: 5.5pt; font-weight: 900; letter-spacing: 0.08em; margin-top: 2pt; }}

.back {{ padding: 0.13in 0.15in 0.1in; display: flex; flex-direction: column; }}
.b-head {{ border-bottom: 0.5pt solid #D5D9E0; padding-bottom: 3pt; }}
.sub {{ font-size: 6.6pt; font-weight: 900; color: var(--flavor); margin-top: 3pt; letter-spacing: 0.02em; }}
.b-body {{ display: flex; gap: 0.1in; margin-top: 4pt; flex: 1; }}
.b-foot {{ margin-top: auto; display: flex; flex-direction: column; gap: 2pt; }}
.b-left {{ flex: 1; display: flex; flex-direction: column; gap: 2.2pt; }}
.b-left .h {{ font-size: 5.6pt; font-weight: 900; }}
.ing {{ font-size: 5.1pt; line-height: 1.25; }}
.xy {{ font-size: 5.6pt; font-weight: 900; color: var(--flavor); }}
.warn {{ font-size: 4.6pt; line-height: 1.25; color: #2A303C; }}
.web {{ font-size: 5.8pt; font-weight: 900; color: var(--flavor); }}
.upc {{ margin-top: 2pt; }}
.bars {{ width: 0.85in; height: 0.26in; display: block; }}
.upc span {{ font-size: 3.8pt; font-weight: 700; }}
.nf {{ width: 1.22in; border: 0.7pt solid {INK}; padding: 2.5pt 3pt; align-self: flex-start; }}
.nf p, .nf div {{ font-size: 4.8pt; line-height: 1.3; }}
.nf-t {{ font-size: 8.6pt !important; font-weight: 900; line-height: 1 !important; border-bottom: 0.5pt solid {INK}; padding-bottom: 1.5pt; }}
.nf-s {{ border-bottom: 2.2pt solid {INK}; padding: 1pt 0 1.5pt; }}
.nf-cal {{ display: flex; justify-content: space-between; font-size: 7pt !important; border-bottom: 1.2pt solid {INK}; padding: 0.5pt 0; }}
.nf-dv {{ text-align: right; font-weight: 700; border-bottom: 0.4pt solid {INK}; }}
.r {{ display: flex; justify-content: space-between; border-bottom: 0.4pt solid {INK}; }}
.r.in span:first-child {{ padding-left: 5pt; }}
.r.thick {{ border-top: 1.6pt solid {INK}; }}
.nf-n {{ font-size: 3.7pt !important; line-height: 1.25 !important; padding-top: 1.5pt; }}

/* Dark (caffeinated) boxes: inverted colors */
.label.dark {{ background: {DARK_BG}; color: {DARK_INK}; border-color: #777; }}
.dark .tm {{ border-color: {DARK_INK}; }}
.dark .claims span, .dark .count em {{ color: #C9CDD4; }}
.dark .flavor > span {{ color: {DARK_INK}; }}
.dark .b-head {{ border-bottom-color: #3A3F48; }}
.dark .warn {{ color: #D5D8DE; }}
.dark .upc {{ background: #fff; color: {INK}; padding: 2pt 3pt; align-self: flex-start; border-radius: 1.5pt; }}
.dark .nf {{ background: #fff; color: {INK}; border-color: #fff; }}
/* Caffeine badge: exactly as wide as the claim lines above it */
.caf {{ margin-top: 4pt; width: 0; min-width: 100%; text-align: center; color: {DARK_BG}; background: var(--flavor);
        padding: 2pt 0 2.2pt; border-radius: 4pt; display: flex; flex-direction: column; align-items: center; }}
.claims .caf b {{ font-size: 5.6pt; font-weight: 900; letter-spacing: 0.07em; line-height: 1.15; white-space: nowrap; }}
.claims .caf span {{ font-size: 4.8pt; font-weight: 700; line-height: 1.15; margin: 0; color: {DARK_BG}; white-space: nowrap; }}
.stack.zoom {{ zoom: 0.7; grid-template-columns: 3in 3in 3in; }}
"""

HEAD = ('<!doctype html><html><head><meta charset="utf-8"><title>bright gum cartons</title>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap">'
        f'<style>{CSS}</style></head><body>')

FOOT_NOTE = ('<div class="calib"><i></i>1-inch print calibration</div>'
             '<p class="howto">Print at 100% / Actual Size on 8.5 x 11 in paper. Do not select Fit to Page.<br>'
             'Cut the rectangular outlines and paste onto a 15-stick carton.</p>')


def flavor_page(f, v):
    return f'''<section class="page">
<p class="pt">BRIGHT GUM &nbsp;|&nbsp; {f['name'].upper()} &nbsp;|&nbsp; FRONT + BACK LABELS</p>
<p class="ps">Each face is exactly 3.00 x 2.40 in at 100% scale. Flavor color {f['color']} is used for the eye, the flavor name and the accents.</p>
<p class="pn">Mockup: nutrition values are calculated estimates; ingredients follow {v['sheet']}. Barcode is decorative and will not scan.</p>
<div class="pair">
  <div>{front(f, v)}<p class="cap">FRONT · 3.00 x 2.40 in</p></div>
  <div>{back(f, v)}<p class="cap">BACK · 3.00 x 2.40 in</p></div>
</div>
{FOOT_NOTE}
</section>'''


def lineup_page(v):
    fronts = "".join(f'<div>{front(f, v)}</div>' for f in FLAVORS)
    return f'''<section class="page">
<p class="pt">BRIGHT GUM &nbsp;|&nbsp; FLAVOR LINEUP &nbsp;|&nbsp; ALL FRONTS</p>
<p class="ps">The eye matches the flavor: Peppermint royal blue, Spearmint emerald, Blue Raspberry azure, Raspberry red, Watermelon melon red, Pickle dill green. Dark grey boxes are the caffeinated line: Cotton Candy has a sky-blue eye, with "Cotton" in sky blue and "Candy" in pink. Caffeinated Peppermint is blue and caffeinated Spearmint is green.</p>
<p class="pn">Preview only, shown at 70% size. Print the flavor pages that follow for true 1:1 labels.</p>
<div class="stack zoom">{fronts}</div>
</section>'''


def build(name):
    v = VARIANTS[name]
    v["dir"].mkdir(exist_ok=True)
    html = HEAD + lineup_page(v) + "".join(flavor_page(f, v) for f in FLAVORS) + "</body></html>"
    path = v["dir"] / (v["stem"] + ".html")
    path.write_text(html)
    print("wrote", path)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name in ([MAIN] + [k for k in VARIANTS if k != MAIN] if which == "all" else [which]):
        build(name)
