# bright studio

A small app that runs in your web browser for working with every bright gum
file: look at them, edit them, rebuild the boxes and cost study, and save your
changes to GitHub.

It runs only on your own computer. Nothing is uploaded unless you press
**Save to GitHub**.

## Start it

You need **Python 3** (already on most Macs; on Windows, install it from
python.org). Then:

1. Download the project to your computer. On GitHub, open the
   `claude/epic-darwin-byofir` branch, click **Code**, then **Download ZIP**, and
   unzip it. (If you use git: `git clone` the repository and check out that
   branch. You need this route to use **Save to GitHub**.)
2. Open a terminal in the project folder (Mac: Terminal; Windows: right-click
   the folder and choose "Open in Terminal").
3. Run:

```bash
python3 studio/bright_studio.py
```

Your browser opens to the studio. To stop it, go back to the terminal and press
**Ctrl+C**. On Windows, if `python3` isn't found, use `python` instead.

## What you can do

| To… | Do this |
|---|---|
| Find a file | Click it in the list on the left, or type in **Find a file** |
| Read a document | Text files (`.md`) open formatted, with tables and headings |
| Edit a document | Click **Edit** (or **Side by side** to see the result as you type), then **Save** or press Ctrl+S / ⌘S |
| Look at boxes, PDFs, images | Click them; they show right in the page. For a PDF, **Open in new tab** gives a bigger view |
| PowerPoint files | Click **Download** and open them in PowerPoint, Keynote or Google Slides |
| Make a new file | Click **New**. Type `folder/name.md` to put it in a folder |
| Rename, move or delete | Use the buttons above the file |
| Update the box labels | Click **Rebuild box labels** after editing `packaging/build_cartons.py` (flavors, colors, ingredients) |
| Update the cost study | Click **Rebuild cost study** after editing numbers in `finance/cost_model.py` |
| Back up your changes | Click **Save to GitHub**, describe what you changed, and press **Save changes and upload** |

Files you've changed but not yet saved to GitHub have an orange dot in the list.

## The rebuild buttons need extra tools

Viewing and editing need only Python. The two **Rebuild** buttons also need:

- **Node.js** (from nodejs.org)
- In the project folder, once:

```bash
npm install playwright pptxgenjs sharp
```

```bash
npx playwright install chromium
```

If a tool is missing, the rebuild panel says which one.

## Save to GitHub needs git

**Save to GitHub** works when the project was downloaded with git (not as a ZIP)
and your computer is signed in to GitHub. The easiest way to set that up is
GitHub Desktop (desktop.github.com): clone the repository with it, then use the
studio as normal.

## Good to know

- The studio only opens files inside the project folder.
- It can only run the two rebuild tasks; it can't run other commands.
- Another website can't control it: each session uses a private key that only
  the studio page knows.
- If port 8765 is busy, start it on another one:
  `python3 studio/bright_studio.py --port 8766`
