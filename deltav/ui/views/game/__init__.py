
import numpy
import pyglet

import deltav.ui
import deltav.physics.body
import deltav.ships

from pyglet.gl import *
from pyglet.window import key
from numpy import *

from deltav.physics.orbit import pi

from .camera import Camera

class GameView(deltav.ui.views.BaseView):

    # Scale factor for the game view, in meters
    scale = 60000000

    def _convert(self, x, y = 0, z = 0):
        """
        Convert physics coordinates to render coordinates.
        """
        x = x * self.scale
        y = y * self.scale
        z = z * self.scale
        return x, y, z

    def _convert_screen(self, x, y, z = 0):
        """
        Convert render coordinates to flat screen coordinates
        """
        x += self.width/2
        y = self.height/2 - y
        return tuple(map(int, (x, y, 0)))


    def __init__(self):
        self.width = deltav.ui.game_window.width
        self.height = deltav.ui.game_window.height

        self.scale = self.width/self.scale

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

        self.camera = Camera(
            deltav.ui.game_window.width,
            deltav.ui.game_window.height,
        )


    def draw_planet(self, planet, pts=30, color=(255,0,0)):

        r = planet.radius * self.scale

        self.camera.draw_sphere((0,0,0), r, color)


    def draw_ship(self, ship, orbit_color=(0,0,255), ship_color=(0,0,255)):

        orbit = [self._convert(*p) for p in ship._orbit.get_plot(60)]
        self.camera.draw_loop(orbit, orbit_color)

        coords = self._convert(*ship.position)

        self.camera.text(ship._name, coords)
        self.camera.draw_symbol(coords, ship_color)


    def load(self):
        pass

    def destroy(self):
        pass

    def on_draw(self):
        self.camera.apply()

        for ship in self.ships:
            self.draw_ship(ship)

        self.draw_planet(self.planet)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.camera.drag(x, y, dx, dy, buttons, modifiers)
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def on_key_press(self, k, modifiers):
        self.camera.key(k, modifiers)

        print(k)

        if k == key.NUM_8:
            self.ships[0].accelerate((0, 0, 10))
        if k == key.NUM_2:
            self.ships[0].accelerate((0, 0, -10))
        if k == key.NUM_4:
            self.ships[0].accelerate((-10, 0, 0))
        if k == key.NUM_6:
            self.ships[0].accelerate((10, 0, 0))
        if k == key.NUM_5:
            self.ships[0].accelerate((0, 10, 0))
        if k == key.NUM_0:
            self.ships[0].accelerate((0, -10, 0))

        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.camera.scroll(scroll_y)

    def tick(self):
        for ship in self.ships:
            ship._orbit.step(10)
