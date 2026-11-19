# bright gum

**A whitening xylitol gum with a positive message inside every wrapper.**
*Something to smile about.*

![bright logo](brand/logo/bright-logo-primary.svg)

## What's here

| Folder | File | What it covers |
|---|---|---|
| `brand/logo/` | `bright-logo-primary.svg` | **The official logo, use it first:** black wordmark with the Peppermint-blue eye, on white. Vector, any size. On flavor boxes the eye takes that flavor's color. |
| | `bright-logo-on-blue.svg`, `-on-green.svg`, `-reversed.svg` | Backup versions for colored or dark backgrounds only |
| `packaging/` | `bright-cartons.pdf` | **Print-ready 1:1 carton labels** (front + back) for Peppermint, Spearmint, Blue Raspberry, Raspberry, Watermelon and Pickle, plus a lineup page. The eye color matches each flavor. |
| | `build_cartons.py`, `render.js` | Regenerate the labels: `python3 packaging/build_cartons.py && node packaging/render.js` |
| `product/` | `formula-sheets.md` | **v1 recipes for every flavor**: grams per stick, batch quantities, label ingredient lines, calculated nutrition |
| | `formula-sheets-long-lasting.md` | **Long-lasting versions** of every recipe (two-stage flavor and sweetener release), plus a timed chew test |
| | `formula.md` | Draft recipe (xylitol ≥ 1 g/stick + whitening), flavor variations, questions for co-packers |
| | `wrapper-messages.md` | **120 positive messages** for the inside of the wrapper (current focus), plus the Bible-verse edition saved for later |
| `regulations/` | `regulations.md` | US food-law checklist: label requirements, allowed claims, warnings, Prop 65, business setup, trademark |
| `marketing/` | `marketing-plan.md` | Audience, positioning, pricing, phased launch, content ideas, metrics |
| | `commercials.md` | Shot-by-shot scripts for "Pass It On" (campus) and "Lift" (rec center, two endings) |

## Product snapshot

- **Format:** 15-stick carton, 3.00 × 2.40 × 0.35 in
- **Flavors:** Peppermint · Spearmint · Blue Raspberry · Raspberry · Watermelon · Pickle
- **Sugar-free**, xylitol as the first ingredient, stain-lifting whitening polish
- **Every wrapper:** a teaser outside, a message inside

## Top 3 things to do next

1. **Before printing production cartons,** add the required "Distributed by"
   company name and address to the back (left off the mockups on purpose; see
   `regulations/regulations.md`). "Anti-Cavity" is already removed.
2. **Contact 5–10 gum co-packers** with the questions in `product/formula.md`
   and order stock samples.
3. **Run a trademark search** for "bright gum" and claim the social handles.
