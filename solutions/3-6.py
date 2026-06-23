import sys
import matplotlib.pyplot as plt
from fontTools.ttLib import TTFont

ttf = TTFont(sys.argv[1])
cmap = ttf.getBestCmap()
assert cmap is not None

ten = cmap[ord('十')]
t = ttf['glyf'][ten]

# print(t.coordinates)
# print(t.flags)


fig, ax = plt.subplots()
ax.set_xlim(0, 1000)
ax.set_ylim(-100, 1000)
ax.set_aspect("equal")

prev_is_zero = False

colors = ['gray', 'black']
idx = 1
for (coord, flag) in zip(t.coordinates, t.flags):
    ax.scatter(coord[0], coord[1], color=colors[flag], s=3)
    ax.annotate(str(idx), (coord[0], coord[1]), fontsize=4)
    idx += 1
    prev_is_zero = flag == 0

xs = [p[0] for p in t.coordinates]
ys = [p[1] for p in t.coordinates]
ax.plot(xs, ys, color='green', linewidth=1, zorder=1)

print(t.coordinates)
plt.show()
