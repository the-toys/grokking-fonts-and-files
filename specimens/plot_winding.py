#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools>=4.50", "matplotlib>=3.7"]
# ///
"""
Generate specimens/winding.png — how nested contours + the non-zero winding
rule make holes. Real glyphs straight from the font; nothing invented.

    ./plot_winding.py specimens/fonts/LXGWWenKaiMonoGB-Regular.ttf
"""
from __future__ import annotations
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, FancyArrowPatch
from matplotlib.lines import Line2D
from fontTools.ttLib import TTFont  # pyright: ignore[reportMissingImports]
from fontTools.pens.recordingPen import RecordingPen  # pyright: ignore[reportMissingImports]

ON = "#2660c4"     # outer contour (filled side)
HOLE = "#d33d4b"   # hole contour (wound the other way)
FILL = "#cfe0f7"
INK = "#22303f"


def midpoint(a, b):
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def glyph_path_and_contours(font, name):
    """Return (matplotlib Path with real quadratics, list-of-contour-vertex-lists)."""
    pen = RecordingPen()
    font.getGlyphSet()[name].draw(pen)
    verts, codes = [], []
    contours = []          # on-curve vertex polyline per contour (for arrows + winding)
    cur = None
    poly = []
    for op, args in pen.value:
        if op == "moveTo":
            cur = args[0]
            poly = [cur]
            verts.append(cur); codes.append(Path.MOVETO)
        elif op == "lineTo":
            cur = args[0]
            poly.append(cur)
            verts.append(cur); codes.append(Path.LINETO)
        elif op == "qCurveTo":
            pts = list(args)
            end = pts.pop()                      # last point is on-curve
            ctrls = pts                          # the rest are off-curve controls
            # expand a run of N controls into N quadratics via implied midpoints
            for i, c in enumerate(ctrls):
                target = end if i == len(ctrls) - 1 else midpoint(c, ctrls[i + 1])
                verts.append(c); codes.append(Path.CURVE3)
                verts.append(target); codes.append(Path.CURVE3)
                cur = target
            poly.append(end)
        elif op == "closePath":
            verts.append((0, 0)); codes.append(Path.CLOSEPOLY)
            contours.append(poly)
            poly = []
    return Path(verts, codes), contours


def shoelace(poly):
    a = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2.0   # >0 CCW, <0 CW (y up)


def draw_dir_arrows(ax, poly, color):
    """A few arrows along the polyline showing traversal direction."""
    n = len(poly)
    if n < 2:
        return
    for frac in (0.18, 0.5, 0.82):
        i = max(1, int(frac * n))
        a = poly[i - 1]; b = poly[i % n]
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=16,
                                     color=color, lw=0, zorder=6))


def panel_glyph(ax, font, name, title):
    path, contours = glyph_path_and_contours(font, name)
    ax.add_patch(PathPatch(path, facecolor=FILL, edgecolor=INK, lw=1.6, zorder=2))
    for poly in contours:
        ccw = shoelace(poly) > 0
        col = HOLE if ccw else ON
        draw_dir_arrows(ax, poly, col)
    xs = [p[0] for c in contours for p in c]
    ys = [p[1] for c in contours for p in c]
    pad = 80
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("x →"); ax.set_ylabel("y ↑")
    ax.grid(True, color="#e6e6e6")


def panel_schematic(ax):
    """Ray-cast winding count: nested rectangles, a ray, signed crossings."""
    ox0, ox1, oy0, oy1 = 1, 11, 1, 7          # outer rectangle (clockwise)
    ix0, ix1, iy0, iy1 = 4.2, 7.8, 3, 5       # inner rectangle (counter-clockwise)
    ax.add_patch(PathPatch(Path([(ox0, oy0), (ox1, oy0), (ox1, oy1), (ox0, oy1), (0, 0),
                                 (ix0, iy0), (ix0, iy1), (ix1, iy1), (ix1, iy0), (0, 0)],
                                [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY,
                                 Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]),
                           facecolor=FILL, edgecolor=INK, lw=1.6))
    ax.annotate("outer ↻ clockwise", ((ox0 + ox1) / 2, oy1 - 0.55), ha="center",
                color=ON, fontsize=11, weight="bold")
    ax.annotate("inner ↺ counter-clockwise (carves the hole)", ((ox0 + ox1) / 2, iy0 - 0.7),
                ha="center", color=HOLE, fontsize=10.5, weight="bold")
    # ray from a point P in the HOLE going right: crosses inner (+1) then outer (−1) → 0
    py = 4
    ax.annotate("", xy=(ox1 + 1.6, py), xytext=(5.5, py),
                arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.6, ls=(0, (4, 3))))
    ax.plot(5.5, py, "o", color="#555", ms=7)
    ax.annotate("P", (5.25, py + 0.25), fontsize=11)
    ax.plot([ix1], [py], "|", color=HOLE, ms=14, mew=2)
    ax.plot([ox1], [py], "|", color=ON, ms=14, mew=2)
    ax.annotate("+1", (ix1 + 0.1, py + 0.45), color=HOLE, fontsize=12, ha="center", weight="bold")
    ax.annotate("−1", (ox1 + 0.1, py + 0.45), color=ON, fontsize=12, ha="center", weight="bold")
    ax.annotate("sum at P = +1 − 1 = 0  ⇒  outside ⇒ empty (the hole)",
                ((ox0 + ox1) / 2, oy0 - 0.9), ha="center", fontsize=10.5)
    ax.annotate("a point in the ring crosses only the outer edge once ⇒ sum = ±1 ⇒ filled",
                ((ox0 + ox1) / 2, oy0 - 1.7), ha="center", fontsize=10.5, color=INK)
    ax.set_xlim(-0.3, 13.4); ax.set_ylim(-1.5, 7.4)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("non-zero winding: cast a ray, add signed crossings", fontsize=12)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "specimens/fonts/LXGWWenKaiMonoGB-Regular.ttf"
    font = TTFont(path)
    cmap = font.getBestCmap()
    if cmap is None:
        raise SystemExit("font has no usable Unicode cmap")
    fig = plt.figure(figsize=(17, 9))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.25, 1])
    glyphs = [
        (0x6C38, "U+6C38 'eternal' — 3 contours, all\nsame winding ⇒ NO hole"),
        (0x53E3, "U+53E3 'mouth' — outer + 1 hole"),
        (0x65E5, "U+65E5 'sun' — outer + 2 holes"),
        (0x56DE, "U+56DE 'return' — nested rings, 2 holes"),
    ]
    for col, (cp, title) in enumerate(glyphs):
        panel_glyph(fig.add_subplot(gs[0, col]), font, cmap[cp], title)
    panel_schematic(fig.add_subplot(gs[1, :]))
    fig.suptitle("Contours, holes & the non-zero winding rule (font units, y up)", fontsize=15)
    handles = [
        Line2D([], [], color=ON, lw=3, label="contour wound clockwise (fills its inside)"),
        Line2D([], [], color=HOLE, lw=3, label="contour wound counter-clockwise (carves a hole)"),
        Line2D([], [], color=FILL, lw=8, label="filled region (the glyph)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=11)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    out = "specimens/winding.png"
    fig.savefig(out, dpi=105)
    print("wrote", out)


if __name__ == "__main__":
    main()
