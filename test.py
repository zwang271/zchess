import math
import numpy as np

# M = [[None for _ in range(8)] for _ in range(8)]
# for i in range(64):
#     x, y = (i % 8, i // 8)
#     M[y][x] = int(100*(math.sin(math.pi/8 * i) + 100*math.sin(math.pi/16 * i)))

# for r in M:
#     print(r)

Ma = np.load("./weights/Ma.npy")
Mb = np.load("./weights/Mb.npy")
print(Ma, "\n", Mb)


