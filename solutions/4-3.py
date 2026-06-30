import sys
from collections import Counter
from fontTools.ttLib import TTFont

font_file = sys.argv[1]
font = TTFont(font_file)

cmap = font.getBestCmap()
print(font['hhea'].numberOfHMetrics)

hmtx = font['hmtx']

counter = Counter()
for v in hmtx.metrics.values():
    adv, lsb = v
    counter[adv] += 1

print(counter)

