
from common import spawn_actor, Actor
import logger
import irc

class MasterActor(Actor):

    def constructor(self):
        self.daemon = False

    def initialize(self):
        self.children = {
            'logger': spawn_actor(logger.LoggerActor, self.inbox),
            'irc': spawn_actor(irc.IRCMainActor, self.inbox)
        }

    def main_loop(self, message):
        if message == "DIE":
            self.stop()
            return

        elif message:
            self.children['logger'].write_to(message)

if __name__ == "__main__":
    main_actor = spawn_actor(MasterActor, None)
