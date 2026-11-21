"""Build the cost study as HTML (rendered to PDF by render_pdf.js) from cost_model.json.

    python3 finance/cost_model.py && python3 finance/build_pdf.py && node finance/render_pdf.js
"""
import json
from pathlib import Path

OUT = Path(__file__).parent
M = json.loads((OUT / "cost_model.json").read_text())
INK, BLUE, SOFT, LINE, TINT = "#0D1117", "#1428DC", "#4A5263", "#DFE3EF", "#F4F6FB"
C_ING, C_MFG, C_PACK, C_SETUP = "#1428DC", "#0085C7", "#046A4A", "#9AA3B5"

k = lambda v: f"${v / 1000:,.0f}k" if v < 1e6 else f"${v / 1e6:.1f}M"
d0 = lambda v: f"${v:,.0f}"
r0 = lambda v: f"${round(v, -2):,.0f}"       # rounded to the nearest $100
d2 = lambda v: f"${v:.2f}"
sd2 = lambda v: f"{'+' if v >= 0 else '−'}${abs(v):.2f}"

_L = json.loads((OUT.parent / "brand" / "logo" / "logo_paths.json").read_text())
LOGO = (f'<svg viewBox="0 0 {_L["viewBox"][2]} {_L["viewBox"][3]}" class="logo" aria-label="bright logo">'
        f'<path fill="{INK}" fill-rule="evenodd" d="{_L["ink"]}"/><path fill="{BLUE}" d="{_L["eye"]}"/></svg>')

cg = M["cogs"][M["base_recipe"]]
L, S = cg["launch_total"], cg["scale_total"]
tot, cap = M["startup_total"], M["factory_capital_total"]
ch = M["channels"][f"{M['recommended_price']:.2f}"]
need, sc = M["need"], M["scenarios"]
y1, y2 = sc["Year 1: campus launch"], sc["At scale: regional retail"]
fb = M["factory_breakeven"]
DIRECT, DIST, INPERSON, ONLINE, FAIRE = ("Direct to local stores", "Distributor to grocery chains",
                                         "In person (campus table, events)", "Online 6-pack, shipped by you",
                                         "Small shops through Faire")

pages = []
def page(title, body, kicker=""):
    pages.append(f'<section class="page"><header>{LOGO}<div><p class="kick">{kicker or "Cost and pricing study"}</p>'
                 f'<h1>{title}</h1></div></header>{body}'
                 f'<footer><span>bright gum · Cost and pricing study · November 2026 · Planning estimates, not supplier quotes</span>'
                 f'<span>{len(pages) + 1}</span></footer></section>')

def table(head, rows, cls="", foot=None):
    h = "".join(f"<th>{c}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    f = ("<tr class='tot'>" + "".join(f"<td>{c}</td>" for c in foot) + "</tr>") if foot else ""
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}{f}</tbody></table>'

# ---------- Page 1: summary sheet ----------
tiles = f'''<div class="tiles">
<div class="tile"><b>{k(tot["typical"])}</b><span>Cash to launch with a contract manufacturer</span><em>Range {k(tot["low"])} to {k(tot["high"])}</em></div>
<div class="tile"><b>{d2(L)} → {d2(S)}</b><span>Cost to make one 15-stick carton: first run, then at scale</span><em>First run {M["launch_run"]:,} cartons; scale {M["scale_run"]:,}+</em></div>
<div class="tile"><b>{d2(M["recommended_price"])}</b><span>Suggested shelf price</span><em>Workable range $2.49 to $3.49</em></div>
<div class="tile"><b>{k(cap["typical"])}</b><span>To build your own small factory instead</span><em>Range {k(cap["low"])} to {k(cap["high"])}. Not recommended yet.</em></div>
</div>'''
findings = f'''<h2>What the numbers say</h2>
<ol class="find">
<li><b>Use a contract manufacturer, not your own factory.</b> Your own line costs about {k(cap["typical"])} to set up and about {d0(M["factory_monthly_total"])} a month to run. It only pays off above roughly {fb["at_launch_fee"] / 1e6:.1f} to {fb["at_scale_fee"] / 1e6:.1f} million cartons a year, which is close to everything a small line can make.</li>
<li><b>Ingredients are the small part.</b> They are about {d2(cg["launch"]["Ingredients"])} of the {d2(L)} first-run cost. The manufacturer's fee and the packaging make up most of the rest. bright's main recipe has no xylitol; adding it would cost only about 5 cents more a carton.</li>
<li><b>Run size is the biggest lever.</b> A {M["launch_run"]:,}-carton run costs about {d2(L)} a carton. At {M["scale_run"]:,} cartons and bulk ingredient prices it falls to about {d2(S)}.</li>
<li><b>Sell the first run directly.</b> At {d2(M["recommended_price"])}, you make {d2(ch[INPERSON]["margin_launch"])} a carton selling in person, {d2(ch[DIRECT]["margin_launch"])} selling to local stores and {d2(ch[ONLINE]["margin_launch"])} on online 6-packs. Through a distributor you would lose {d2(-ch[DIST]["margin_launch"])} a carton until costs come down.</li>
<li><b>Break-even takes volume.</b> Year one roughly breaks even on running costs at about {round(y1["breakeven_cartons"], -2):,.0f} cartons sold directly. A regional retail business breaks even at about {round(y2["breakeven_cartons"], -3):,.0f} cartons a year.</li>
</ol>'''
price_box = f'''<div class="two">
<div class="box"><h3>What you could charge</h3><p>Mainstream gum sells for $1.39 to $1.79 a pack. Premium and natural gums sell for $2.49 to $2.99, and functional gums for about $3.99. A whitening gum with a message in every wrapper fits the premium tier: <b>$2.49 to $3.49</b>.</p></div>
<div class="box"><h3>What you need to charge</h3><p>To break even selling to local stores, the shelf price must be at least <b>{d2(need[DIRECT]["breakeven_launch"])}</b> on the first run and <b>{d2(need[DIRECT]["breakeven_scale"])}</b> at scale. Through a distributor it must be at least <b>{d2(need[DIST]["breakeven_launch"])}</b> on the first run and <b>{d2(need[DIST]["breakeven_scale"])}</b> at scale.</p></div>
</div>
<p class="note"><b>How to read this study.</b> Every figure is a planning estimate built from public price lists, supplier listings and market reports gathered in November 2026. None is a quote. Gum manufacturers do not publish prices, so their fees are the least certain numbers here. Page 6 shows how reliable each input is and what to ask for when you request quotes.</p>'''
page("What it costs to make bright gum, and what to charge", tiles + findings + price_box, "Summary")

# ---------- Page 2: startup costs ----------
rows = [[r["item"], d0(r["low"]), f"<b>{d0(r['typical'])}</b>", d0(r["high"]), r["basis"]] for r in M["startup_items"]]
fr = M["first_run"]
rows.append([f"First production run ({M['launch_run']:,} cartons)", r0(fr["low"]), f"<b>{r0(fr['typical'])}</b>", r0(fr["high"]), "This model (page 3)"])
sub = M["startup_subtotal"]
rows.append([f"Contingency ({M['contingency']:.0%})"] + [r0((sub[x] + fr[x]) * M["contingency"]) if x != "typical" else f"<b>{r0((sub[x] + fr[x]) * M['contingency'])}</b>" for x in ("low", "typical", "high")] + ["Allowance for surprises"])
start = table(["One-time cost", "Low", "Typical", "High", "Where the number comes from"], rows, "num3",
              ["Total cash to launch", r0(tot["low"]), r0(tot["typical"]), r0(tot["high"]), "Two flavors, contract manufacturer"])
cheap = '''<div class="two">
<div class="box"><h3>Where the money goes</h3><p>About a third is the first production run, which you earn back as you sell it. The whitening study is the largest single test. It is only needed to print "Whitening" on the box, so it can wait until demand is proven.</p></div>
<div class="box"><h3>A cheaper first step</h3><p>Some private-label gum makers will put their existing sugar-free gum in your packaging. Listings show $1.80 to $4.00 a box with minimum orders of 300 to 1,000 boxes. A 1,000-box market test could cost a few thousand dollars and show whether people want the message idea before you pay for a custom formula. These are unverified overseas listings, and imported food must still meet FDA rules.</p></div>
</div>'''
page("What it costs to start", "<p class='lede'>One-time costs to develop, test and launch two flavors with a contract manufacturer.</p>" + start + cheap)

# ---------- Page 3: cost per carton ----------
def bar(parts, total, scale_to):
    segs = "".join(f'<i style="width:{v / scale_to * 100:.1f}%;background:{c}"></i>' for v, c in parts)
    return f'<div class="bar">{segs}<b>{d2(total)}</b></div>'
order = [("Ingredients", C_ING), ("Manufacturing", C_MFG), ("Packaging", C_PACK), ("Run setup", C_SETUP)]
bars = f'''<div class="bars">
<p>First run ({M["launch_run"]:,} cartons)</p>{bar([(cg["launch"][n], c) for n, c in order], L, L)}
<p>At scale ({M["scale_run"]:,}+ cartons)</p>{bar([(cg["scale"][n], c) for n, c in order], S, L)}
<div class="legend">{"".join(f'<span><i style="background:{c}"></i>{n if n != "Manufacturing" else "Manufacturer fee"}</span>' for n, c in order)}</div></div>'''
comp = table(["Part of the cost", "First run", "At scale", "What it covers"], [
    ["Ingredients", d2(cg["launch"]["Ingredients"]), d2(cg["scale"]["Ingredients"]), "40.5 g of gum, with 5% lost in production"],
    ["Manufacturer fee", d2(cg["launch"]["Manufacturing"]), d2(cg["scale"]["Manufacturing"]), "Making, wrapping and packing, plus their overhead and profit (range $0.20 to $0.60)"],
    ["Packaging", d2(cg["launch"]["Packaging"]), d2(cg["scale"]["Packaging"]), "Printed carton, 15 wrappers, share of display box and shipping case"],
    ["Run setup", d2(cg["launch"]["Run setup"]), d2(cg["scale"]["Run setup"]), "About $2,000 per production run"],
], "num2", ["Cost per carton", d2(L), d2(S), f"Likely range: ${M['cogs_range']['launch'][0]:.2f} to ${M['cogs_range']['launch'][1]:.2f} first run; ${M['cogs_range']['scale'][0]:.2f} to ${M['cogs_range']['scale'][1]:.2f} at scale"])
ing = M["ingredients"][M["base_recipe"]]
top = sorted(ing["rows"], key=lambda r: -r["startup"])[:6]
ingt = table(["Ingredient (main recipe, no xylitol)", "Share of recipe", "$/kg small lots", "$/kg bulk", "Per carton, first run", "Per carton, at scale"],
             [[r["ingredient"], f"{r['pct']:.1f}%", d2(M["prices"][r["ingredient"]]["startup"]), d2(M["prices"][r["ingredient"]]["scale"]), d2(r["startup"]), d2(r["scale"])] for r in top],
             "num5", ["All ingredients", "100%", "", "", d2(ing["startup"]), d2(ing["scale"])])
rec = table(["Recipe", "Ingredients, first run", "Ingredients, at scale", "Whole carton, first run", "Whole carton, at scale"],
            [[n, d2(M["ingredients"][n]["startup"]), d2(M["ingredients"][n]["scale"]), d2(M["cogs"][n]["launch_total"]), d2(M["cogs"][n]["scale_total"])] for n in M["ingredients"]], "num4")
page("What one carton costs to make", bars + comp + "<h2>The ingredients that cost the most</h2>" + ingt
     + "<h2>Main recipe vs. the xylitol alternatives</h2>" + rec
     + "<p class='note'>bright's main recipe has no xylitol. It costs about the same as the standard xylitol recipe and about 5 cents less than the long-lasting xylitol recipe, which is the fair comparison because the main recipe is also built long-lasting. The bigger reasons for dropping xylitol are easier manufacturing, a more stable stick and a wider choice of manufacturers, not cost.</p>")

# ---------- Page 4: packaging and own factory ----------
pack = table(["Cartons ordered", "Price per printed carton", "Notes"], [
    ["1,000", "$0.44 to $1.00", "Short digital runs; too costly to sell through distributors"],
    ["10,000", "$0.15 to $0.55", "Typical first run"],
    ["50,000", "$0.18 to $0.30", ""],
    ["100,000", "$0.09 to $0.22", "Where packaging reaches about $0.20 to $0.25 a carton all-in"],
], "", ["One-time tooling", "$300 to $950", "Cutting die and printing plates"])
wrap = '''<div class="two">
<div class="box"><h3>Foil-lined wrappers</h3><p>Listings price printed foil-and-paper gum wrap at $1.80 to $6.70 per kg, which works out to about 1 to 3 cents a carton. The material is cheap. The hurdles are the minimum order of 300 to 500 kg, enough for about 100,000 cartons, and printing plates at $200 to $800 per color.</p></div>
<div class="box"><h3>Plain paper, message inside</h3><p>Plain paper likely saves a cent or two a carton at most. Its real advantage is flexibility: smaller minimum orders, and digital printing with no plates, so the set of messages can be large and can change often. Add one sealed inner pack per carton to keep the gum fresh.</p></div>
</div>'''
capt = table(["Own-factory set-up cost", "Low", "Typical", "High"],
             [[r["item"], d0(r["low"]), f"<b>{d0(r['typical'])}</b>", d0(r["high"])] for r in M["factory_capital"]], "num3",
             ["Total before you make a stick", d0(cap["low"]), d0(cap["typical"]), d0(cap["high"])])
mon = table(["Monthly running cost", "Per month"], [[r["item"], d0(r["cost"])] for r in M["factory_monthly"]], "num1",
            ["Total fixed cost", f"{d0(M['factory_monthly_total'])} a month"])
fact = f'''<div class="two"><div>{capt}</div><div>{mon}
<p class="note">Electricity is minor: roughly 0.5 to 1 kWh per kg of gum at about 13 cents per kWh, well under 1 cent a carton. People and rent are the real running costs.</p></div></div>
<div class="box wide"><h3>When would your own factory pay off?</h3><p>Running it costs about {d0(M["factory_monthly_total"] * 12)} a year whether or not you sell anything. What it saves is the manufacturer's fee of $0.25 to $0.45 a carton. So it needs <b>{fb["at_launch_fee"] / 1e6:.1f} to {fb["at_scale_fee"] / 1e6:.1f} million cartons a year</b> just to cover running costs, before repaying the set-up money. A small line with one wrapping machine makes about {M["factory_capacity_year"] / 1e6:.1f} million cartons a year running flat out. A bench-top kit for testing recipes yourself is a different matter: a small mixer, hand roller and tools cost about $10,000 to $30,000.</p></div>'''
page("Packaging, equipment and running costs", "<h2>Printed cartons get much cheaper with volume</h2>" + pack + wrap + "<h2>Buying your own equipment</h2>" + fact)

# ---------- Page 5: pricing and profit ----------
mx = max(s["per_piece"] for s in M["shelf"])
shelf = "".join(f'<div class="srow"><span>{s["name"]}</span><div class="sbar"><i style="width:{s["per_piece"] / mx * 100:.0f}%"></i></div><b>{d2(s["price"])}</b><em>{s["per_piece"] * 100:.0f}¢ a piece</em></div>' for s in M["shelf"])
ours = M["recommended_price"]
shelf += f'<div class="srow us"><span>bright 15 (suggested)</span><div class="sbar"><i style="width:{ours / 15 / mx * 100:.0f}%"></i></div><b>{d2(ours)}</b><em>{ours / 15 * 100:.0f}¢ a piece</em></div>'
cht = table(["Where you sell (shelf price $2.99)", "You keep per carton", "Profit, first run", "Profit, at scale"],
            [[n, d2(v["net"]), f"{sd2(v['margin_launch'])} ({v['pct_launch']:.0%})", f"{sd2(v['margin_scale'])} ({v['pct_scale']:.0%})"] for n, v in ch.items()], "num3")
nt = table(["Shelf price you need", "To break even, first run", "To break even, at scale", "For a 40% margin, first run", "For a 40% margin, at scale"],
           [[n, d2(need[n]["breakeven_launch"]), d2(need[n]["breakeven_scale"]), d2(need[n]["target_launch"]), d2(need[n]["target_scale"])] for n in (INPERSON, DIRECT, FAIRE, DIST)], "num4")
def scol(s):
    return [f"{s['cartons']:,}", d2(s["avg_net"]), d2(s["unit_cost"]), r0(s["revenue"]), r0(s["gross_profit"]), r0(s["marketing"]), r0(s["overhead"]),
            f"<b>{'−' if s['profit'] < 0 else ''}{r0(abs(s['profit']))}</b>", f"{round(s['breakeven_cartons'], -2):,.0f}"]
labels = ["Cartons sold in the year", "Average kept per carton", "Cost per carton", "Sales", "Profit after making the gum", "Marketing", "Other running costs", "Profit before paying yourself", "Cartons needed to break even"]
a, b = scol(y1), scol(y2)
sct = table(["Two example years at $2.99", "Year 1: campus launch", "At scale: regional retail"], [[labels[i], a[i], b[i]] for i in range(len(labels))], "num2")
page("What to charge, and when it turns a profit",
     "<h2>What other gums cost on the shelf</h2><div class='shelf'>" + shelf + "</div>"
     + "<h2>What you keep depends on where you sell</h2>" + cht
     + "<p class='note'>A store keeps about 40% of the shelf price. A distributor, promotions and a broker take roughly another third of what is left. Selling single cartons online does not work: postage and handling cost more than the gum, so sell 6-packs or larger.</p>"
     + nt + "<h2>Two example years</h2>" + sct
     + "<p class='note'>Year 1 assumes 40% sold in person, 40% to local stores and 20% online, with about $18,000 of running costs. The scale year assumes 60% through a distributor, 30% direct to stores and 10% online, with $60,000 of running costs and 15% of sales spent on marketing. Neither includes a salary for you, or the one-time launch costs.</p>")

# ---------- Page 6: confidence, quotes, sources ----------
conf = table(["Input", "How reliable", "Why"], [
    ["Shelf prices of other gums", "Good", "Seen on retailer sites in November 2026"],
    ["Lab tests, trademark, barcode and LLC fees", "Good", "Published price lists and fee schedules"],
    ["Store and distributor margins", "Fair", "Industry data and consultant guides"],
    ["Ingredient prices", "Fair", "Supplier list prices and market reports; small lots cost 3 to 10 times the bulk price"],
    ["Carton and wrapper prices", "Fair to weak", "Vendor guides and overseas listings; your carton is thinner than standard and needs a custom quote"],
    ["Equipment prices", "Weak", "Overseas asking prices before freight, duty and installation"],
    ["Manufacturer's fee and minimum order", "Weak", "No gum maker publishes prices; built from general food-industry figures"],
    ["Whitening study, factory fit-out, gum base price", "Weak", "No public price found; these are estimates"],
], "")
ask = '''<div class="two">
<div class="box"><h3>Ask every manufacturer for</h3><ul>
<li>Price per carton at three volumes: their minimum, 50,000 and 250,000</li>
<li>Minimum order in cartons, per flavor</li>
<li>Development fee, what it covers, and whether it is credited to the first order</li>
<li>Who owns the formula</li>
<li>Wrapper options and their minimum orders: foil-lined, and plain paper printed inside</li>
<li>Whether they supply shelf-life and stain-removal data</li>
</ul></div>
<div class="box"><h3>Next steps</h3><ul>
<li>Get three manufacturer quotes; they replace the weakest numbers here</li>
<li>Get a custom quote for your 3.00 x 2.40 x 0.35 in carton</li>
<li>Confirm import duty on any imported ingredients with a customs broker; tariffs changed in 2026</li>
<li>Update finance/cost_model.py with the quotes and rebuild this study</li>
</ul></div></div>'''
import cost_model
src = "<ul class='src'>" + "".join(f"<li>{s}</li>" for s in cost_model.SOURCES) + "</ul>"
page("How reliable these numbers are", conf + ask + "<h2>Sources</h2>" + src
     + "<p class='note'>Research note: most supplier pages could not be opened directly during research, so prices were read from search-result extracts and were not re-checked on the live pages. Treat every figure as a starting point for a quote, not as a quote.</p>")

CSS = f"""
@page {{ size: 8.5in 11in; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Lato', Arial, sans-serif; color: {INK}; font-size: 9.2pt; line-height: 1.38; }}
.page {{ width: 8.5in; height: 11in; padding: 0.55in 0.6in 0.7in; position: relative; page-break-after: always; overflow: hidden; }}
.page:last-child {{ page-break-after: auto; }}
header {{ display: flex; align-items: center; gap: 0.22in; padding-bottom: 0.14in; border-bottom: 1pt solid {LINE}; margin-bottom: 0.16in; }}
.logo {{ width: 1.25in; height: 0.406in; flex: none; }}
.kick {{ font-size: 7.6pt; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; color: {BLUE}; }}
h1 {{ font-size: 17pt; font-weight: 900; line-height: 1.15; }}
h2 {{ font-size: 10.6pt; font-weight: 900; margin: 0.15in 0 0.06in; }}
h3 {{ font-size: 9.4pt; font-weight: 900; margin-bottom: 3pt; color: {BLUE}; }}
.lede {{ font-size: 10pt; color: {SOFT}; margin-bottom: 0.1in; }}
footer {{ position: absolute; left: 0.6in; right: 0.6in; bottom: 0.38in; display: flex; justify-content: space-between; font-size: 7.4pt; color: {SOFT}; }}
.tiles {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.12in; }}
.tile {{ background: {TINT}; border-radius: 8pt; padding: 0.13in 0.12in; display: flex; flex-direction: column; gap: 3pt; }}
.tile b {{ font-size: 17pt; font-weight: 900; color: {BLUE}; line-height: 1.05; white-space: nowrap; }}
.tile span {{ font-size: 8.6pt; font-weight: 700; line-height: 1.25; }}
.tile em {{ font-style: normal; font-size: 7.6pt; color: {SOFT}; line-height: 1.25; }}
.find {{ padding-left: 0.2in; display: flex; flex-direction: column; gap: 5pt; }}
.find li::marker {{ font-weight: 900; color: {BLUE}; }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.14in; margin-top: 0.13in; align-items: start; }}
.box {{ background: {TINT}; border-radius: 8pt; padding: 0.12in 0.14in; }}
.box.wide {{ margin-top: 0.13in; }}
.box ul {{ padding-left: 0.16in; display: flex; flex-direction: column; gap: 2pt; }}
.note {{ font-size: 8.2pt; color: {SOFT}; margin-top: 0.09in; }}
table {{ width: 100%; border-collapse: collapse; font-size: 8.5pt; }}
th {{ text-align: left; font-size: 7.6pt; font-weight: 900; color: {SOFT}; border-bottom: 1pt solid {INK}; padding: 3pt 5pt 3pt 0; vertical-align: bottom; }}
td {{ border-bottom: 0.5pt solid {LINE}; padding: 3.2pt 5pt 3.2pt 0; vertical-align: top; }}
tr.tot td {{ font-weight: 900; border-top: 1pt solid {INK}; border-bottom: none; }}
.num1 td:nth-child(n+2), .num1 th:nth-child(n+2), .num2 td:nth-child(2), .num2 td:nth-child(3), .num2 th:nth-child(2), .num2 th:nth-child(3),
.num3 td:nth-child(2), .num3 td:nth-child(3), .num3 td:nth-child(4), .num3 th:nth-child(2), .num3 th:nth-child(3), .num3 th:nth-child(4),
.num4 td:nth-child(n+2), .num4 th:nth-child(n+2), .num5 td:nth-child(n+2), .num5 th:nth-child(n+2) {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
.num2 td:nth-child(4), .num3 td:nth-child(5) {{ color: {SOFT}; padding-left: 10pt; }}
.num2 th:nth-child(4), .num3 th:nth-child(5) {{ padding-left: 10pt; }}
.bars p {{ font-size: 8.4pt; font-weight: 700; margin-top: 5pt; }}
.bar {{ display: flex; align-items: center; height: 0.24in; margin-top: 2pt; }}
.bar i {{ display: block; height: 100%; }}
.bar b {{ margin-left: 7pt; font-size: 11pt; font-weight: 900; }}
.legend {{ display: flex; gap: 0.2in; font-size: 7.8pt; color: {SOFT}; margin: 5pt 0 0.1in; }}
.legend i {{ display: inline-block; width: 8pt; height: 8pt; border-radius: 2pt; margin-right: 4pt; vertical-align: -1pt; }}
.shelf {{ display: flex; flex-direction: column; gap: 2.5pt; }}
.srow {{ display: grid; grid-template-columns: 1.5in 1fr 0.5in 0.9in; align-items: center; gap: 8pt; font-size: 8.5pt; }}
.sbar {{ height: 0.13in; }}
.sbar i {{ display: block; height: 100%; background: #AEB6C9; border-radius: 2pt; }}
.srow b {{ text-align: right; font-variant-numeric: tabular-nums; }}
.srow em {{ font-style: normal; color: {SOFT}; }}
.srow.us span, .srow.us b {{ font-weight: 900; color: {BLUE}; }}
.srow.us .sbar i {{ background: {BLUE}; }}
.src {{ padding-left: 0.16in; font-size: 7.8pt; color: {SOFT}; columns: 2; column-gap: 0.25in; }}
.src li {{ break-inside: avoid; margin-bottom: 2pt; }}
"""
html = ('<!doctype html><html><head><meta charset="utf-8"><title>bright gum cost and pricing study</title>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap">'
        f"<style>{CSS}</style></head><body>{''.join(pages)}</body></html>")
(OUT / "bright-gum-cost-study.html").write_text(html)
print("wrote", OUT / "bright-gum-cost-study.html", "-", len(pages), "pages")
