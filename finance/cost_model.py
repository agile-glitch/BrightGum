"""bright gum cost and pricing model.

Every assumption lives in this file. Run it to print a summary and write
finance/cost_model.json, which the PDF sheet and the PowerPoint are built from.

    python3 finance/cost_model.py

All prices are planning estimates gathered from public listings and market
reports in November 2026 (see SOURCES at the bottom). None is a supplier quote.
"""
import json
from pathlib import Path

OUT = Path(__file__).parent
CARTON_KG = 0.0405          # 15 sticks x 2.7 g
YIELD_LOSS = 0.05           # ingredients lost in production

# --- Ingredient prices, USD per kg: (startup small lots, at-scale bulk, confidence) -----------
PRICES = {
    "Xylitol":                       (11.40, 5.50, "List prices; bulk = China price plus duty and freight"),
    "Gum base":                      (6.00, 3.50, "Estimate; no public price from gum-base suppliers"),
    "Gum base, long-flavor grade":   (7.80, 4.50, "Estimate (standard base plus 30%)"),
    "Sorbitol powder":               (8.20, 2.00, "List prices; market report"),
    "Mannitol":                      (9.00, 4.00, "Estimate"),
    "Calcium carbonate":             (2.50, 0.80, "Market index; small lot is an estimate"),
    "Glycerin":                      (4.30, 1.60, "List price; contract assessment"),
    "Sodium tripolyphosphate":       (10.00, 2.00, "List prices; market reports disagree"),
    "Sunflower lecithin":            (5.60, 4.00, "List price; bulk is an estimate"),
    "Sucralose":                     (31.00, 17.00, "List price; market reports"),
    "Mint flavor (oil + menthol)":   (60.00, 50.00, "USDA farm price plus estimate"),
    "Encapsulated flavor":           (60.00, 45.00, "Estimate; quote-only ingredient"),
    "Encapsulated sweeteners":       (60.00, 40.00, "Estimate; quote-only ingredient"),
}

# --- Recipes (Peppermint, % by weight), from the product/ formula sheets ------------------------
RECIPES = {
    "Xylitol, standard": {
        "Xylitol": 40.0, "Gum base": 30.0, "Sorbitol powder": 18.5, "Calcium carbonate": 4.0,
        "Glycerin": 3.0, "Mint flavor (oil + menthol)": 2.5, "Sodium tripolyphosphate": 1.5,
        "Sunflower lecithin": 0.3, "Sucralose": 0.2,
    },
    "Xylitol, long-lasting": {
        "Xylitol": 40.0, "Gum base, long-flavor grade": 30.0, "Sorbitol powder": 16.6,
        "Calcium carbonate": 4.0, "Glycerin": 3.0, "Mint flavor (oil + menthol)": 2.0,
        "Encapsulated flavor": 1.5, "Sodium tripolyphosphate": 1.5, "Sunflower lecithin": 0.3,
        "Sucralose": 0.1, "Encapsulated sweeteners": 1.0,
    },
    "No xylitol": {
        "Sorbitol powder": 52.6, "Gum base, long-flavor grade": 28.0, "Mannitol": 5.0, "Glycerin": 4.0,
        "Calcium carbonate": 4.0, "Mint flavor (oil + menthol)": 2.0, "Encapsulated flavor": 1.5,
        "Sodium tripolyphosphate": 1.5, "Sunflower lecithin": 0.3, "Sucralose": 0.1,
        "Encapsulated sweeteners": 1.0,
    },
}

# --- Per-carton costs with a contract manufacturer: (launch run ~20,000 cartons, scale run 100,000+)
PACKAGING = {
    "Printed carton":                         (0.30, 0.15),
    "15 printed stick wrappers":              (0.05, 0.03),
    "Display box and shipping case (share)":  (0.08, 0.05),
}
CONVERSION = (0.45, 0.25)        # manufacturer's making, wrapping, packing, overhead and margin
RUN_SETUP_FEE = 2000             # per production run
LAUNCH_RUN, SCALE_RUN = 20_000, 100_000
COGS_RANGE = {"launch": (1.00, 1.90), "scale": (0.55, 1.00)}   # rough low/high around the typical

# --- One-time costs to launch 2 flavors with a contract manufacturer: (low, typical, high, basis)
STARTUP = [
    ("Formula development with the manufacturer", 2500, 10000, 25000, "Vendor price pages (not gum-specific)"),
    ("Pilot batches (2 flavors)", 2000, 3500, 6000, "Vendor price page (not gum-specific)"),
    ("Lab tests: nutrition, sugar alcohols, microbes, heavy metals", 2900, 3500, 4700, "Published lab price lists"),
    ("Shelf-life study", 1250, 4000, 8000, "Published lab price lists"),
    ("Whitening (stain-removal) study", 5000, 12000, 25000, "Estimate; labs quote on request"),
    ("Flavor-duration and taste panel", 3000, 6000, 12000, "University sensory lab price list"),
    ("Label review and nutrition panel", 500, 1300, 2500, "Published consultant prices"),
    ("Trademark: name and logo", 700, 1400, 3500, "USPTO fee $350 per class; attorney extra"),
    ("LLC, barcodes, first-year insurance", 800, 1650, 3300, "State fees, GS1 US, broker averages"),
    ("Printing plates and carton die", 500, 2000, 4000, "Packaging industry guides"),
    ("Launch marketing: samples, campus events, video", 3000, 8000, 20000, "Estimate"),
]
CONTINGENCY = 0.15

# --- Own factory (small imported line in rented space): (low, typical, high) -----------------------
FACTORY_CAPITAL = [
    ("Mixer, extruder, rolling and scoring line", 60000, 100000, 130000),
    ("Stick wrapping machine", 70000, 85000, 90000),
    ("Cartoner, coder, metal detector, case sealer", 30000, 45000, 70000),
    ("Freight, import duty, installation (25-40%)", 45000, 75000, 115000),
    ("Food-grade fit-out with humidity control (5,000 sq ft)", 300000, 450000, 850000),
    ("Food-safety plan, certification, start-up", 20000, 35000, 50000),
]
FACTORY_MONTHLY = [
    ("Rent with building charges", 7000),
    ("Four line operators", 18000),
    ("Quality and food-safety manager", 10000),
    ("Plant and maintenance lead", 8000),
    ("Electricity, water, climate control", 3000),
    ("Insurance, maintenance, compliance", 3000),
]
FACTORY_CAPACITY_CARTONS_PER_HOUR = 300 * 60 / 15       # a 300 sticks/min wrapper is the bottleneck

# --- Market: shelf prices seen at US retailers, November 2026 (price, pieces) -----------------------
SHELF = [
    ("Trident 14", 1.39, 14), ("Orbit 14", 1.72, 14), ("Extra 15", 1.79, 15), ("5 gum 15", 2.49, 15),
    ("Glee 16", 2.49, 16), ("Simply Gum 15", 2.99, 15), ("Refresh 12", 3.99, 12),
]
PRICE_POINTS = [2.49, 2.99, 3.49]
RECOMMENDED_PRICE = 2.99

# --- Channel assumptions ---------------------------------------------------------------------------
RETAILER_MARGIN = 0.40          # store keeps 40% of shelf price (range 35-51%)
FAIRE_COMMISSION = 0.15
DISTRIBUTOR_MARGIN = 0.22
STORE_MARGIN_VIA_DISTRIBUTOR = 0.38
TRADE_AND_BROKER = 0.20         # promotions 15% + broker 5%
CARD_FEE = (0.026, 0.10)        # in-person card reader
ONLINE = {"pack": 6, "postage": 6.00, "mailer": 0.50, "pay_pct": 0.029, "pay_fixed": 0.30}
TARGET_MARGIN = 0.40


def channel_net(p):
    """What bright keeps per carton, by channel, at shelf price p."""
    o = ONLINE
    online = (o["pack"] * p * (1 - o["pay_pct"]) - o["pay_fixed"] - o["postage"] - o["mailer"]) / o["pack"]
    return {
        "In person (campus table, events)": p * (1 - CARD_FEE[0]) - CARD_FEE[1],
        "Direct to local stores": p * (1 - RETAILER_MARGIN),
        "Online 6-pack, shipped by you": online,
        "Small shops through Faire": p * (1 - RETAILER_MARGIN) * (1 - FAIRE_COMMISSION),
        "Distributor to grocery chains": p * (1 - STORE_MARGIN_VIA_DISTRIBUTOR) * (1 - DISTRIBUTOR_MARGIN) * (1 - TRADE_AND_BROKER),
    }


def main():
    r2 = lambda x: round(x, 2)
    ingredients = {}
    for name, recipe in RECIPES.items():
        assert abs(sum(recipe.values()) - 100) < 1e-6, name
        rows = []
        for ing, pct in recipe.items():
            small, bulk, _ = PRICES[ing]
            rows.append({"ingredient": ing, "pct": pct,
                         "startup": pct / 100 * small * CARTON_KG * (1 + YIELD_LOSS),
                         "scale": pct / 100 * bulk * CARTON_KG * (1 + YIELD_LOSS)})
        ingredients[name] = {"rows": rows, "startup": sum(r["startup"] for r in rows),
                             "scale": sum(r["scale"] for r in rows)}

    def cogs(recipe):
        ing = ingredients[recipe]
        launch = {"Ingredients": ing["startup"], "Manufacturing": CONVERSION[0],
                  "Packaging": sum(v[0] for v in PACKAGING.values()), "Run setup": RUN_SETUP_FEE / LAUNCH_RUN}
        scale = {"Ingredients": ing["scale"], "Manufacturing": CONVERSION[1],
                 "Packaging": sum(v[1] for v in PACKAGING.values()), "Run setup": RUN_SETUP_FEE / SCALE_RUN}
        return {"launch": launch, "scale": scale,
                "launch_total": sum(launch.values()), "scale_total": sum(scale.values())}

    base = "No xylitol"          # bright's main recipe; the xylitol recipes are alternatives
    c = {name: cogs(name) for name in RECIPES}
    L, S = c[base]["launch_total"], c[base]["scale_total"]

    st = {k: sum(row[i] for row in STARTUP) for i, k in ((1, "low"), (2, "typical"), (3, "high"))}
    first_run = {"low": LAUNCH_RUN * COGS_RANGE["launch"][0], "typical": LAUNCH_RUN * L,
                 "high": LAUNCH_RUN * COGS_RANGE["launch"][1]}
    total = {k: (st[k] + first_run[k]) * (1 + CONTINGENCY) for k in st}

    cap = {k: sum(row[i] for row in FACTORY_CAPITAL) for i, k in ((1, "low"), (2, "typical"), (3, "high"))}
    monthly = sum(v for _, v in FACTORY_MONTHLY)
    factory_breakeven = {"at_launch_fee": monthly * 12 / CONVERSION[0], "at_scale_fee": monthly * 12 / CONVERSION[1]}
    capacity_year = FACTORY_CAPACITY_CARTONS_PER_HOUR * 2000

    channels = {}
    for p in PRICE_POINTS:
        channels[f"{p:.2f}"] = {name: {"net": net, "margin_launch": net - L, "margin_scale": net - S,
                                       "pct_launch": (net - L) / net, "pct_scale": (net - S) / net}
                                for name, net in channel_net(p).items()}
    def price_for(name, keep):
        """Shelf price at which bright keeps `keep` per carton in this channel (the relation is a straight line)."""
        a, b = channel_net(1.0)[name], channel_net(2.0)[name]
        return 1.0 + (keep - a) / (b - a)
    need = {name: {"breakeven_launch": price_for(name, L), "breakeven_scale": price_for(name, S),
                   "target_launch": price_for(name, L / (1 - TARGET_MARGIN)),
                   "target_scale": price_for(name, S / (1 - TARGET_MARGIN))}
            for name in channel_net(1.0)}

    n = channel_net(RECOMMENDED_PRICE)
    names = list(n)
    def scenario(cartons, mix, unit_cost, overhead, marketing_pct):
        avg = sum(n[k] * w for k, w in mix.items())
        revenue = avg * cartons
        gross = (avg - unit_cost) * cartons
        marketing = revenue * marketing_pct
        return {"cartons": cartons, "mix": mix, "avg_net": avg, "revenue": revenue, "unit_cost": unit_cost,
                "gross_profit": gross, "marketing": marketing, "overhead": overhead,
                "profit": gross - marketing - overhead,
                "breakeven_cartons": overhead / (avg - unit_cost - avg * marketing_pct)}
    scenarios = {
        "Year 1: campus launch": scenario(20_000, {names[0]: 0.4, names[1]: 0.4, names[2]: 0.2}, L, 18_000, 0.0),
        "At scale: regional retail": scenario(250_000, {names[4]: 0.6, names[1]: 0.3, names[2]: 0.1}, S, 60_000, 0.15),
    }

    model = {
        "carton": "15 sticks, 40.5 g", "recommended_price": RECOMMENDED_PRICE,
        "ingredients": ingredients, "prices": {k: {"startup": v[0], "scale": v[1], "basis": v[2]} for k, v in PRICES.items()},
        "packaging": {k: {"launch": v[0], "scale": v[1]} for k, v in PACKAGING.items()},
        "cogs": c, "cogs_range": COGS_RANGE, "base_recipe": base,
        "startup_items": [{"item": a, "low": b, "typical": d, "high": e, "basis": f} for a, b, d, e, f in STARTUP],
        "startup_subtotal": st, "first_run": first_run, "startup_total": total, "contingency": CONTINGENCY,
        "launch_run": LAUNCH_RUN, "scale_run": SCALE_RUN,
        "factory_capital": [{"item": a, "low": b, "typical": d, "high": e} for a, b, d, e in FACTORY_CAPITAL],
        "factory_capital_total": cap, "factory_monthly": [{"item": a, "cost": b} for a, b in FACTORY_MONTHLY],
        "factory_monthly_total": monthly, "factory_breakeven": factory_breakeven, "factory_capacity_year": capacity_year,
        "shelf": [{"name": a, "price": b, "pieces": d, "per_piece": b / d} for a, b, d in SHELF],
        "channels": channels, "need": need, "scenarios": scenarios, "target_margin": TARGET_MARGIN,
    }
    (OUT / "cost_model.json").write_text(json.dumps(model, indent=1))

    print("Ingredient cost per carton (startup / scale):")
    for k, v in ingredients.items():
        print(f"  {k:24s} ${v['startup']:.3f} / ${v['scale']:.3f}")
    print("Cost per carton, contract manufacturer (launch / scale):")
    for k, v in c.items():
        print(f"  {k:24s} ${v['launch_total']:.2f} / ${v['scale_total']:.2f}   {{" + ", ".join(f"{a} {b:.2f}" for a, b in v['launch'].items()) + "}")
    print("Startup: one-time", st, "| first run", {k: round(v) for k, v in first_run.items()}, "| total", {k: round(v) for k, v in total.items()})
    print("Factory capital", cap, "| monthly", monthly, "| breakeven cartons/yr", {k: round(v) for k, v in factory_breakeven.items()}, "| capacity/yr", capacity_year)
    for p, ch in channels.items():
        print(f"Shelf ${p}:")
        for name, v in ch.items():
            print(f"  {name:34s} keep ${v['net']:.2f}  launch {v['margin_launch']:+.2f} ({v['pct_launch']:+.0%})  scale {v['margin_scale']:+.2f} ({v['pct_scale']:+.0%})")
    print("Shelf price needed (break-even launch/scale, 40% margin launch/scale):")
    for name, v in need.items():
        print(f"  {name:34s} {v['breakeven_launch']:.2f} / {v['breakeven_scale']:.2f}   {v['target_launch']:.2f} / {v['target_scale']:.2f}")
    for name, s in scenarios.items():
        print(name, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in s.items() if k != "mix"})


SOURCES = [
    "Ingredient list prices: bulknaturaloils.com, bakersauthority.com, ingredi.com, univarsolutions.com, total-ingredients.com",
    "Ingredient market reports: procurementresource.com, businessanalytiq.com, imarcgroup.com, expertmarketresearch.com, Argus glycerine",
    "Mint oil farm prices: USDA NASS Crop Values (nass.usda.gov)",
    "Lab test prices: Medallion Labs catalog, Colorado State University, Michigan State University (canr.msu.edu), measurlabs.com",
    "Development fees: wwgourmet-copack.com, labs.addjoi.com, kolabtree.com",
    "Setup fees: uspto.gov fee schedule (2025), GS1 US, nolo.com, insureon.com, advisorsmith.com",
    "Cartons and tooling: axenpackaging.com, cubitpackaging.com, shoprigidboxes.com, howtobuypackaging.com",
    "Gum wrappers and equipment: made-in-china.com and alibaba.com supplier listings, mac-trader.com, loynds.com",
    "Facility and wages: costar.com, eia.gov electricity prices, bls.gov occupational wages, sqfi.com",
    "Shelf prices: target.com, walmart.com, vitacost.com (November 2026)",
    "Channel margins: NACS Magazine (June 2025), eightx.co, faire.com, shopify.com",
    "Market size: Circana via snackandbakery.com (52 weeks to May 18, 2025); National Student Clearinghouse",
]

if __name__ == "__main__":
    main()
