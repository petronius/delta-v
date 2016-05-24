"""
A module for simplifying control binding and keyboard lookups
"""

import deltav.ui

from pyglet.window import key

# A dictionary that maps action names to a list of acceptable key presses for
# that action.
bindings = {

    "QUIT": key.ESCAPE,

    "SET_SPEED_1": key._1,
    "SET_SPEED_2": key._2,
    "SET_SPEED_3": key._3,
    "SET_SPEED_4": key._4,
    "SET_SPEED_5": key._5,
    "SET_SPEED_6": key._6,
    "SET_SPEED_7": key._7,
    "SET_SPEED_8": key._8,
    "SET_SPEED_9": key._9,

    "SPEED_PLUS": key.F,
    "SPEED_MINUS": key.S,
    "SPEED_PAUSE": key.SPACE,

    "CYCLE_FOCUS": key.C,

    "SHOW_SYMBOLS": key.F4,
    "SHOW_ORBITS": key.F3,
    "SHOW_BODIES": key.F2,
    "SHOW_LABELS": key.F1,

    "CYCLE_TARGET": key.T,
    "SHOOT_AT_TARGET_A": key.Q,
    "SHOOT_AT_TARGET_T": key.W,

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
