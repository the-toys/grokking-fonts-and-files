# Grokking Fonts & Files

A hands-on, browser-based tutorial that takes you from "what even is a font file" to
reading and building OpenType fonts with confidence. Every fact is grounded in two real
fonts (LXGW WenKai Mono GB and LXGW ZhenKai GB) rather than abstract spec prose.

> **Status — work in progress.** Modules **1 (sfnt container)** and **2 (cmap & glyph IDs)** are
> deep, reviewed, and byte-verified end to end. Modules **3–7** are drafted in the same shape and
> still being iterated/optimized — their finer details aren't final yet. The two real fonts are
> bundled (via Git LFS) so anyone can reproduce and check every number.

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
specimens/fonts/        the two real fonts (Git LFS) + their OFL license
```

## The curriculum

| # | Module | Core question | Status |
|---|--------|---------------|--------|
| 1 | The sfnt container | How is a font file laid out? | ✅ verified |
| 2 | cmap & glyph IDs | How does a character become a glyph? | ✅ verified |
| 3 | Outlines | How is a glyph drawn? | 🔧 iterating |
| 4 | Metrics & the em | What makes text line up? | 🔧 iterating |
| 5 | Identity & families | How do separate files become one family? | 🔧 iterating |
| 6 | Shaping & layout | How do glyphs combine and move? | 🔧 iterating |
| 7 | Packaging & frontiers | Collections, variable fonts, web fonts | 🔧 iterating |

## Reproduce the data

The two source fonts are bundled in `specimens/fonts/` via **Git LFS**, so first make sure LFS
is installed (`git lfs install`) and the files are pulled (`git lfs pull`):

```sh
specimens/extract.py specimens/fonts/LXGWWenKaiMonoGB-Regular.ttf
specimens/extract.py specimens/fonts/*.ttf
```

Output matches `specimens/SPECIMENS.md`. Nothing in the lessons is invented — run it and check.

## Fonts & license

The tutorial text and code are the author's. The two bundled fonts in `specimens/fonts/` —
**LXGW WenKai Mono GB** (v1.522) and **LXGW ZhenKai GB** (v0.825) — are © LXGW and the Klee Project
Authors, redistributed **unmodified** under the **SIL Open Font License 1.1**; see
`specimens/fonts/OFL.txt`. Upstream: <https://github.com/lxgw/LxgwWenkaiGB> and
<https://github.com/lxgw/LxgwZhenKai>.

## Exercises

Each module has exercises (concept questions or programming tasks). Attempt them,
then have your tutor (AI agents) check your answers. Hints and self-check solutions are tucked behind
collapsible sections.
