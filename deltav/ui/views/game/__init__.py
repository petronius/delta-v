
from collections import OrderedDict

import numpy
import pyglet

import deltav.ui
import deltav.physics.body

from pyglet.gl import *
from numpy import *

from deltav.physics.orbit import pi
from deltav.ships import MobShip, PlayerShip
from deltav.ui.keyboard import bindings as k

from deltav.gamestate import GameState

from .view3d import View3D
from .panels import tracking as TrackingPanel
from .panels import nav as NavPanel

class GameView(deltav.ui.views.BaseView):

    player_options = {
        "tracking": OrderedDict([
            ("labels", True),
            ("bodies", True),
            ("orbits", True),
            ("symbols", True),
        ])
    }

    def toggle_option(self, type_, name):
        self.player_options[type_][name] = not self.player_options[type_][name]

    def get_option(self, type_, name):
        return self.player_options[type_][name]


    def __init__(self):

        self.game_state = GameState() # FIXME: on_load

        self.ui_batch = pyglet.graphics.Batch()

        coords = self.game_state.player.position
        self.view3d = View3D(self,
            (
             0, #5,
             0, #deltav.ui.game_window.height//2 + 5,
             deltav.ui.game_window.width, #//2 - 10,
             deltav.ui.game_window.height, #//2 -10,
            ),
            coords
        )


        self.panels = (
            TrackingPanel,
            NavPanel,
        )

        for panel in self.panels:
            panel.load(deltav.ui.game_window, self)


    def load(self):
        pass

    def destroy(self):
        pass

    def on_draw(self):
        self.view3d.render(self)
        self.ui_batch.draw()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        # FIXME: only pass if is on viewport
        self.view3d.drag(dx, dy, buttons)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def on_key_press(self, key, modifiers):
        if key == k["SHOW_ORBITS"]:
            self.toggle_option("tracking", "orbits")
        elif key == k["SHOW_LABELS"]:
            self.toggle_option("tracking", "labels")
        elif key == k["SHOW_SYMBOLS"]:
            self.toggle_option("tracking", "symbols")
        elif key == k["SHOW_BODIES"]:
            self.toggle_option("tracking", "bodies")

        elif key == k["SPEED_PLUS"]:
            self.game_state.set_speed(1)
        elif key == k["SPEED_MINUS"]:
            self.game_state.set_speed(-1)
        elif key == k["SPEED_PAUSE"]:
            self.game_state.toggle_pause()

        elif key == k["ACC_PLUS"]:
            self.game_state.player._orbit.accelerate(50)
        elif key == k["ACC_MINUS"]:
            self.game_state.player._orbit.accelerate(-50)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # FIXME: only pass if is on viewport
        self.view3d.scroll(scroll_y)

    def tick(self):
        self.game_state.tick()
        for panel in self.panels:
            panel.update(self)
        coords = self.game_state.player.position
        self.view3d.center_on(coords)
