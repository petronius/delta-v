
import pyglet

from deltav.window import DeltaVWindow
from deltav.views.game import GameView


class DeltaVApp(pyglet.app.EventLoop):
    """
    A subclass of :py:class:`pyglet.app.EventLoop`. This manages the running
    loop and is responsible for setting an exit code when the loop quits.
    """

    #: Has a value of ``None`` until the event loop exits, at which point the
    #: value will match a suitable POSIX exit code (see
    #: :mod:`errno <python:errno>` in the stdlib). (0 for a normal exit, a
    #: positive integer for anything else.)
    returncode = None

    def __init__(self, *args, **kwargs):
        super(DeltaVApp, self).__init__(*args, **kwargs)
        # TODO: this should be configurable to use all available displays in
        # full screen, for extra spaceshipness
        self.window = DeltaVWindow()
        # TODO: in future, we will load the main menu first instead
        self.new_game()

    def new_game():
        self.gameserver = GameServer()
        self.gameclient = GameClient(self.gameserver)
        self.gameclient.connect()
        view = GameView(client=self.gameclient)
        self.window.set_view(view)
        # Schedule the event loop to trigger updates in the window each tick.
        pyglet.clock.schedule(self.window.tick)

    def user_quit(self):
        """
        Should be called whenever the user asks the app to quit. Stops the app
        loop so that cleanup processes can run before the program exits.

        Once the app has quit, this method will set the value of
        :attr:`returncode` so that the main program can use it to determine
        which exit code to quit with.
        """
        self.exit()
        self.returncode = 0
