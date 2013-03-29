from itertools import repeat

from common import Actor, spawn_actor, read_json, read_file_or_die
from irc_connection import IRCConnectionActor

class IRCMainActor(Actor):

    def constructor(self):
        self.daemon = False

    def initialize(self):
        self.wait_for_message = False
        self.irc_settings = read_json(read_file_or_die('config/irc/irc.json'))
        self.networks = read_json(read_file_or_die('config/irc/networks.json'))

        self.children = self.make_babies(*zip(
            self.networks,
            repeat(IRCConnectionActor),
            self.networks.values(),
            repeat(self.irc_settings)
        ))

    def main_loop(self, message):
        if message:
            target, source, subject, payload = message

        for name, child in list(self.children.items()):
            if message and source == name and subject == 'kill me':
                del self.children[name]

            # respawn your children if they died!
            # (but not if they asked to be stopped...)
            elif not child.is_alive():
                # Ditch the 'irc:' prefix to get the network name
                network = name.split(':', 1)[1]
                self.children[name] = spawn_actor(
                    IRCConnectionActor,
                    self.master_inbox,
                    network,
                    self.networks[network],
                    self.irc_settings
                )


        # if there are no more children that are supposed to run,
        # you can just as well kill yourself :(
        # this might be changed into a stop message, possibly,
        # so that the parent process doesn't try to restart
        # everything again, perpetuating some morbid circle.
        if not self.children:
            self.send(('master', self.name, 'quit', None))
            self.stop()
