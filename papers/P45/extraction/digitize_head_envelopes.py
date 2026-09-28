"""Measure the riser-head deflection envelopes of P45 Figures 4(a)-9(a).

Provenance tool for ``papers/P45/reference/figure4_9_head_envelopes.json``.
It needs the page images of the private source PDF, which are NOT part of the
repository. Produce them from a legally obtained copy with poppler:

    pdfimages -png p45-safai1983.pdf <outdir>/pg

(the source is a 300 dpi bilevel scan; pages are written as pg-000.png ... pg-010.png)
and run:

    python papers/P45/extraction/digitize_head_envelopes.py <outdir>

Method (numbers only are written; no raster data):
1. x calibration: the four tick marks just above each x-axis line, fitted by least
   squares to the axis labels. The labels are metric renderings of round feet
   (5/10/15/20 ft etc.), so the feet values are used.
2. y calibration: five equally spaced tick marks beside the y-axis, fitted to the
   labelled heights (feet values).
3. The plotted curves form one connected ink component (they join at the ball
   joint). Its top 60 px are split into column bundles; each bundle's tip
   (topmost 4 px) gives one head-end deflection. Bundles below 10% of the axis
   full scale are the y-axis line tip and are discarded.
4. Uncertainty per value: max tick residual + 6 px line width (in metres).
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

FT = 0.3048
FIGS = {
    "4(a)": dict(case=1, page=4, box=(150, 690, 1060, 1860), xt_ft=[5, 10, 15, 20], yt_ft=[100, 200, 300, 400, 500]),
    "5(a)": dict(case=2, page=4, box=(1290, 0, 2200, 1360), xt_ft=[5, 10, 15, 20], yt_ft=[100, 200, 300, 400, 500]),
    "6(a)": dict(case=3, page=5, box=(170, 740, 1110, 1870), xt_ft=[12.5, 25, 37.5, 50], yt_ft=[300, 600, 900, 1200, 1500]),
    "7(a)": dict(case=4, page=5, box=(1290, 150, 2200, 1300), xt_ft=[12.5, 25, 37.5, 50], yt_ft=[300, 600, 900, 1200, 1500]),
    "8(a)": dict(case=5, page=6, box=(170, 520, 1060, 1860), xt_ft=[25, 50, 75, 100], yt_ft=[600, 1200, 1800, 2400, 3000]),
    "9(a)": dict(case=6, page=6, box=(1290, 180, 2200, 1280), xt_ft=[25, 50, 75, 100], yt_ft=[600, 1200, 1800, 2400, 3000]),
}
LINE_WIDTH_PX = 6


def _cluster(idx, gap=4):
    out, grp = [], []
    for i in idx:
        if grp and i - grp[-1] > gap:
            out.append(float(np.mean(grp))); grp = []
        grp.append(i)
    if grp:
        out.append(float(np.mean(grp)))
    return out


def _equal_spaced(c, n):
    best = None
    for combo in itertools.combinations(c, n):
        d = np.diff(combo)
        score = float(np.std(d) / np.mean(d)) if np.mean(d) > 50 else 9.0
        if best is None or score < best[0]:
            best = (score, list(combo))
    if not best or best[0] >= 0.05:
        raise ValueError("no equally spaced tick set found")
    return best[1], best[0]


def _fit(px, val):
    a, b = np.polyfit(px, val, 1)
    return float(a), float(b), float(np.max(np.abs(np.array(val) - (a * np.array(px) + b))))


def measure(name, f, page_dir: Path):
    ink = np.array(Image.open(page_dir / f"pg-{f['page']:03d}.png").convert("L")) < 128
    x0, y0, x1, y1 = f["box"]
    sub = ink[y0:y1, x0:x1]
    h, w = sub.shape
    xr = int(np.argmax(sub[h // 2:, :].sum(axis=1))) + h // 2
    yc = int(np.argmax(sub[:, : w // 2].sum(axis=0)))
    xprof = sub[xr - 10:xr - 2, :].sum(axis=0)
    xt, _ = _equal_spaced(_cluster([c for c in range(40, w) if xprof[c] >= 3]), 4)
    ax, bx, rx = _fit(xt, [v * FT for v in f["xt_ft"]])
    origin = -bx / ax
    best = yt = None
    for lo, hi in ((3, 10), (-10, -2)):
        for base in (yc, int(origin)):
            yprof = sub[:, base + lo: base + hi].sum(axis=1)
            for thr in (3, 4, 5):
                cands = _cluster([r for r in range(0, xr - 20) if yprof[r] >= thr])
                if not 5 <= len(cands) <= 14:
                    continue
                try:
                    sel, score = _equal_spaced(cands, 5)
                except ValueError:
                    continue
                if best is None or score < best:
                    best, yt = score, sel
    ay, by, ry = _fit(yt, [v * FT for v in f["yt_ft"]][::-1])
    top_row = int(min(yt)) - 120
    off = int(origin) + 6
    region = sub[top_row: xr - 4, off: w]
    lab, _ = ndimage.label(region, structure=np.ones((3, 3)))
    tips = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl[0].stop - sl[0].start < 0.25 * (xr - top_row):
            continue
        ys, xs = np.where(lab[sl] == i)
        ys, xs = ys + sl[0].start, xs + sl[1].start
        band = ys <= ys.min() + 60
        cols = np.sort(np.unique(xs[band]))
        groups, g = [], [cols[0]]
        for c in cols[1:]:
            if c - g[-1] > 12:
                groups.append(g); g = [c]
            else:
                g.append(c)
        groups.append(g)
        for g in groups:
            m = band & (xs >= g[0]) & (xs <= g[-1])
            gt = ys[m].min()
            tip = xs[m & (ys <= gt + 4)]
            tips.append((gt + top_row, tip.min() + off, tip.max() + off))
    to_m = lambda c: ax * c + bx
    to_h = lambda r: ay * r + by
    ends = sorted(
        [{"deflection_m": [round(to_m(a), 3), round(to_m(b), 3)], "tip_height_m": round(to_h(r), 2)}
         for r, a, b in tips if to_m(b) > 0.1 * f["xt_ft"][-1] * FT],  # discard the y-axis line tip
        key=lambda e: e["deflection_m"][0])
    u = rx + LINE_WIDTH_PX * abs(ax)
    lo_edge, hi_edge = ends[0]["deflection_m"][0], ends[-1]["deflection_m"][1]
    return {
        "figure": name, "case": f["case"],
        "x_scale_m_per_px": round(abs(ax), 6), "x_tick_residual_m": round(rx, 4), "y_tick_residual_m": round(ry, 3),
        "tip_bundles": ends,
        "head_envelope_min_m": lo_edge, "head_envelope_max_m": hi_edge,
        "uncertainty_m": round(u, 3),
    }


def main(page_dir: str) -> dict:
    return {
        "schema_version": "engiproof.p45.figure_digitization/1.0",
        "source_pages": "pdfimages -png of the canonical source PDF (300 dpi bilevel scan)",
        "method": __doc__.split("Method")[1].strip(),
        "figures": [measure(k, v, Path(page_dir)) for k, v in FIGS.items()],
    }


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=2))
