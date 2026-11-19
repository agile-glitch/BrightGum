"""Trace the chosen bright logo image into vector paths.

The boxes, cost study and studio all draw the logo from the paths this script
writes, so they match the chosen artwork exactly instead of an approximation.

    python3 brand/logo/trace_logo.py <logo image> [<second image of the same logo to cross-check>]

Needs: pip install pillow numpy potracer
Writes: brand/logo/logo_paths.json and the four bright-logo-*.svg files.
"""
import json
import sys
from pathlib import Path

import numpy as np
import potrace
from PIL import Image

OUT = Path(__file__).parent
INK, BLUE, PAPER = "#0D1117", "#1428DC", "#FFFFFF"
UPSCALE = 3          # trace at 3x for smooth curves
PAD = 0.045          # clear space around the logo, as a share of its width


def masks(path, scale=1):
    im = Image.open(path).convert("RGB")
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    a = np.asarray(im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    eye = (b - r > 70) & (b > 120)                 # the blue square
    ink = (lum < 110) & ~eye & (b - r < 40)        # the black wordmark and face
    return ink, eye


def bbox(m):
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def keep_main(ink, eye):
    """Drop specks far from the logo: keep rows/columns inside the dense band of ink."""
    x0, y0, x1, y1 = bbox(ink | eye)
    return ink[y0:y1, x0:x1], eye[y0:y1, x0:x1]


def path_d(mask, ox, oy, k):
    bm = potrace.Bitmap(~mask)      # the tracer fills where values are low (dark), so invert the mask
    plist = bm.trace(turdsize=int(40 * UPSCALE), alphamax=1.0, opticurve=True, opttolerance=0.5)
    f = lambda p: f"{(p.x + ox) * k:.1f},{(p.y + oy) * k:.1f}"
    d = []
    for curve in plist:
        d.append("M" + f(curve.start_point))
        for s in curve.segments:
            d.append(f"L{f(s.c)}L{f(s.end_point)}" if s.is_corner else f"C{f(s.c1)} {f(s.c2)} {f(s.end_point)}")
        d.append("Z")
    return "".join(d)


def main():
    src = sys.argv[1]
    ink, eye = keep_main(*masks(src, UPSCALE))
    h, w = ink.shape
    if len(sys.argv) > 2:      # cross-check against a second image of the same logo
        i2, e2 = keep_main(*masks(sys.argv[2], 1))
        both = Image.fromarray(((i2 | e2) * 255).astype("uint8")).resize((w, h), Image.LANCZOS)
        b2 = np.asarray(both) > 127
        b1 = ink | eye
        print(f"match with second image: {(b1 & b2).sum() / (b1 | b2).sum():.1%} overlap")

    # normalise to a 1000-wide drawing with clear space around it
    k = 1000 / (w * (1 + 2 * PAD))
    pad = w * PAD
    vb_w, vb_h = 1000, round((h + 2 * pad) * k, 1)
    data = {"viewBox": [0, 0, vb_w, vb_h], "ratio": vb_w / vb_h,
            "ink": path_d(ink, pad, pad, k), "eye": path_d(eye, pad, pad, k), "source": Path(src).name}
    (OUT / "logo_paths.json").write_text(json.dumps(data))

    def svg(ink_c, eye_c, bg=None):
        rect = f'<rect width="{vb_w}" height="{vb_h}" fill="{bg}"/>' if bg else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" '
                f'role="img" aria-label="bright logo">{rect}<path fill="{ink_c}" fill-rule="evenodd" d="{data["ink"]}"/>'
                f'<path fill="{eye_c}" d="{data["eye"]}"/></svg>\n')
    (OUT / "bright-logo-primary.svg").write_text(svg(INK, BLUE))
    (OUT / "bright-logo-on-blue.svg").write_text(svg(INK, PAPER, BLUE))
    (OUT / "bright-logo-on-green.svg").write_text(svg(INK, PAPER, "#5B7046"))
    (OUT / "bright-logo-reversed.svg").write_text(svg(PAPER, BLUE, INK))
    print(f"viewBox 0 0 {vb_w} {vb_h} (ratio {data['ratio']:.3f}); ink path {len(data['ink'])} chars, eye {len(data['eye'])} chars")


if __name__ == "__main__":
    main()
