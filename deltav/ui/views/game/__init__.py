
import numpy
import pyglet

import deltav.ui
import deltav.physics.body
import deltav.ships

from pyglet.gl import *

from deltav.physics.orbit import pi

class GameView(deltav.ui.views.BaseView):

    # Scale factor for the game view, in meters
    scale = 60000000

    def _convert(self, x, y = 0, z = 0):
        """
        Convert physics coordinates to screen coordinates.
        """
        width = deltav.ui.game_window.width
        height = deltav.ui.game_window.height
        scale = width/self.scale
        x = x * scale + width/2
        y = height/2 - y * scale
        return x, y, z

    def __init__(self):
        shuttle, station = (
            deltav.ships.PlayerShip("OV-103 Discovery"),
            deltav.ships.MobShip("ISS"),
        )

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

        self.planet = deltav.physics.body.Body(5.972e24, 6371000) 

        station.orbit(self.planet, v_position, v_velocity)
        shuttle.orbit(self.planet, tuple(map(lambda x : x*1.3, v_position)), tuple(map(lambda x : x, v_velocity)))

        self.ships = (shuttle, station,)


    def draw_planet(self, planet, pts=30, color=(255,0,0)):

        verts = ()
        for i in range(pts):
            angle = float(i)/pts * 2 * pi
            x = planet.radius * numpy.cos(angle)
            y = planet.radius * numpy.sin(angle)
            verts += self._convert(x, y)[:2]

        pyglet.graphics.draw(pts, pyglet.gl.GL_LINE_LOOP,
            ("v2f", verts),
            ("c3B", color*pts),
        )

    def draw_triangle(self, offset, color, x, y, z):

            a = (x, y+offset)
            b = (x+offset, y)
            c = (x-offset, y)
            pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
                ('v2f', a + b + c),
                ('c3B', color*3),
            )

    def draw_ship(self, ship, orbit_color=(0,0,255), ship_color=(0,0,255)):

        # draw orbit        
        points = ()
        for pt in ship._orbit.get_plot(30):
            x, y, z = self._convert(*pt)
            points += (x, y)

        pyglet.graphics.draw(30, pyglet.gl.GL_LINE_LOOP,
            ("v2f", points),
            ("c3B", orbit_color*30),
        )

        # draw ship
        self.draw_triangle(5, ship_color, x, y, z)
        pyglet.text.Label(ship._name, font_size=10, x = x + 10, y = y, anchor_x = "left", anchor_y = "top").draw()



    def load(self):
        pass

    def destroy(self):
        pass

    def on_draw(self):
        #self.camera.apply()

        # glEnable(GL_DEPTH_TEST)

        for ship in self.ships:
            self.draw_ship(ship)

        self.draw_planet(self.planet)

        # glDisable(GL_DEPTH_TEST)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        #self.camera.drag(x, y, dx, dy, buttons, modifiers)
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def on_key_press(self, key, modifiers):
        #self.camera.key(key, modifiers)
        pass

    def tick(self):
        for ship in self.ships:
            ship._orbit.step(1)
