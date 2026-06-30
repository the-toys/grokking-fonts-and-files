from functools import reduce
import sys
import struct
from fontTools.ttLib import TTFont

font_file = sys.argv[1]
font = TTFont(font_file)
cmap = font.getBestCmap()
assert cmap

char = "颜"

name = cmap[ord(char)]
glyph_id = font.getGlyphID(name)

loca = font["loca"]
g = font["glyf"][name]

bytes_start = loca[glyph_id]
bytes_end = loca[glyph_id + 1]
sz = bytes_end - bytes_start

glyf_start = 592352
with open(font_file, "rb") as f:
    f.seek(glyf_start + bytes_start)
    bs = f.read(sz)


def parse_short(bs):
    return struct.unpack(">H", bs)[0]


def parse_signed_short(bs):
    return struct.unpack(">h", bs)[0]


def parse(bs):
    number_of_contours = parse_signed_short(bs[:2])
    if number_of_contours == -1:
        raise NotImplementedError
    bs = bs[10:]
    total_pts = 0
    for _ in range(number_of_contours):
        idx = parse_short(bs[:2])
        bs = bs[2:]
        total_pts = idx + 1

    instruction_len = parse_short(bs[:2])
    bs = bs[2:]
    if instruction_len > 0:
        bs = bs[instruction_len:]

    flags, consumed = parse_flags(bs, total_pts)
    coords = parse_coords(flags, bs[consumed:])
    return coords


class Flag:
    on_curve: bool
    x_short: bool
    y_short: bool
    repeat: bool
    x_same_or_sign: bool
    y_same_or_sign: bool

    def __init__(
        self, on_curve, x_short, y_short, repeat, x_same_or_sign, y_same_or_sign
    ):
        self.on_curve = on_curve
        self.x_short = x_short
        self.y_short = y_short
        self.repeat = repeat
        self.x_same_or_sign = x_same_or_sign
        self.y_same_or_sign = y_same_or_sign

    def __repr__(self):
        return f'ON_CURVE={self.on_curve}'


def parse_flags(bs, total_pts):
    flags = []
    idx = 0
    while total_pts > 0:
        b = bs[idx]
        idx += 1
        on_curve = (b & (1 << 0)) > 0
        x_short = (b & (1 << 1)) > 0
        y_short = (b & (1 << 2)) > 0
        repeat = (b & (1 << 3)) > 0
        x_same_or_sign = (b & (1 << 4)) > 0
        y_same_or_sign = (b & (1 << 5)) > 0

        flags.append(
            Flag(
                on_curve=on_curve,
                x_short=x_short,
                y_short=y_short,
                repeat=repeat,
                x_same_or_sign=x_same_or_sign,
                y_same_or_sign=y_same_or_sign,
            )
        )
        total_pts -= 1
        if repeat:
            next_cnt = bs[idx]
            idx += 1
            for _ in range(next_cnt):
                flags.append(flags[-1])
            total_pts -= next_cnt

    return flags, idx


def parse_coords(flags, bs):
    x_diffs = []
    y_diffs = []
    print(len(flags), len(bs))
    # parse x
    for f in flags:
        if f.x_short and f.x_same_or_sign:
            x_diffs.append(bs[0])
            bs = bs[1:]
        elif f.x_short and not f.x_same_or_sign:
            x_diffs.append(-bs[0])
            bs = bs[1:]
        elif not f.x_short and f.x_same_or_sign:
            x_diffs.append(0)
        else:
            x_diffs.append(parse_signed_short(bs[:2]))
            bs = bs[2:]
    # parse y
    for f in flags:
        if f.y_short and f.y_same_or_sign:
            y_diffs.append(bs[0])
            bs = bs[1:]
        elif f.y_short and not f.y_same_or_sign:
            y_diffs.append(-bs[0])
            bs = bs[1:]
        elif not f.y_short and f.y_same_or_sign:
            y_diffs.append(0)
        else:
            y_diffs.append(parse_signed_short(bs[:2]))
            bs = bs[2:]
    s = 0
    xs = []
    ys = []
    for xdiff in x_diffs:
        s += xdiff
        xs.append(s)
    s = 0
    for ydiff in y_diffs:
        s += ydiff
        ys.append(s)
    return list(zip(xs, ys))


coords = parse(bs)
print(coords)
print(g.coordinates)
