"""
Handle all 3D drawing for the game view.

TODO:
- store ship/symbol/orbit colors on class
- solid planets?
- fix symbol jitter
- @perspective/@flat class method decorators
- Collaps draw_(ships|planets) into render()
"""
import pyglet
import numpy

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

    SYMBOL_COLOR = (0, 255, 0)
    LABEL_COLOR = (255, 255, 255, 255)
    BODY_COLOR = (255, 0, 0)
    ORBIT_COLOR = (0, 0, 255)

    FONT_FACE="Droid Sans Mono"

    def __init__(self, game_view, bounds, center_on):

        self.bx, self.by, self.w, self.h = bounds

        self.x = 0.0
        self.y = 0.0
        self.z = 312

        self.mode = self.NOFLAT
        
        self.rx = 0
        self.ry = 0
        self.rz = 0

        self.near = 0.1
        self.far = 10000000
        self.fov = 60

        # GL initialization
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthFunc(GL_LEQUAL)

        self.center_on(center_on)

    def center_on(self, coords):
        #self.center = numpy.array([0,0,0])
        #return
        x, y, z = map(lambda x: x*self.SCALE, coords)
        self.center = numpy.array([x, y, z])


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

    def render(self, game_view):
        scene = game_view.game_state.get_scene_data()
        _debug_boxes = game_view.game_state.get_debug_boxes()
        self.apply()

        for uuid, ship in scene["ships"].items(): # passing in the night

            if game_view.get_option("tracking", "orbits"):
                orbit = [self._world_to_scene(p) for p in ship["orbit"]["plot"]]

                if ship["orbit"]["is_elliptical"]:
                    self.draw_loop(orbit, self.ORBIT_COLOR)
                else:
                    self.draw_line(orbit, self.ORBIT_COLOR)

            coords = self._world_to_scene(ship["position"])

            if game_view.get_option("tracking", "labels"):
                self.text(ship["name"], coords)

            if game_view.get_option("tracking", "symbols"):
                self.draw_triangle(coords, self.SYMBOL_COLOR)

        for uuid, bullet in scene["bullets"].items(): # a hail of

            if game_view.get_option("tracking", "orbits"):
                orbit = [self._world_to_scene(p) for p in bullet["orbit"]["plot"]]

                if bullet["orbit"]["is_elliptical"]:
                    self.draw_loop(orbit, self.ORBIT_COLOR)
                else:
                    self.draw_line(orbit, self.ORBIT_COLOR)

            coords = self._world_to_scene(bullet["position"])

            if game_view.get_option("tracking", "symbols"):
                self.draw_diamond(coords, (255, 0, 0))

        for uuid, debris in scene["debris"].items(): # a hail of

            if game_view.get_option("tracking", "orbits"):
                orbit = [self._world_to_scene(p) for p in debris["orbit"]["plot"]]

                if debris["orbit"]["is_elliptical"]:
                    self.draw_loop(orbit, self.ORBIT_COLOR)
                else:
                    self.draw_line(orbit, self.ORBIT_COLOR)

            coords = self._world_to_scene(debris["position"])

            if game_view.get_option("tracking", "symbols"):
                self.draw_square(coords, (100, 100, 100))

        if game_view.get_option("tracking", "bodies"):
            for uuid, planet in scene["bodies"].items(): # rising to the surface
                r = planet["radius"] * self.SCALE
                p = self._world_to_scene(planet["position"])
                self.draw_sphere(p, r, self.BODY_COLOR)

        if _debug_boxes:
            for box in _debug_boxes:
                self.draw_cube(*box)

        # Reset when we're done, for other rendering actions that need the
        # default pyglet behaviour
        width, height = deltav.ui.game_window.width, deltav.ui.game_window.height
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, width, height)
        glOrtho(0, width, 0, height, -1, 2)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    #
    # Rendering setup
    #
    
    def _perspective(self):
        self.mode = self.NOFLAT
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(self.bx, self.by, self.w, self.h)
        gluPerspective(self.fov, self.w/self.h, self.near, self.far)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)

        self.apply()

    def _flat(self):
        self.mode = self.FLAT

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(self.bx, self.by, self.w, self.h)
        glOrtho(0, self.w, 0, self.h, -1, 2)
        glMatrixMode(GL_MODELVIEW)

        self.apply()

    #
    # Coordinate mapping
    #

    def _world_to_scene(self, coords):
        """
        Convert physics coordinates to render coordinates.
        """
        result = self.center - tuple(map(lambda x: x*self.SCALE, coords))
        return tuple(result)

    def _scene_to_screen(self, coords, snap_to_edge=False):
        """
        Rotate world coordinates x, y to screen coordinates
        """
        x, y, z = coords
        self._perspective() # reset before doing any maths

        mmat = glGetDoublev(GL_MODELVIEW_MATRIX)
        pmat = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        x, y, z = gluProject(x, y, z, mmat, pmat, viewport)

        x -= self.bx
        y -= self.by

        if snap_to_edge == True:
            x, y, z = self._snap_to_edge(x, y, z)

        return int(x), int(y), int(z)

    def _snap_to_edge(self, x, y, z):
        """
        For things we want to indicate the direction of, even when we can't
        see them.
        """
        # _xmax = self.bx + self.w - 10
        # _ymax = self.by + self.h - 10
        # _xmin = self.bx + 10
        # _ymin = self.by + 10

        # if z >= 1:
        #     # keep it in front of the camera
        #     z = .9
        #     # move the point offscreen beyond the edge of the current quadrant
        #     # it is in. the next step will snap it back to the edge
        #     if y < self.by + self.h/2:
        #         y = self.by - y
        #     elif self.by + self.h/2 < y:
        #         y += _ymax
        #     if x < self.bx + self.w/2:
        #         x = self.bx - x
        #     elif self.bx + self.w/2 < x:
        #         x += _xmax
        # if x < _xmin:
        #     x = _xmin
        # elif x > _xmax:
        #     x = _xmax
        # if y < _ymin:
        #     y = _ymin
        # elif y > _ymax:
        #     y = _ymax
        return x, y, z

    def drag(self, dx, dy, button):
        """
        Mouse drag event handler.
        """
        if button == 1:
            self.x -= dx*2
            self.y -= dy*2
        elif button == 2:
            self.z += dy*10
        elif button == 4:
            self.ry += dx/4.
            self.rx -= dy/4.

    def scroll(self, delta):
        """
        Scroll wheel
        """
        self.z += delta*10

    #
    # Drawing functions.
    #

    def text(self, s, coords):
        """
        Add text in the scene

        FIXME: position labels optimally for location on screen (ie, don't draw
                offscreen).
        BONUS: don't let labels be drawn on each other
        """

        x, y, z = self._scene_to_screen(coords, snap_to_edge = True)

        if z < 1:

            self._flat()

            s = '<font face="%s" size="1" color="#FFFFFF">%s</font>' % (self.FONT_FACE, s)

            pyglet.text.HTMLLabel(s,
                x = x + 10,
                y = y,
                anchor_x = "left",
                anchor_y = "top",
            ).draw()


    def draw_triangle(self, coords, color, offset=5):
        """
        Draw a flat symbol
        """

        x, y, z = self._scene_to_screen(coords, snap_to_edge = True)

        a = (x, y+offset, z)
        b = (x+offset, y, z)
        c = (x-offset, y, z)

        self._flat()
        pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
            ('v3f', a + b + c),
            ('c3B', color*3),
        )


    def draw_diamond(self, coords, color, offset=5):
        """
        Draw a flat symbol
        """

        x, y, z = self._scene_to_screen(coords, snap_to_edge = True)

        a = (x, y+offset, z)
        b = (x+offset, y, z)
        c = (x, y-offset, z)
        d = (x-offset, y, z)

        self._flat()
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
            ('v3f', a + b + c + d),
            ('c3B', color*4),
        )


    def draw_square(self, coords, color, offset=5):
        """
        Draw a flat symbol
        """

        x, y, z = self._scene_to_screen(coords, snap_to_edge = True)

        a = (x-offset, y+offset, z)
        b = (x+offset, y+offset, z)
        c = (x+offset, y-offset, z)
        d = (x-offset, y-offset, z)

        self._flat()
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
            ('v3f', a + b + c +d),
            ('c3B', color*4),
        )

    def draw_cube(self, p1, p2):
        p1 = self._world_to_scene(p1)
        p2 = self._world_to_scene(p2)

        color = (0.0, 0.0, 1) # the diagonal
        self.draw_line((p1, p2), color)

        self._perspective()

        glColor3f(*color)
        glBegin(GL_LINE_STRIP)
        # top
        glVertex3f(p1[0], p1[1], p1[2])        
        glVertex3f(p1[0], p1[1], p2[2])

        glVertex3f(p2[0], p1[1], p2[2])

        glVertex3f(p2[0], p1[1], p1[2])
        
        glVertex3f(p1[0], p1[1], p1[2])
        # bottom
        glVertex3f(p1[0], p2[1], p1[2])        
        glVertex3f(p1[0], p2[1], p2[2])
        
        glVertex3f(p2[0], p2[1], p2[2])
        
        glVertex3f(p2[0], p2[1], p1[2])
        
        glVertex3f(p1[0], p2[1], p1[2])
        # sides
        glEnd()
        glBegin(GL_LINE_STRIP)
        glVertex3f(p1[0], p1[1], p2[2])
        glVertex3f(p1[0], p2[1], p2[2])

        glEnd()
        glBegin(GL_LINE_STRIP)
        glVertex3f(p2[0], p1[1], p2[2])
        glVertex3f(p2[0], p2[1], p2[2])

        glEnd()
        glBegin(GL_LINE_STRIP)
        glVertex3f(p2[0], p1[1], p1[2])
        glVertex3f(p2[0], p2[1], p1[2])

        glEnd()



    def draw_loop(self, verticies, color):
        # Set up for more rendering
        self._perspective()

        glColor3f(*color)
        glBegin(GL_LINE_LOOP)
        for vtx in verticies:
            glVertex3f(*vtx)
        glEnd()


    def draw_line(self, verticies, color):
        self._perspective()
        glColor3f(*color)
        glBegin(GL_LINE_STRIP)
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
        glTranslatef(*coords)
        glRotatef(90, 1, 0, 0)
        gluSphere(q, radius, slices, stacks)

        gluDeleteQuadric(q)
