"""
Object for handling game state. Initialized by the GameView when it is ready
to start a new game (or load an old one).

Receives user input from UI, manages simulation. UI can inspect it to display
information.
"""

import numpy
import pyglet

import deltav.ui
import deltav.physics.body

from pyglet.gl import *
from numpy import *

from deltav.physics.orbit import pi
from deltav.ships import MobShip, PlayerShip
from deltav.ui.keyboard import bindings as k

class GameState(object):

    def __init__(self):

        self.speed = 1
        self.paused = False

        planet = deltav.physics.body.Body(5.972e24, 6371000) 

        self.player = PlayerShip('SASE C-3402 <font face="Droid Sans Fallback">黄河</font> Yellow River')
        self.player.orbit(planet, (6524.834 * 1000,0,0), (0,7.81599286557539 * 1000,0))

        shuttle, station = (
            MobShip("OV-103 Discovery"),
            MobShip("ISS"),
        )

        v_position = (
            -9.389136074764635E+02 * 1000,
            -5.116319908091118E+03 * 1000,
            4.342059664304661E+03 * 1000,
        )

        v_velocity = (
            6.628784989010491E+00 * 1000,
            1.718224103100249E+00 * 1000,
            3.457710395445335E+00 * 1000,
        )

        station.orbit(planet, v_position, v_velocity)
        shuttle.orbit(planet, (
            0,
            6524.834 * 1000,
            0
        ), (
            -30 * 1000,
            0,
            0,
        ))

        ships = (self.player, station) # shuttle, station)

        self.scene = {
            "ships": ships,
            "bodies": (planet,),
        }

    def set_speed(self, delta):
        self.speed += delta
        if self.speed < 1:
            self.speed = 1
        elif self.speed > 100:
            self.speed = 100

    def toggle_pause(self):
        self.paused = not self.paused

    def tick(self):
        if not self.paused:
            for ship in self.scene.get("ships", ()):
                ship._orbit.step(1*self.speed)