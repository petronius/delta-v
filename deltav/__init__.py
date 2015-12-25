"""
Dirty visualisation glue code
"""

import numpy
import pyglet
import time

from numpy import radians, pi

from deltav.ships import PlayerShip, MobShip

class Body(object):
    def __init__(self, mass, radius):
        self.mass = mass
        self.radius = radius

counter = 0

# Rough and ready for testing
class Window(pyglet.window.Window):

    scale = 60000000 # how wide the window is, in m


    def _convert(self, x, y, z):
        # no z yet
        global counter

        scale = self.width/self.scale

        x *= scale
        y *= scale


        # recenter
        x += self.width/2
        y = self.height/2 - y
        
        return int(x), int(y), 0

    def draw_triangle(self, offset, color, x, y, z):

            a = (x, y+offset)
            b = (x+offset, y)
            c = (x-offset, y)
            pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
                ('v2i', a + b + c),
                ('c3B', color*3),
            )

    def draw_orbit(self, orbit, pts=50, color=(0, 0, 255)):

        points = ()
        for pt in orbit.get_plot(pts):
            x, y, z = self._convert(*pt)
            points += (x, y)

        pyglet.graphics.draw(pts, pyglet.gl.GL_LINE_LOOP,
            ("v2i", points),
            ("c3B", color*pts),
        )


    def draw_planet(self, planet, pts=30, color=(255,0,0)):

        scale = self.width/self.scale
        r = planet.radius
        r = r * scale

        verts = ()
        for i in range(pts):
            angle = float(i)/pts * 2 * pi

            x = r * numpy.cos(angle) + self.width//2
            y = r * numpy.sin(angle) + self.height//2

            verts += (x, y)

        pyglet.graphics.draw(pts, pyglet.gl.GL_LINE_LOOP,
            ("v2f", verts),
            ("c3B", color*pts),
        )



    def on_draw(self):
        global ships, counter, earth

        self.clear()

        for ship in ships:
            coords = self._convert(*ship.position)

            self.draw_orbit(ship._orbit)
            self.draw_triangle(5, (255,255,255), *coords)
            pyglet.text.Label(ship._name, font_size=10, x = coords[0] + 10, y = coords[1] + 10, anchor_x = "left", anchor_y = "top").draw()

            counter += 1

        self.draw_planet(earth)

def update(dt):
    global counter
    for ship in ships:
        ship._orbit.step(60)

if __name__ == "__main__":

    pyglet.clock.schedule_interval(update, 1/24.0)

    earth = Body(5.972e24, 6371000) # kg, m

    iss = PlayerShip("ISS")
    iss.mass = 419600 # kg

    ssh = PlayerShip("OV-103 Discovery")
    ssh.mass = 90000

    # Horizons ephemerides, in km and km/s, multiplied out to meters
    # 2457380.183935185 = A.D. 2015-Dec-23 16:24:52.0000 (TDB)

    v_position = (
        -9.389136074764635E+02 * 1000,
        -5.116319908091118E+03 * 1000,
        4.342059664304661E+03 * 1000,
    )

    v_velocity = (
        6.628784989010491E+00 * 1000,
        1.718224103100249E+00 * 1000,
        3.457710395445335E+00 * 1000,
    )

    iss.orbit(earth, v_position, v_velocity)
    ssh.orbit(earth, tuple(map(lambda x : x*2, v_position)), tuple(map(lambda x : x*8, v_velocity)))

    ships = (iss,ssh,)

    print(ssh._orbit)

    win = Window(width=800,height=800)
    pyglet.app.run()

