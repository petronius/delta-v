"""
Dirty visualisation glue code
"""

import numpy
import pyglet
import time

from ships import PlayerShip, MobShip

class Body(object):
    def __init__(self, mass, radius):
        self.mass = mass
        self.radius = radius

counter = 0

# Rough and ready for testing
# class Window(pyglet.window.Window):

#     c = False

#     def _convert(self, ship):
#         global counter
#         x, y, z = ship._orbit.v_position
#         print(counter, x, y)

#         bounds = 160000000

#         scale = self.width/bounds

#         x *= scale
#         y *= scale


#         # recenter
#         x += self.width/2
#         y = self.height/2 - y
        
#         return int(x), int(y)


#     def on_draw(self):
#         global ships, counter

#         if not self.c:
#             self.clear()
#             self.c = True

#         for ship in ships:
#             coords = self._convert(ship)
#             if coords[0] > 0 and coords[0] < self.width and \
#                coords[1] > 0 and coords[1] < self.height:
#                 pass
#             else:
#                 continue

#             a = (coords[0], coords[1]+5)
#             b = (coords[0]+5, coords[1])
#             c = (coords[0]-5, coords[1])
#             pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
#                 ('v2i', a + b + c),
#                 ('c3B', (255,255,255)*3),
#             )
#             #pyglet.text.Label(str(counter), font_size=10, x = coords[0] + 10, y = coords[1] + 10, anchor_x = "left", anchor_y = "top").draw()
#             counter += 1


#         pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
#             ('v2i', tuple(map(int, (self.width/2+5, self.height/2,
#                      self.width/2-5, self.height/2,
#                      self.width/2, self.height/2+5)))),
#             ('c3B', (0,255,255)*3),
#         )

# def update(dt):
#     global counter
#     for ship in ships:
#         ship._orbit.step(560)
#         time.sleep(.01)

import copy

from numpy import float128, radians

if __name__ == "__main__":
    earth = Body(float128("5.972e24"), 6371000) # kg, m

    iss = PlayerShip("ISS")
    iss.mass = 419600 # kg

    # Horizons ephemerides, in km and km/s, multiplied out to meters
    # 2457380.183935185 = A.D. 2015-Dec-23 16:24:52.0000 (TDB)

    # pyglet.clock.schedule_interval(update, 1/24.0)

    v_position = numpy.array([
        float128("-9.389136074764635E+02") * 1000,
        float128("-5.116319908091118E+03") * 1000,
        float128( "4.342059664304661E+03") * 1000,
    ], dtype="float128")

    v_velocity = numpy.array([
        float128("6.628784989010491E+00") * 1000,
        float128("1.718224103100249E+00") * 1000,
        float128("3.457710395445335E+00") * 1000,
    ], dtype="float128")

    # Test
    test_values = {
        "eccentricity": float128("3.743276399381678E-04"),
        "argument_of_periapsis": radians(float128("5.857936559219403E+01")),
        "inclination": radians(float128("5.157910786454486E+01")),
        "mean_anomaly": radians(float128("3.563009472454253E+02")),
        "true_anomaly": radians(float128("3.562981785606661E+02")),
        "semi_major_axis": float128("6.778354516341115E+03") * 1000,
        "long_of_asc_node": radians(float128("2.181413903120838E+02")),
    }


    iss.orbit(earth, v_position, v_velocity)

    print(iss._orbit)

    args = copy.deepcopy(test_values)
    args.pop("true_anomaly", "")
    args["gravitational_parameter"] = iss._orbit.gravitational_parameter
    reversed = iss._orbit.reverse(**args)

    for k, v in test_values.items():
        rv = getattr(iss._orbit, k)
        if rv != v:
            print(k, ":")
            print(" ", v)
            print(" ", rv)
    print("reversed:")
    print(" ",v_position)
    print(" ", reversed[0])
    print("--")
    print(" ",v_velocity)
    print(" ", reversed[1])

    # # win = Window(width=800,height=800)
    # # pyglet.app.run()


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
