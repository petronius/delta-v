"""
A module for simplifying control binding and keyboard lookups
"""

import deltav.ui

from pyglet.window import key

# A dictionary that maps action names to a list of acceptable key presses for
# that action.
bindings = {

    "SPEED_PLUS": key.F,
    "SPEED_MINUS": key.S,
    "SPEED_PAUSE": key.SPACE,

    "SHOW_SYMBOLS": key.F4,
    "SHOW_ORBITS": key.F3,
    "SHOW_BODIES": key.F2,
    "SHOW_LABELS": key.F1,

    "ACC_PLUS": key.NUM_ADD,
    "ACC_MINUS": key.NUM_SUBTRACT,
    
}

def check(binding):
    """
    Check *binding* to see if it is being pressed at the moment. The value of
    *binding* should be one of the keys in :data:`bindings`.
    """
    possible_keys = bindings.get(binding)
    for keyset in possible_keys:
        try:
            sym, mods = keyset
        except TypeError:
            sym = keyset
            mods = 0
        allk = [sym,]
        # TODO: the modifiers code isn't working properly
        mods = key.modifiers_string(mods)
        for m in filter(None, mods.split('|')):
            allk.append(getattr(key, m))
        pressedk = filter(lambda x: deltav.ui.game_window.keyboard[x], allk)
        return pressedk == allk
