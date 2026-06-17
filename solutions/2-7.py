import sys
import struct
import hexdump
import bisect

file = sys.argv[1]

tables = {}
with open(file, "rb") as f:
    file_type = f.read(4)
    # print(file_type)
    num_tables = struct.unpack(">H", f.read(2))[0]
    # print(num_tables)
    f.seek(12)
    for i in range(num_tables):
        tag = f.read(4).decode()
        _ = f.read(4)
        offset = struct.unpack(">I", f.read(4))[0]
        length = struct.unpack(">I", f.read(4))[0]
        print(f"{tag=} {offset=} {length=}")
        tables[tag] = (offset, length)
# print(tables)


def read_short(f):
    return struct.unpack(">H", f.read(2))[0]


def read_signed_short(f):
    return struct.unpack(">h", f.read(2))[0]


def read_int(f):
    return struct.unpack(">I", f.read(4))[0]


def hp(bs):
    hexdump.hexdump(bs)


def explore_cmap():
    (offset, _) = tables["cmap"]
    with open(file, "rb") as f:
        f.seek(offset)
        assert f.read(2) == b"\x00\x00"
        num_tables = read_short(f)
        cmap_tables = {}
        for _ in range(num_tables):
            platform = read_short(f)
            encoding = read_short(f)
            cmap_offset = read_int(f)
            cmap_tables[(platform, encoding)] = offset + cmap_offset
        for (p, e), o in cmap_tables.items():
            print(f"platform: {p}\tencoding: {e}\toffset(file): {o}")
        # f.seek(cmap_tables[(3, 1)])
        # print("format at (3,1):", read_short(f))   # → 4
        # f.seek(cmap_tables[(3, 10)])
        # print("format at (3,10):", read_short(f))   # → 12

        f.seek(cmap_tables[(3, 1)])
        header = f.read(14)
        total = header[2] * 256 + header[3]
        n_segs = (header[6] * 256 + header[7]) // 2
        explore_cmap_format4(n_segs, total, f)


class CmapTableF4:
    def __init__(self, start_code, end_code, id_delta, id_range_offset, glyph_id_arr):
        n = len(start_code)
        self.n = n
        self.start_code = start_code
        self.end_code = end_code
        self.id_delta = id_delta
        self.id_range_offset = id_range_offset + glyph_id_arr
        self.id_range_offset_offset = 14 + n * 2 + 2 + n * 2 + n * 2

    def lookup(self, char):
        c = ord(char)
        idx = bisect.bisect_left(self.end_code, c)
        start_code = self.start_code[idx]
        if start_code > c:
            return 0
        if self.id_range_offset[idx] == 0:
            return (c + self.id_delta[idx]) & 0xFFFF
        else:
            val = self.id_range_offset[idx]
            oidx = idx + val // 2 + (c - start_code)
            if self.id_range_offset[oidx] == 0:
                return 0
            return self.id_range_offset[oidx] + self.id_delta[idx]


def explore_cmap_format4(n_segs, total, f):
    # print(n_segs)
    # cur = f.tell()
    rem = total - 14
    end_code = [0] * n_segs
    start_code = [0] * n_segs
    id_delta = [0] * n_segs
    id_range_offset = [0] * n_segs
    for i in range(n_segs):
        end_code[i] = read_short(f)
    rem -= n_segs * 2
    _ = f.read(2)
    rem -= 2
    for i in range(n_segs):
        start_code[i] = read_short(f)
    rem -= n_segs * 2
    for i in range(n_segs):
        id_delta[i] = read_signed_short(f)
    rem -= n_segs * 2
    for i in range(n_segs):
        id_range_offset[i] = read_short(f)
    rem -= n_segs * 2
    print("# glyph_id_arr", rem // 2)
    glyph_id_arr = [0] * (rem // 2)
    for i in range(rem // 2):
        glyph_id_arr[i] = read_short(f)
    cmap_table = CmapTableF4(
        start_code, end_code, id_delta, id_range_offset, glyph_id_arr
    )
    # print(cmap_table.lookup("一"))
    # print(cmap_table.lookup("A"))
    print(cmap_table.lookup("永"))


explore_cmap()
