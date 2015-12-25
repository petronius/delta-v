
from cairocffi import *

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

xs = []
ys = []
zs = []
for i in range(1000):
    iss._orbit.step(60)
    x, y, z = iss._orbit.v_position
    xs.append(x)
    ys.append(y)
    zs.append(z)

ax.plot(xs, ys, zs)
ax.legend()
plt.show()
