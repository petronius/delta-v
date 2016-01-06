"""
Dirty visualisation glue code
"""

import pyglet

import deltav.app
import deltav.assetloader
import deltav.ui

from deltav.ui.views.game import GameView

if __name__ == "__main__":

    deltav.assetloader.load_fonts()

    deltav.app.init()
    deltav.ui.init()

    deltav.ui.game_window.set_view(GameView())
    pyglet.clock.schedule(deltav.ui.game_window.tick)

    deltav.app.game_app.run()