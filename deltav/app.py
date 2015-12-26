
import pyglet

game_app = None


def init(*args, **kwargs):
    global game_app
    game_app = DeltaVApp(*args, **kwargs)


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
