
import celestials
import ships


class GameState(object):

    COMMANDS = {
        "scan": lambda *_ : _,
        "speed": lambda i: int(i),
        "jump": lambda target, lat, lon, alt: (str(target), int(lat), int(lon), int(alt)),
    }

    scheduled_action = None

    def __init__(self, player, mobs, terrain):
        self._player = player
        self._mobs = list(mobs)
        self._celestials = list(terrain)

    def simulate_step(self):
        for obj in self._celestials:
            obj.simulate_step()
        for obj in self._mobs:
            obj.simulate_step()
        self._player.simulate_step()
        self.execute_player_action()


    def check_command(self, action, args):
        return action, self.COMMANDS[action](*args)

    def schedule_player_action(self, action, args):
        self.scheduled_action = (action, args)

    def execute_player_action(self):
        if not self.scheduled_action:
            return
        
        action, args = self.scheduled_action

        if action == "scan":
            visibles = self._player.visible_objects(self._mobs + self._celestials)
            output = []
            for info in visibles:
                obj, visibility, location, angular_size = info
                heading, distance = location
                output.append(":: Getting a reading at heading {}, magnitude {} {} ({}) s={}".format(heading, visibility, obj._type, obj._name, angular_size))
            print("-"*80)
            for line in output:
                print(line)
            print("-"*80)

        elif action == "period":
            print("Setting period: {}".format(args))
            self._player._period = args

        elif action == "jump":
            target, lat, lon, alt = args
            for c in self._celestials:
                if c._name == target:
                    print("JUMP!", c)
                    self._player.set_orbit(c, mean_distance = alt, orbital_period = self._player._period, position = (lat, lon))
                    break
            else:
                # FIXME: the tick has already run, this needs to happen before that.
                print("No celestial body with that name.")

        self.scheduled_action = None


def new_game():

    from maps import sol
    
    player = ships.PlayerShip()
    player.set_orbit(sol.CELESTIALS["Earth"], mean_distance = 400, orbital_period = 90 * 60, position = (10, 0))

    return GameState(player, sol.MOBS.values(), sol.CELESTIALS.values())