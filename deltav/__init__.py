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
class Window(pyglet.window.Window):

    c = False

    def _convert(self, ship):
        global counter
        x, y, z = ship._orbit.v_position
        #print(counter, x, y)

        bounds = 20000000

        scale = self.width/bounds

        x *= scale
        y *= scale

        # recenter
        x += self.width/2
        y += self.height/2

        return int(x), int(y)


    def on_draw(self):
        global ships, counter

        if not self.c:
            self.clear()
            self.c = True

        for ship in ships:
            coords = self._convert(ship)
            if coords[0] > 0 and coords[0] < self.width and \
               coords[1] > 0 and coords[1] < self.height:
                pass
            else:
                continue

            a = (coords[0], coords[1]+5)
            b = (coords[0]+5, coords[1])
            c = (coords[0]-5, coords[1])
            pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
                ('v2i', a + b + c),
                ('c3B', (255,255,255)*3),
            )
            #pyglet.text.Label(str(counter), font_size=10, x = coords[0] + 10, y = coords[1] + 10, anchor_x = "left", anchor_y = "top").draw()
            counter += 1


        pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
            ('v2i', tuple(map(int, (self.width/2+5, self.height/2,
                     self.width/2-5, self.height/2,
                     self.width/2, self.height/2+5)))),
            ('c3B', (0,255,255)*3),
        )

def update(dt):
    global counter
    for ship in ships:
        ship._orbit.step(60)
        time.sleep(.1)




if __name__ == "__main__":
    earth = Body(5.972e24, 6371000) # kg, m

    ship1 = PlayerShip("NASA OV-103 Discovery")
    ship1.mass = 234824.2 # kg

    ship1.orbit(earth, numpy.array([1498.0751313466 * 1000, 3946.0670245861 * 1000, 5110.4330569027 * 1000], dtype="float64"), # m
        numpy.array([-6.1929127574 * 1000, -2.4942114793 * 1000, 3.741321742 * 1000], dtype="float64")) # m/s
    ships = (ship1,) #ship2, ship3)

    pyglet.clock.schedule_interval(update, 1/24.0)

    win = Window(width=800,height=800)
    pyglet.app.run()