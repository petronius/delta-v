"""
Handle all 3D drawing for the game view.

TODO:
- store ship/symbol/orbit colors on class
- solid planets?
- fix symbol jitter
- @perspective/@flat class method decorators
"""
import pyglet

import deltav.ui

import OpenGL
# Has to be set before more imports
OpenGL.ERROR_CHECKING = deltav.configure.DEBUG
from OpenGL.GL import *
from OpenGL.GLU import *



class View3D:

    # Scale factor for the game view, in meters
    SCALE = 1e-5

    FLAT="flat"
    NOFLAT="noflat"

    def __init__(self):

        self.w = deltav.ui.game_window.width
        self.h = deltav.ui.game_window.height

        self.x = 0.0
        self.y = 0.0
        self.z = 512

        self.mode = self.NOFLAT
        
        self.rx = 0
        self.ry = 0
        self.rz = 0

        self.near = 0.1
        self.far = 100192
        self.fov = 60

        # GL initialization
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthFunc(GL_LEQUAL)

    def apply(self):
        """ Apply camera transformation.
        """
        glLoadIdentity()
        if self.mode == self.FLAT:
            return
        glTranslatef(-self.x, -self.y, -self.z)
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.ry, 0, 1, 0)
        glRotatef(self.rz, 0, 0, 1)

    def render(self, scene):
        self.apply()

        for ship in scene.get("ships", ()):
            self.draw_ship(ship)

        for planet in scene.get("bodies", ()):
            self.draw_planet(planet)

        # Reset when we're done, for other rendering actions that need the
        # default pyglet behaviour
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.w, 0, self.h, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    #
    # Rendering setup
    #
    
    def _perspective(self):
        self.mode = self.NOFLAT
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.w/self.h, self.near, self.far)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)

        self.apply()

    def _flat(self):
        self.mode = self.FLAT

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.w, 0, self.h, 0, self.far)
        glMatrixMode(GL_MODELVIEW)

        self.apply()

    #
    # Coordinate mapping
    #

    def _world_to_scene(self, coords):
        """
        Convert physics coordinates to render coordinates.
        """
        return tuple(map(lambda x: x*self.SCALE, coords))

    def _scene_to_screen(self, coords):
        """
        Rotate world coordinates x, y to screen coordinates
        """
        x, y, _ = coords
        self._perspective() # reset before doing any maths

        mmat = glGetDoublev(GL_MODELVIEW_MATRIX)
        pmat = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        x, y, _ = gluProject(x, y, _, mmat, pmat, viewport)

        return x, y, 0

    def drag(self, dx, dy, button):
        """ Mouse drag event handler.
        """
        if button == 1:
            self.x -= dx*2
            self.y -= dy*2
        elif button == 2:
            self.x -= dx*2
            self.z -= dy*2
        elif button == 4:
            self.ry += dx/4.
            self.rx -= dy/4.

    def scroll(self, delta):
        self.z += delta*20

    #
    # Drawing functions. Needs cleanup
    #

    def draw_planet(self, planet, pts=30, color=(255,0,0)):

        r = planet.radius * self.SCALE

        self.draw_sphere(planet.position, r, color)


    def draw_ship(self, ship, orbit_color=(0,0,255), ship_color=(0,0,255)):

        orbit = [self._world_to_scene(p) for p in ship._orbit.get_plot(60)]
        self.draw_loop(orbit, orbit_color)

        coords = self._world_to_scene(ship.position)

        self.text(ship._name, coords)
        self.draw_symbol(coords, ship_color)

    def text(self, s, coords):
        """
        Add text in the scene
        """

        x, y, _ = self._scene_to_screen(coords)

        self._flat()

        pyglet.text.Label(s,
            font_size=10,
            x = x + 10,
            y = y,
            anchor_x = "left",
            anchor_y = "top"
        ).draw()


    def draw_symbol(self, coords, color, offset=5):
        """
        Draw a flat symbol
        """
        x, y, _ = self._scene_to_screen(coords)

        a = (x, y+offset)
        b = (x+offset, y)
        c = (x-offset, y)

        self._flat()
        pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
            ('v2f', a + b + c),
            ('c3B', color*3),
        )


    def draw_loop(self, verticies, color):
        # Set up for more rendering
        self._perspective()

        glColor3f(*color)
        glBegin(GL_LINE_LOOP)
        for vtx in verticies:
            glVertex3f(*vtx)
        glEnd()


    def draw_sphere(self, coords, radius, color):
        self._perspective()

        stacks = slices = 20

        glColor3f(*color)
        q = gluNewQuadric()
        gluQuadricNormals(q, GLU_NONE)
        gluQuadricDrawStyle(q, GLU_LINE)
        gluQuadricTexture(q, GL_TRUE)
        glTranslatef(0.0,0.0,0.0)
        glRotatef(90, 1, 0, 0)
        gluSphere(q, radius, slices, stacks)

        gluDeleteQuadric(q)
