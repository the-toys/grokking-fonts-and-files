# Verified specimens

Every number/byte in this tutorial comes from these two real files (pinned upstream releases):

- `LXGWWenKaiMonoGB-Regular.ttf` — LXGW WenKai Mono GB v1.522 (~25 MB)
- `LXGWZhenKaiGB-Regular.ttf` — LXGW ZhenKai GB v0.825 (~17 MB)
- `LXGWHybrid.ttc` — the hybrid collection built by `lxgw-wenkai-zhenkai/build.py` (~42 MB)

Reproduce all of this with `specimens/extract.py` (uses fontTools).

## Header (WenKai .ttf, first 12 bytes)

```
00 01 00 00   00 11   01 00   00 04   00 10
sfntVersion   numTab  srchRng entSel  rngShift
0x00010000=TT 17      256     4       16
```

`searchRange/entrySelector/rangeShift` derive from numTables: 2^4=16 ≤ 17 → 16×16=256, log2 16=4, 17×16−256=16.

## Table directory (WenKai .ttf, 17 tables)

```
tag      offset       length
head        284           54
hhea        340           36
maxp        376           32
OS/2        408           96
hmtx        504       187302
cmap     187808       217212
prep     405020            7
loca     405028       187324
glyf     592352     24708009   (24.7 MB of 25 MB)
name   25300364         1190
post   25301556       446366
gasp   25747924            8
GPOS   25747932          420
GSUB   25748352         5564
meta   25753916           69
vhea   25753988           36
vmtx   25754024        93662
```

Directory entries are sorted by **tag** (ASCII ascending: GPOS,GSUB,OS/2,cmap,...). Table bodies are laid out in a **different** physical order (head first @284, glyf huge block in middle, GPOS near end). First directory record raw bytes:
`47 50 4f 53 | db 9e 76 46 | 01 88 e1 dc | 00 00 01 a4` = tag "GPOS", checksum, offset 25747932, length 420.

OS/2 record raw: `4f 53 2f 32 | fe 89 fd aa | 00 00 01 98 | 00 00 00 60` = offset 408, length 96.

## cmap (Module 2)

5 subtables:
```
platformID  platEncID  format  nMappings   meaning
0           3          4       43498       Unicode, BMP only (16-bit)
0           4          12      46510       Unicode, full range (32-bit)
0           5          14      0           Unicode Variation Sequences (empty)
3           1          4       43498       Windows, BMP (16-bit)
3           10         12      46510       Windows, full Unicode (32-bit)
```
- platformID: 0=Unicode, 3=Windows, 1=Mac. (3,1)=Windows BMP, (3,10)=Windows full.
- format 4 = segmented 16-bit (BMP); format 12 = segmented 32-bit (all planes); format 14 = variation selectors.
- The two format-12 tables map 46510 codepoints; numGlyphs is 46830.

Sample mappings (getBestCmap):
```
U+0041 'A' -> glyph name "A"
U+4E00 '一' -> glyph name "u4E00"
U+6C38 '永' -> glyph name "u6C38"
U+9FA5 '龥' -> glyph name "u9FA5"  (last char of the CJK Unified base block)
```

## Outlines (Module 3) — TrueType quadratic, glyf+loca

`head.indexToLocFormat = 1` → loca uses 32-bit (long) offsets.

Simple glyph '一' (U+4E00, glyph "u4E00"):
- isComposite=False, numberOfContours=1, 21 points, endPtsOfContours=[20]
- first 6 coords: (110,383) (837,420) (861,422) (881,430) (893,430) (921,413)
- first 6 on-curve flags: 1 1 0 0 0 0  (1=on-curve corner/anchor, 0=off-curve control point)

Simple glyph '十' (U+5341): 1 contour, 46 points, on-curve flags start 1 1 0 1 0 1.

Composite glyphs (reuse other glyphs as components):
- "dieresis" → 1 component, base glyph "dieresiscomb" placed at (x=500, y=0)
- "acute" → 1 component, base glyph "acutecomb" placed at (x=517, y=0)

## Metrics (Module 4)

- unitsPerEm = 1000, numGlyphs = 46830, numberOfHMetrics = 46821
- advance, leftSideBearing (font units):
  - 'A' = (500, 21)
  - '一' = (1000, 59)   → full-width = exactly 1 em
  - 'i' = (500, 73)
- Latin 'A','i' advance = 500 = **half** em → this Mono's Latin is half-width; 2 Latin cells = 1 CJK cell.
- hhea: ascent 928, descent -241, lineGap 0
- OS/2: sTypoAscender 880, sTypoDescender -120, sTypoLineGap 0; usWinAscent 928, usWinDescent 241

ZhenKai '一' advance is also 1000/1000 em — build.py prints this equality as proof no re-metricizing is needed.

## Identity (Module 5) — OS/2, head, name (the build.py module)

WenKai source values:
- OS/2 version 4, usWeightClass **400**, usWidthClass 5 (Medium/normal)
- fsSelection = 0b1000000 = bit 6 set = REGULAR (0x40). (bit 0=ITALIC 0x01, bit 5=BOLD 0x20, bit 6=REGULAR 0x40)
- achVendID "LXGW"
- PANOSE = [2, 2, 5, 9, 0, 0, 0, 0, 0, 0]  (byte0=2 Latin Text; byte3=bProportion=9=Monospaced)
- head.macStyle = 0b0 (no bold, no italic), head.flags = 0b100101011, fontRevision 1.522, indexToLocFormat 1

name records (platform 3 = Windows):
```
id 1  (Family)            "LXGW WenKai Mono GB"   /  Chinese: "霞鹜文楷等宽 GB"
id 2  (Subfamily)         "Regular"
id 4  (Full name)         "LXGW WenKai Mono GB"
id 6  (PostScript name)   "LXGWWenKaiMonoGB-Regular"
id 16 (Typographic family) — (used to override 1 when present)
id 17 (Typographic subfamily)
```

build.py rewrites ids 1,2,3,4,6, removes 16/17, sets usWeightClass (400 vs 700), flips fsSelection BOLD/REGULAR + head.macStyle, and sets post.isFixedPitch + panose.bProportion (9 mono / 3 modern).

## Shaping (Module 6) — GSUB / GPOS

```
GSUB: scripts = DFLT bopo grek hani kana latn
      12 lookups
      features = afrc calt ccmp frac salt subs sups vert
GPOS: scripts = DFLT bopo grek hani kana latn
       3 lookups
      features = halt vert vhal
```
Feature tags: vert=vertical alternates, vhal/halt=vertical/horizontal alt metrics, calt=contextual alternates, ccmp=glyph composition/decomposition, frac/afrc=fractions, sups/subs=super/subscript, salt=stylistic alternates. Scripts: hani=Han, kana=Kana, bopo=Bopomofo, grek=Greek, latn=Latin, DFLT=default.

## Packaging (Module 7) — TTC

- `LXGWHybrid.ttc`: magic "ttcf", **18 faces / 9 families**, ~42 MB (≈ size of the two sources, not 9×).
- `shareTables=True` proof — only **2 distinct glyf offsets** across all 18 faces:
  - glyf @ 368 shared by faces [0,2,4,6,8,10,12,14,16] (all 9 Regular faces ← WenKai outlines)
  - glyf @ 25848192 shared by faces [1,3,5,7,9,11,13,15,17] (all 9 Bold faces ← ZhenKai outlines)
- name tables differ per face (distinct offsets) — that's the only per-family data duplicated.
- face0 family "LXGW WenKai ZhenKai Mono GB" Regular glyf@368; face1 same family Bold glyf@25848192; face2 "LXGW WenKai" Regular glyf@368 (same physical outlines as face0).
