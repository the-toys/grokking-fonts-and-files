#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools>=4.50"]
# ///
"""
Reproduce every specimen used in this tutorial straight from the real fonts.

Point it at the source .ttf files (and optionally the built .ttc):

    ./extract.py /path/to/LXGWWenKaiMonoGB-Regular.ttf
    ./extract.py wen.ttf zhen.ttf hybrid.ttc

Output should match specimens/SPECIMENS.md. This is the "show your work" file:
nothing in the lessons is invented -- run this and check.
"""
from __future__ import annotations
import sys
from fontTools.ttLib import TTFont, TTCollection  # pyright: ignore[reportMissingImports]


def dump_ttf(path: str) -> None:
    print(f"\n===== {path} =====")
    f = TTFont(path, lazy=True)
    r = f.reader
    print(f"sfntVersion={r.sfntVersion!r}  numTables={r.numTables}  unitsPerEm={f['head'].unitsPerEm}")

    print("-- table directory (offset/length) --")
    for tag in r.keys():
        e = r.tables[tag]
        print(f"  {tag:5} {e.offset:>10} {e.length:>10}")

    print("-- cmap subtables --")
    for t in f["cmap"].tables:
        print(f"  platformID={t.platformID} platEncID={t.platEncID} format={t.format} n={len(t.cmap)}")
    best = f.getBestCmap()
    for ch in "A一永龥":
        print(f"  U+{ord(ch):04X} {ch!r} -> {best.get(ord(ch))}")

    print("-- metrics --")
    hmtx = f["hmtx"]
    for ch in "A一i":
        gn = best.get(ord(ch))
        if gn:
            print(f"  {ch!r} advance,lsb = {hmtx[gn]}")
    hhea, os2 = f["hhea"], f["OS/2"]
    print(f"  hhea asc/desc/gap = {hhea.ascent}/{hhea.descent}/{hhea.lineGap}")
    print(f"  OS/2 typo asc/desc/gap = {os2.sTypoAscender}/{os2.sTypoDescender}/{os2.sTypoLineGap}")

    print("-- identity (OS/2 + head + name) --")
    head = f["head"]
    print(f"  usWeightClass={os2.usWeightClass} fsSelection={bin(os2.fsSelection)} "
          f"macStyle={bin(head.macStyle)} vendID={os2.achVendID}")
    if hasattr(os2, "panose"):
        print(f"  PANOSE={list(os2.panose.__dict__.values())}")
    for rec in f["name"].names:
        if rec.nameID in (1, 2, 4, 6) and rec.platformID == 3:
            print(f"  name id={rec.nameID} -> {rec.toUnicode()!r}")

    print("-- outline of '一' --")
    glyf = f["glyf"]
    g = glyf[best[ord("一")]]
    if not g.isComposite():
        coords, endPts, flags = g.getCoordinates(glyf)
        print(f"  contours={g.numberOfContours} points={len(coords)} endPts={list(endPts)}")
        print(f"  first6 coords={list(coords[:6])}")
        print(f"  first6 onCurve={[fl & 1 for fl in flags[:6]]}")

    print("-- shaping (GSUB/GPOS) --")
    for tag in ("GSUB", "GPOS"):
        if tag in f:
            t = f[tag].table
            scripts = [s.ScriptTag for s in t.ScriptList.ScriptRecord]
            feats = sorted({fr.FeatureTag for fr in t.FeatureList.FeatureRecord})
            print(f"  {tag}: scripts={scripts} lookups={len(t.LookupList.Lookup)} features={feats}")


def dump_ttc(path: str) -> None:
    print(f"\n===== {path} (collection) =====")
    c = TTCollection(path, lazy=True)
    print(f"numFonts={len(c.fonts)}")
    shared: dict[int, list[int]] = {}
    for i, sub in enumerate(c.fonts):
        go = sub.reader.tables["glyf"].offset
        shared.setdefault(go, []).append(i)
    print(f"distinct glyf offsets = {len(shared)} (few => shareTables worked)")
    for go, faces in shared.items():
        print(f"  glyf@{go} shared by faces {faces}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    for p in args:
        (dump_ttc if p.lower().endswith(".ttc") else dump_ttf)(p)


if __name__ == "__main__":
    main()
