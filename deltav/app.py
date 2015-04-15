
import shlex

class App(object):

    _prompt = ": "

    def __init__(self, gamestate):
        self._g = gamestate
        self._e = 0

    def _handle_input(self, inp):
        if inp:
            inp = shlex.split(inp)
            cmd, args = inp[0], inp[1:]
            try:
                cmd, args = self._g.check_command(cmd, args)
                self._g.schedule_player_action(cmd, args)
                return True
            except Exception as e:
                print("Bad command: {}".format(e))
        else:
            return True
        return False

    def run(self):
        import readline
        try:
            while True:
                inp_valid = None
                while not inp_valid:
                    if inp_valid is not None:
                        print("Invalid input!")
                    inp = input(self._prompt)
                    inp_valid = self._handle_input(inp)
                self._g.simulate_step()
        except (KeyboardInterrupt, EOFError):
            self._e = 1
        return self._e


_app = None

def run(gamestate):
    global _app
    _app = App(gamestate)
    return _app.run()