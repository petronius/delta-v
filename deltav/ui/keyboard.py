"""
A module for simplifying control binding and keyboard lookups
"""

import deltav.ui

from pyglet.window import key

# A dictionary that maps action names to a list of acceptable key presses for
# that action.
bindings = {

    "SPEED_1": key._1,
    "SPEED_2": key._2,
    "SPEED_3": key._3,
    "SPEED_4": key._4,
    "SPEED_5": key._5,
    "SPEED_6": key._6,
    "SPEED_7": key._7,
    "SPEED_8": key._8,
    "SPEED_9": key._9,

    "SHOW_SYMBOLS": key.F4,
    "SHOW_ORBITS": key.F3,
    "SHOW_BODIES": key.F2,
    "SHOW_LABELS": key.F1,
    
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
