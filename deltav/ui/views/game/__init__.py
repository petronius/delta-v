
from collections import OrderedDict

import numpy
import pyglet

import deltav.app
import deltav.ui
import deltav.physics.body

from pyglet.gl import *
from numpy import *


from deltav.physics.orbit import pi
from deltav.ships import MobShip, PlayerShip
from deltav.ui.keyboard import bindings as k

from deltav.gamestate import new_game_state

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
        ]),
    }

    def toggle_option(self, type_, name):
        self.player_options[type_][name] = not self.player_options[type_][name]

    def get_option(self, type_, name):
        return self.player_options[type_][name]


    def __init__(self):

        self.game_state = new_game_state() # FIXME: on_load
        self.game_state.start()

        self.ui_batch = pyglet.graphics.Batch()

        #coords = self.game_state.player.position
        self.view3d = View3D(self,
            (
             0, #5,
             0, #deltav.ui.game_window.height//2 + 5,
             deltav.ui.game_window.width, #//2 - 10,
             deltav.ui.game_window.height, #//2 -10,
            ),
            (0,0,0)
        )


        self.panels = (
            TrackingPanel,
            NavPanel,
        )

        for panel in self.panels:
            panel.load(deltav.ui.game_window, self)

        # self._focus = self.game_state.player


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

        elif key == k["SET_SPEED_1"]:
            self.game_state.set_speed(1)
        elif key == k["SET_SPEED_2"]:
            self.game_state.set_speed(2)
        elif key == k["SET_SPEED_3"]:
            self.game_state.set_speed(3)
        elif key == k["SET_SPEED_4"]:
            self.game_state.set_speed(4)
        elif key == k["SET_SPEED_5"]:
            self.game_state.set_speed(5)
        elif key == k["SET_SPEED_6"]:
            self.game_state.set_speed(6)
        elif key == k["SET_SPEED_7"]:
            self.game_state.set_speed(7)
        elif key == k["SET_SPEED_8"]:
            self.game_state.set_speed(8)
        elif key == k["SET_SPEED_9"]:
            self.game_state.set_speed(9)

        elif key == k["SPEED_PLUS"]:
            self.game_state.set_speed(multiplier=2)
        elif key == k["SPEED_MINUS"]:
            self.game_state.set_speed(multiplier=.5)

        elif key == k["SPEED_PAUSE"]:
            self.game_state.toggle_pause()

        elif key == k["CYCLE_TARGET"]:
            self.game_state.cycle_target("player")
        elif key == k["SHOOT_AT_TARGET_A"]:
            self.game_state.shoot_at_target("player", "bullet")
        elif key == k["SHOOT_AT_TARGET_T"]:
            self.game_state.shoot_at_target("player", "torpedo")

        elif key == k["QUIT"]:
            self.game_state.stop()
            deltav.app.game_app.user_quit()

        # elif key == k["ACC_PLUS"]:
        #     self.game_state.player._orbit.accelerate(50)
        # elif key == k["ACC_MINUS"]:
        #     self.game_state.player._orbit.accelerate(-50)

        # elif key == k["CYCLE_FOCUS"]:
        #     self.cycle_focus()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # FIXME: only pass if is on viewport
        self.view3d.scroll(scroll_y)

    def tick(self, dt):
        for panel in self.panels:
            try:
                panel.update(self)
            except AssertionError:
                pass # FIXME: "assert _is_loaded failing in pyglet gui code?
        # coords = self.get_focus().get_position()
        coords = (0,0,0)
        self.view3d.center_on(coords)


    # def cycle_focus(self):
    #     objs = []
    #     for k in sorted(self.game_state.scene):
    #         objs += self.game_state.scene[k]
    #     if self._focus in objs:
    #         idx = objs.index(self._focus)
    #     else:
    #         idx = -1
    #     try:
    #         self._focus = objs[idx+1]
    #     except IndexError:
    #         self._focus=objs[0]

    # def get_focus(self):
    #     if self._focus is None:
    #         self.cycle_focus()
    #     elif not self.game_state.in_scene(self._focus):
    #         self.cycle_focus()
    #     return self._focus
