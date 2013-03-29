from itertools import repeat

from common import Actor, read_json, read_file_or_die
from irc_connection import IRCConnectionActor

class IRCMainActor(Actor):

    def constructor(self):
        self.daemon = False

    def initialize(self):
        self.wait_for_message = False
        self.keep_the_kids_alive = True
        self.irc_settings = read_json(read_file_or_die('config/irc/irc.json'))
        self.networks = read_json(read_file_or_die('config/irc/networks.json'))

        self.make_babies(*zip(
            self.networks,
            repeat(IRCConnectionActor),
            self.networks.values(),
            repeat(self.irc_settings)
        ))

    def main_loop(self, message):
        # if there are no more children that are supposed to run,
        # you can just as well kill yourself :(
        # this might be changed into a stop message, possibly,
        # so that the parent process doesn't try to restart
        # everything again, perpetuating some morbid circle.
        if not self.children:
            self.send(('master', self.name, 'quit', None))
            self.stop()
