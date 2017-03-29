
import os.path
import deltav.system

from pyglet_gui.constants import *
from pyglet_gui.gui import Frame, Label
from pyglet_gui.manager import Manager
from pyglet_gui.buttons import Button
from pyglet_gui.containers import VerticalContainer, HorizontalContainer, GridContainer
from pyglet_gui.theme import Theme

from pyglet_gui.controllers import TwoStateController

theme = Theme({"font": "Droid Sans Mono",
               "font_size": 12,
               "text_color": [255, 255, 255, 255],
               "gui_color": [255, 0, 0, 255],
               "button": {
                   "down": {
                       "image": {
                           "source": "button-down.png",
                           "frame": [8, 6, 2, 2],
                           "padding": [18, 18, 8, 6]
                       },
                       "text_color": [0, 0, 0, 255]
                   },
                   "up": {
                       "image": {
                           "source": "button.png",
                           "frame": [6, 5, 6, 3],
                           "padding": [18, 18, 8, 6]
                       }
                   }
               }
              }, resources_path=os.path.join(deltav.system.DIR_ASSETS, "ui-theme"))


class OptionButton(Button):

    def __init__(self, type_, name, game_view):
        self.type_ = type_
        self.name = name
        self.game_view = game_view
        state = self.game_view.get_option(self.type_, self.name)
        super(OptionButton, self).__init__(name.upper(), state, self.callback)

    def callback(self, val):
        self.game_view.toggle_option(self.type_, self.name)

    def update_view(self):
        self._is_pressed = self.game_view.get_option(self.type_, self.name)
        # do part of the work of the default change_state() method
        self.reload()
        self.reset_size()

buttons = []

def load(window, game_view):

    global buttons
    for option, state in game_view.player_options["tracking"].items():
        buttons.append(OptionButton("tracking", option, game_view))

    manager = Manager(
        VerticalContainer([

            # HorizontalContainer([
            #   VerticalContainer([
            #     Label("Module 1"), 
            #     Button("(1,2)"),
            #   ]),
            #   VerticalContainer([
            #     Label("Module 2"), 
            #     Button("(2,2)"),
            #   ]),
            # ]),
            Label("TRACKING DISPLAY"),

            GridContainer([[button] for button in buttons]),
        ]),

        anchor = ANCHOR_TOP_RIGHT,
        is_movable = False,
        window = window,
        batch = game_view.ui_batch,
        theme = theme,
        offset = (-10, 20)

    )

    return manager


def update(game_view):
    global buttons
    # get the player display options and update the panel to reflect the
    # current state
    for button in buttons:
        button.update_view()