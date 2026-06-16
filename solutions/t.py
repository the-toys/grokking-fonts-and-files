import sys
import struct

file = sys.argv[1]

tables = {}
with open(file, 'rb') as f:
    file_type = f.read(4)
    print(file_type)
    num_tables = struct.unpack(">H", f.read(2))[0]
    print(num_tables)
    f.seek(12)
    for i in range(num_tables):
        tag = f.read(4).decode()
        _ = f.read(4)
        offset = struct.unpack(">I", f.read(4))[0]
        length = struct.unpack(">I", f.read(4))[0]
        print(f'{tag=} {offset=} {length=}')
        tables[tag] = (offset, length)
# print(tables)


def explore_cmap():
    (offset, length) = tables['cmap']
    with open(file, 'rb') as f:
        f.seek(offset)
        print(f.read(20))



explore_cmap()

