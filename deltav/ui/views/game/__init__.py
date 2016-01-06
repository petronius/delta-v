
import numpy
import pyglet

import deltav.ui
import deltav.physics.body

from pyglet.gl import *
from numpy import *

from deltav.physics.orbit import pi
from deltav.ships import MobShip, PlayerShip
from deltav.ui.keyboard import bindings as k

from .view3d import View3D
from .panels import status as StatusPanel
from .panels import nav as NavPanel

class GameView(deltav.ui.views.BaseView):

    def __init__(self):

        self.ui_batch = pyglet.graphics.Batch()

        self.speed = 1

        planet = deltav.physics.body.Body(5.972e24, 6371000) 

        self.player = PlayerShip('SASE C-3402 <font face="Droid Sans Fallback">黄河</font> Yellow River')
        self.player.orbit(planet, (
            9.01e3 * 1000,
            0,
            -2e03 * 1000,
        ), (
            4.628784989010491E+00 * 1000,
            4.718224103100249E+00 * 1000,
            4.457710395445335E+00 * 1000,
        ))

        shuttle, station = (
            MobShip("OV-103 Discovery"),
            MobShip("ISS"),
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

        station.orbit(planet, v_position, v_velocity)
        shuttle.orbit(planet, tuple(map(lambda x : x*1.3, v_position)), tuple(map(lambda x : x, v_velocity)))

        ships = (shuttle, station, self.player)

        self.scene = {
            "ships": ships,
            "bodies": (planet,),
        }

        self.view3d = View3D(self,
            (
             5,
             deltav.ui.game_window.height//2 + 5,
             deltav.ui.game_window.width//2 - 10,
             deltav.ui.game_window.height//2 -10,
            )
        )

        self.panels = (
            StatusPanel,
            NavPanel,
        )

        for panel in self.panels:
            panel.load(deltav.ui.game_window, self.ui_batch, self.player)


    def load(self):
        pass

    def destroy(self):
        pass

    def on_draw(self):
        self.view3d.render(self.scene)
        self.ui_batch.draw()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        # FIXME: only pass if is on viewport
        self.view3d.drag(dx, dy, buttons)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def on_key_press(self, key, modifiers):
        if key == k["SHOW_ORBITS"]:
            self.view3d.show("ORBITS")
        elif key == k["SHOW_LABELS"]:
            self.view3d.show("LABELS")
        elif key == k["SHOW_SYMBOLS"]:
            self.view3d.show("SYMBOLS")
        elif key == k["SHOW_BODIES"]:
            self.view3d.show("BODIES")

        elif key == k["SPEED_1"]:
            self.speed = 1
        elif key == k["SPEED_2"]:
            self.speed = 2
        elif key == k["SPEED_3"]:
            self.speed = 3
        elif key == k["SPEED_4"]:
            self.speed = 4
        elif key == k["SPEED_5"]:
            self.speed = 5
        elif key == k["SPEED_6"]:
            self.speed = 6
        elif key == k["SPEED_7"]:
            self.speed = 7
        elif key == k["SPEED_8"]:
            self.speed = 8
        elif key == k["SPEED_9"]:
            self.speed = 9

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # FIXME: only pass if is on viewport
        self.view3d.scroll(scroll_y)

    def tick(self):
        for ship in self.scene.get("ships", ()):
            ship._orbit.step(2**self.speed)
        for panel in self.panels:
            panel.update()
        self.view3d.center_on(self.player.position)
