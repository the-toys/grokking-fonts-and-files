#!/usr/bin/env python
"""Build (and self-verify) the two font CTF challenge artifacts.

Both are subset from a real specimen font, so every glyph is genuine.

  cmap_swap.ttf   — the flag lives ONLY in the character->glyph map.
                    A run of Private-Use code points (U+E000…) renders as the
                    flag; nothing else in the file spells it out.  (Module 2)

  gsub_reveal.ttf — the cmap is honest (every char maps to itself).  A GSUB
                    'calt' rule rewrites a single seed character into the whole
                    flag at shaping time.  (Module 6)

Run it and it prints PASS/PASS.  Nothing here is hand-waved:

    ~/.venv/bin/python specimens/ctf/build_ctf.py
"""
import os
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "fonts", "LXGWWenKaiMonoGB-Regular.ttf")

FLAG_CMAP = "flag{c0d3po1nts_can_l13}"
FLAG_GSUB = "flag{gsub_1s_a_r3wr1t3r}"
SEED = "@"                      # honest glyph that GSUB explodes into the flag
PUA0 = 0xE000                   # first decoy Private-Use code point


def load_reverse_names():
    """glyph name -> the character it draws, from the pristine source cmap."""
    f = TTFont(SRC)
    return {gname: chr(cp) for cp, gname in f.getBestCmap().items()}


def subset(text, extra_glyphs=()):
    """A fresh, minimal TTFont covering exactly `text` (+ any extra glyphs)."""
    f = TTFont(SRC)
    opt = Options()
    opt.glyph_names = True          # keep post names (the tutorial reads them)
    opt.recalc_bounds = True
    opt.layout_features = ["*"]
    ss = Subsetter(options=opt)
    ss.populate(text=text, glyphs=list(extra_glyphs))
    ss.subset(f)
    return f


def name_of(font, ch):
    return font.getBestCmap()[ord(ch)]


# ─────────────────────────── challenge 1: cmap swap ───────────────────────────
def build_cmap_swap(rev):
    font = subset(FLAG_CMAP)
    # Keep this challenge purely about the cmap: drop the layout tables the
    # subsetter carried over from the source, so there's no shaping distraction.
    for t in ("GSUB", "GPOS", "GDEF"):
        if t in font:
            del font[t]
    # Glyph that draws each flag character, in flag order:
    glyph_seq = [name_of(font, ch) for ch in FLAG_CMAP]
    # Wipe the honest cmap; install a decoy PUA -> flag-glyph mapping instead.
    decoy = {PUA0 + i: g for i, g in enumerate(glyph_seq)}
    for sub in font["cmap"].tables:
        sub.cmap = dict(decoy)
    out = os.path.join(HERE, "cmap_swap.ttf")
    font.save(out)

    # write the "leaked" decoy string (the PUA code points, in order)
    leaked = "".join(chr(PUA0 + i) for i in range(len(FLAG_CMAP)))
    with open(os.path.join(HERE, "leaked.txt"), "w", encoding="utf-8") as fh:
        fh.write(leaked)

    # VERIFY: invert the shipped cmap exactly as a solver would.
    g = TTFont(out)
    m = g.getBestCmap()
    recovered = "".join(rev[m[cp]] for cp in sorted(m))
    ok = recovered == FLAG_CMAP
    # The post glyph NAMES reveal the SET of letters, but the flag order lives
    # only in the cmap — so dumping post alone must NOT spell the flag.
    order_str = "".join(rev.get(g, "") for g in g.getGlyphOrder())
    leak = FLAG_CMAP in order_str
    print(f"cmap_swap.ttf  {os.path.getsize(out):>6} B  "
          f"recovered={recovered!r}  {'PASS' if ok else 'FAIL'}")
    print(f"    glyph-order string = {order_str!r}  "
          f"(post-dump leaks flag in order: {leak})")
    return ok and not leak


# ─────────────────────────── challenge 2: GSUB reveal ─────────────────────────
def build_gsub_reveal(rev):
    font = subset(FLAG_GSUB + SEED)
    seed_g = name_of(font, SEED)
    flag_gs = [name_of(font, ch) for ch in FLAG_GSUB]
    fea = (
        "languagesystem DFLT dflt;\n"
        "languagesystem latn dflt;\n"
        "feature calt {\n"
        f"    sub {seed_g} by {' '.join(flag_gs)};\n"
        "} calt;\n"
    )
    addOpenTypeFeaturesFromString(font, fea)
    out = os.path.join(HERE, "gsub_reveal.ttf")
    font.save(out)

    # VERIFY: shape the lone seed with HarfBuzz; the run must spell the flag.
    import uharfbuzz as hb
    with open(out, "rb") as fh:
        face = hb.Face(fh.read())
    hb_font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(SEED)
    buf.guess_segment_properties()
    hb.shape(hb_font, buf, {"calt": True})
    order = font.getGlyphOrder()
    shaped = "".join(rev[order[info.codepoint]] for info in buf.glyph_infos)
    ok = shaped == FLAG_GSUB
    print(f"gsub_reveal.ttf {os.path.getsize(out):>6} B  "
          f"shaped({SEED})={shaped!r}  {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    rev = load_reverse_names()
    ok1 = build_cmap_swap(rev)
    ok2 = build_gsub_reveal(rev)
    raise SystemExit(0 if (ok1 and ok2) else 1)
