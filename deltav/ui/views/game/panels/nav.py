
import numpy
import os.path
import deltav.system

from deltav.physics.orbit import pi

from pyglet_gui.constants import *
from pyglet_gui.gui import Frame, Label
from pyglet_gui.manager import Manager
from pyglet_gui.buttons import Button
from pyglet_gui.containers import VerticalContainer, HorizontalContainer, GridContainer
from pyglet_gui.theme import Theme

theme = Theme({"font": "Silkscreen",
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


elements = {
  "eccentricity": (Label(""), None),
  "semi_major_axis": (Label(""), "m"),
  "inclination": (Label(""), "r"),
  "long_of_ascending_node": (Label(""), "r"),
  "argument_of_periapsis": (Label(""), "r"),
  # "mean_anomaly": (Label(""), "r"),
  # "eccentric_anomaly": (Label(""), "r"),
  "true_anomaly": (Label(""), "r"),
  "semi_latus_rectum": (Label(""), "m"),
  "period": (Label(""), "s"),
  # "time_from_periapsis": (Label(""), "s"),
}

orbital_statuses = [
  [
    Label("e"),
    elements["eccentricity"][0],
  ],
  [
    Label("α"),
    elements["semi_major_axis"][0],
  ],
  [
    Label("i"),
    elements["inclination"][0],
  ],
  [
    Label("Ω"),
    elements["long_of_ascending_node"][0],
  ],
  [
    Label("ω"),
    elements["argument_of_periapsis"][0],
  ],
  # [
  #   Label("M"),
  #   elements["mean_anomaly"][0],
  # ],
  # [
  #   Label("E/D/F"),
  #   elements["eccentric_anomaly"][0],
  # ],
  [
    Label("v"),
    elements["true_anomaly"][0],
  ],
  [
    Label("p"),
    elements["semi_latus_rectum"][0],
  ],
  [
    Label("Period"),
    elements["period"][0],
  ],
  # [
  #   Label("Time from peraipsis"),
  #   elements["time_from_periapsis"][0],
  # ],

]

manager = None

def load(window, game_view):

  orbit = game_view.get_scene_data()["player"]["orbit"]

  manager = Manager(
    VerticalContainer([

      Label("NAVIGATION"),

      GridContainer(orbital_statuses),

    ]),

    anchor = ANCHOR_BOTTOM_LEFT,
    is_movable = False,
    window = window,
    batch = game_view.ui_batch,
    theme = theme,
    offset = (20, 20)
    
  )
    
  return manager


def _format_pretty(n, u):
  if n == numpy.Inf:
    return "∞", ""
  elif n is None or numpy.isnan(n):
    return "-", ""
  elif u == "m":

    if n <= 1000:
      return round(n, 2), "m"
    elif n <= 1.5e11:
      return round(n/1000, 2), "km"
    else:
      return round(n/1.4960e11, 2), "AU"

  elif u == "r":

    res, u = round(n * (180/pi), 3), "°"

    res %= 360
    while res < 0:
      res = 360 + res

    return res, u

  elif u == "s":

    m, s = divmod(n, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d:
      return "%02d days, %02d:%02d:%02d" % (d, h, m, s), ""
    else:
      return "%02d:%02d:%02d" % (h, m, s), ""

  else:

    if u is None:
      u = ""

    return round(n, 6), u


def update(game_view):
  orbit = game_view.get_scene_data()["player"]["orbit"]
  for k, kv in elements.items():
    el, units = kv
    v = orbit[k]
    v, u = _format_pretty(v, units)
    s = "%s %s" % (v, u)
    el.set_text(s)