
import sys

import app
import game


if __name__ == "__main__":
    gamestate = game.new_game()
    retcode = app.run(gamestate)
    sys.exit(retcode)