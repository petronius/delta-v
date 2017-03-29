
from collections import OrderedDict
from functools import partial

import numpy
import pyglet

import deltav.app
import deltav.ui
import deltav.physics.body

from pyglet.gl import *
from numpy import *


from deltav.physics.orbit import pi
from deltav.ships import MobShip, PlayerShip
from deltav.ui.keyboard import bindings as k, check as key_check
from deltav.gameserver.util import DebugClock

from deltav.gamestate import new_game_state

from .view3d import View3D
from .panels import tracking as TrackingPanel
from .panels import nav as NavPanel

#
# FIXME: between this class and view3d, we should only get scene data once per
# tick, to reduce IPC overhead
#

class GameView(deltav.ui.views.BaseView):

    player_options = {
        "tracking": OrderedDict([
            ("labels", True),
            ("bodies", True),
            ("orbits", True),
            ("symbols", True),
        ]),
    }

    def __init__(self, client):
        self.client = client
        self.ui_clock = DebugClock()

    def load(self, window):
        self.panels = [
            OTDS(window),               # Orbital tactical data system: 3d view of current scene, visual targetting + maneuvering controls
            # FireControl(window),        # Current target + threats detailed data, programming firing patterns, etc.
            # TacNav(window),             # Tactical navigation, programming maneuvers, etc.
            # DamageControl(window),      # Our ship detailed data
            # GroundTrack(window),        # Detailed information about everything orbiting the current body, alttitude and ground info
            # ShipLogs(window),           # Combat logs
            # CommsPanel(window),         # Quests and scenario objectives
            # SystemMap(window),          # Map of current planetary system
            # LRNavControl(window),       # Long range nav control: Map of solar system, plus "loading" screen between planetary systems
        ]
        self.active_panel = None


    def on_draw(self):
        self.ui_clock.start_timer()
        self.active_panel.draw()
        self.ui_clock.record_time()

    def tick(self, dt):
        scene = self.client.get_scene_info()
        ship = self.client.get_ship_info()

        for panel in self.panels:
            panel.update(scene, ship)


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.active_panel.drag(dx, dy, buttons)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # FIXME: only pass if is on viewport
        self.active_panel.scroll(scroll_y)

    def on_key_press(self, key, modifiers):
        self.active_panel.keypress(key, modifiers)

    #     self.ui_batch = pyglet.graphics.Batch()

    #     #coords = self.game_state.player.position
    #     self.view3d = View3D(self,
    #         (
    #          0, #5,
    #          0, #deltav.ui.game_window.height//2 + 5,
    #          deltav.ui.game_window.width, #//2 - 10,
    #          deltav.ui.game_window.height, #//2 -10,
    #         ),
    #         (0,0,0)
    #     )


    #     self.panels = (
    #         TrackingPanel,
    #         NavPanel,
    #     )

    #     for panel in self.panels:
    #         panel.load(deltav.ui.game_window, self)

    #     self._focus = "player"

    #     self.single_press_keys = {
    #         "SHOW_ORBITS": partial(self.toggle_option, "tracking", "orbits"),
    #         "SHOW_LABELS": partial(self.toggle_option, "tracking", "labels"),
    #         "SHOW_SYMBOLS": partial(self.toggle_option, "tracking", "symbols"),
    #         "SHOW_BODIES": partial(self.toggle_option, "tracking", "bodies"),

    #         "SET_SPEED_1": ("set_speed", 1),
    #         "SET_SPEED_2": ("set_speed", 2),
    #         "SET_SPEED_3": ("set_speed", 3),
    #         "SET_SPEED_4": ("set_speed", 4),
    #         "SET_SPEED_5": ("set_speed", 5),
    #         "SET_SPEED_6": ("set_speed", 6),
    #         "SET_SPEED_7": ("set_speed", 7),
    #         "SET_SPEED_8": ("set_speed", 8),
    #         "SET_SPEED_9": ("set_speed", 9),

    #         "SPEED_PAUSE": ("toggle_pause",),

    #         "CYCLE_TARGET": ("cycle_target", "player"),
    #         "SHOOT_AT_TARGET_A": ("shoot_at_target", "player", "bullet"),
    #         "SHOOT_AT_TARGET_T": ("shoot_at_target", "player", "torpedo"),
    #         # Fixme: these should probably be in UI methods, not lambdas
    #         "QUIT": partial(self.request_quit),
    #         "CYCLE_FOCUS": partial(self.cycle_focus, reset=True),
    #     }
    #     self.press_and_hold_keys = {

    #         "SPEED_PLUS": ("set_speed", {"multiplier": 2}),
    #         "SPEED_MINUS": ("set_speed", {"multiplier": .5}),

    #         "ACC_PLUS": ("player_accelerate", 50),
    #         "ACC_MINUS": ("player_accelerate", -50),

    #         "PITCH_DOWN": ("player_turn", {"x": -1}),
    #         "PITCH_UP": ("player_turn", {"x": 1}),

    #         "YAW_LEFT": ("player_turn", {"y": -1}),
    #         "YAW_RIGHT": ("player_turn", {"y": 1}),
    #         "ROLL_LEFT": ("player_turn", {"z": -1}),
    #         "ROLL_RIGHT": ("player_turn", {"z": 1}),
    #     }

    #     self.ui_clock = DebugClock()

    # def toggle_option(self, type_, name):
    #     self.player_options[type_][name] = not self.player_options[type_][name]

    # def get_option(self, type_, name):
    #     return self.player_options[type_][name]


    # def request_quit(self):
    #     self.game_state.stop()
    #     deltav.app.game_app.user_quit()

    # def load(self):
    #     pass

    # def destroy(self):
    #     pass

    # def on_draw(self):
    #     self.ui_clock.start_timer()
    #     data = self.get_focus()
    #     self.view3d.center_on(data["position"])
    #     self.view3d.render(self)
    #     self.ui_batch.draw()
    #     self.ui_clock.record_time()

    # def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
    #     # FIXME: only pass if is on viewport
    #     self.view3d.drag(dx, dy, buttons)

    # def on_key_press(self, key, modifiers):
    #     for key_, action in self.single_press_keys.items():
    #         if key == k[key_]:
    #             if callable(action):
    #                 action()
    #             else:
    #                 self.waiting_cmds.append(action)
    #             break

    # def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
    #     # FIXME: only pass if is on viewport
    #     self.view3d.scroll(scroll_y)

    # def tick(self, dt):
    #     # Only do this once per tick
    #     for key, action in self.press_and_hold_keys.items():
    #         if key_check(key):
    #             if callable(action):
    #                 action()
    #             else:
    #                 self.waiting_cmds.append(action)

    #     for panel in self.panels:
    #         try:
    #             panel.update(self)
    #         except AssertionError:
    #             pass # FIXME: "assert _is_loaded failing in pyglet gui code?
    #     # Reset this cache per tick
    #     self.scene_data = None
    #     # send all commands from this UI tick at once
    #     self.game_state.exec_cmdlist(self.waiting_cmds)
    #     self.waiting_cmds = []

    # def reset_view(self):
    #     data = self.get_focus()
    #     self.view3d.center_on(data["position"], True)


    # def cycle_focus(self, reset=False):
    #     objs = []
    #     scene_data = self.get_scene_data()["objects"]
    #     for k in sorted(scene_data.keys()):
    #         objs += scene_data[k]
    #     if self._focus in objs:
    #         idx = objs.index(self._focus)
    #     else:
    #         idx = -1
    #     try:
    #         self._focus = objs[idx+1]
    #     except IndexError:
    #         self._focus = objs[0]
    #     if reset:
    #         self.reset_view()

    # def get_focus(self):
    #     if self._focus is None:
    #         self.cycle_focus()

    #     scene_data = self.get_scene_data()["objects"]
    #     objs = []
    #     for k in sorted(scene_data.keys()):
    #         objs += scene_data[k]

    #     if not self._focus in objs:
    #         self.cycle_focus()

    #     for k, l in scene_data.items():
    #         for uuid, data in l.items():
    #             if uuid == self._focus:
    #                 return data


    # def get_scene_data(self):
    #     if not self.scene_data:
    #         self.scene_data = self.game_state.get_scene_data()
    #     return self.scene_data
