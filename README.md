# bright gum

**A whitening xylitol gum with a positive message inside every wrapper.**
*Something to smile about.*

![bright logo](brand/logo/bright-logo-primary.svg)

## Look at and edit everything: bright studio

Run `python3 studio/bright_studio.py` from this folder. A page opens in your
browser where you can browse every file, read and edit documents, view the boxes
and PDFs, rebuild the labels and cost study, and save to GitHub. See
[`studio/README.md`](studio/README.md).

## What's here

| Folder | File | What it covers |
|---|---|---|
| `brand/logo/` | `bright-logo-primary.svg` | **The official logo, use it first:** traced directly from the chosen logo image, so the letter shapes match it exactly. Black wordmark with the Peppermint-blue eye, on a transparent background. Vector, any size. On flavor boxes the eye takes that flavor's color. |
| | `bright-logo-on-blue.svg`, `-on-green.svg`, `-reversed.svg` | Backup versions for colored or dark backgrounds only |
| | `source/`, `trace_logo.py`, `logo_paths.json` | The chosen logo images, the script that traces them, and the traced shapes that the boxes, cost study and studio all draw from |
| `packaging/` | `bright-cartons.pdf` | **Print-ready 1:1 carton labels** (front + back) for Peppermint, Spearmint, Blue Raspberry, Raspberry, Watermelon, Pickle, plus the caffeinated dark boxes (Cotton Candy, Peppermint and Spearmint), and a lineup page. The eye color matches each flavor. |
| | `no-xylitol/bright-cartons-no-xylitol.pdf` | The same six cartons with xylitol removed: "A message in every wrapper" takes its place |
| | `package-dimensions.md` | Real sizes of common 15-stick gum packs, and the recommended production carton size |
| | `build_cartons.py`, `render.js` | Regenerate the labels: `python3 packaging/build_cartons.py && node packaging/render.js` |
| `product/` | `formula-sheets.md` | **v1 recipes for every flavor**: grams per stick, batch quantities, label ingredient lines, calculated nutrition |
| | `formula-sheets-long-lasting.md` | **Long-lasting versions** of every recipe (two-stage flavor and sweetener release), plus a timed chew test |
| | `formula-sheets-no-xylitol.md` | **No-xylitol versions** of every recipe (sorbitol-based, built long-lasting), with an honest comparison |
| | `caffeinated-line.md` | **Caffeinated line (dark boxes):** Cotton Candy, Peppermint and Spearmint recipes, caffeine amount and the rules to know |
| | `ingredients-in-major-gums.md` | **What's in the major gum brands:** their ingredient lists, what each chemical does, which are under scrutiny, and how bright compares |
| | `formula.md` | Draft recipe (xylitol ≥ 1 g/stick + whitening), flavor variations, questions for co-packers |
| | `wrapper-messages.md` | **120 positive messages** for the inside of the wrapper (current focus), plus the Bible-verse edition saved for later |
| `finance/` | `bright-gum-cost-study.pdf` | **Cost and pricing study** (6 pages): cost to start, cost per carton, own factory vs. contract manufacturer, what to charge, break-even |
| | `bright-gum-cost-study.pptx` | The same study as a 12-slide PowerPoint |
| | `cost_model.py` | Every assumption in one place. Change a number, then rebuild: `python3 finance/cost_model.py && python3 finance/build_pdf.py && node finance/render_pdf.js && node finance/build_pptx.js` (the PowerPoint build needs `npm install pptxgenjs sharp`) |
| `regulations/` | `regulations.md` | US food-law checklist: label requirements, allowed claims, warnings, Prop 65, business setup, trademark |
| `studio/` | `bright_studio.py` | **bright studio**: the browser app for viewing, editing and rebuilding these files |
| `marketing/` | `marketing-plan.md` | Audience, positioning, pricing, phased launch, content ideas, metrics |
| | `commercials.md` | Shot-by-shot scripts for "Pass It On" (campus) and "Lift" (rec center, two endings) |

## Product snapshot

- **Format:** 15-stick carton, 3.00 × 2.40 × 0.35 in
- **Flavors:** Peppermint · Spearmint · Blue Raspberry · Raspberry · Watermelon · Pickle · caffeinated dark boxes: Cotton Candy, Peppermint and Spearmint
- **Sugar-free**, xylitol as the first ingredient, stain-lifting whitening polish
- **Every wrapper:** a teaser outside, a message inside

## Top 3 things to do next

1. **Before printing production cartons,** add the required "Distributed by"
   company name and address to the back (left off the mockups on purpose; see
   `regulations/regulations.md`). "Anti-Cavity" is already removed.
2. **Contact 5–10 gum co-packers** with the questions in `product/formula.md`
   and order stock samples.
3. **Run a trademark search** for "bright gum" and claim the social handles.
