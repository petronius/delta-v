
import os.path
import deltav.system

from pyglet_gui.constants import *
from pyglet_gui.gui import Frame, Label
from pyglet_gui.manager import Manager
from pyglet_gui.buttons import Button
from pyglet_gui.containers import VerticalContainer, HorizontalContainer, GridContainer
from pyglet_gui.theme import Theme

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

manager = None
ship_modules = None
loaded = False

def load(window, game_view):

  global manager, modules
  ship_modules = player.modules

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
      Label("SYSTEMS STATUS"),

      GridContainer([
          [
            Button("PWR"),
            Label(ship_modules["powersrc"].NAME), 
          ],
          [
            Button("CMP"),
            Label(ship_modules["computer"].NAME), 
          ],
          [
            Button("SHD"),
            Label(ship_modules["shielding"].NAME), 
          ],
          [
            Button("PRP"),
            Label(ship_modules["engines"].NAME), 
          ],
          [
            Button("SNS"),
            Label(ship_modules["sensors"].NAME), 
          ],
          [
            Button("WEP"),
            Label(ship_modules["weapons"].NAME), 
          ],
      ]),

    ]),

    anchor = ANCHOR_TOP_RIGHT,
    is_movable = False,
    window = window,
    batch = game_view.ui_batch,
    theme = theme,
    offset = (-10, 20)

  )
  loaded = True
  return manager


def update():
  pass
