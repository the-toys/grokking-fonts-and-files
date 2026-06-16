# Grokking Fonts & Files

A hands-on, browser-based tutorial that takes you from "what even is a font file" to
reading and building OpenType fonts with confidence. Every fact is grounded in two real
fonts (LXGW WenKai Mono GB and LXGW ZhenKai GB) rather than abstract spec prose.

## Run it

It's a static site — no build step.

```sh
open index.html          # macOS
# or serve it so relative links behave everywhere:
python3 -m http.server   # then visit http://localhost:8000
```

## Layout

```
index.html              course home + module cards
modules/                one HTML page per module (01–07)
assets/style.css        shared styling (dark/light auto)
assets/app.js           sidebar nav, progress (localStorage), copy buttons
specimens/SPECIMENS.md  every verified number/byte used in the lessons
specimens/extract.py    reproduce all specimens from the real fonts (fonttools)
```

## The curriculum

| # | Module | Core question |
|---|--------|---------------|
| 1 | The sfnt container | How is a font file laid out? |
| 2 | cmap & glyph IDs | How does a character become a glyph? |
| 3 | Outlines | How is a glyph drawn? |
| 4 | Metrics & the em | What makes text line up? |
| 5 | Identity & families | How do separate files become one family? |
| 6 | Shaping & layout | How do glyphs combine and move? |
| 7 | Packaging & frontiers | Collections, variable fonts, web fonts |

## Reproduce the data

```sh
specimens/extract.py /path/to/LXGWWenKaiMonoGB-Regular.ttf
specimens/extract.py wen.ttf zhen.ttf hybrid.ttc
```

Output matches `specimens/SPECIMENS.md`. Nothing in the lessons is invented — run it and check.

## Exercises

Each module ends with exercises (concept questions or programming tasks). Attempt them,
then have your tutor check your answers. Hints and self-check solutions are tucked behind
collapsible sections.
