from common import Actor, spawn_actor, read_json, read_file_or_die
from irc_connection import IRCConnectionActor

class IRCMainActor(Actor):

    def constructor(self):
        self.daemon = False

    def initialize(self):
        self.wait_for_message = False
        self.irc_settings = read_json(read_file_or_die('config/irc/irc.json'))
        self.networks = read_json(read_file_or_die('config/irc/networks.json'))

        self.children = {
            network: spawn_actor(IRCConnectionActor, self.inbox, network,
                                 self.networks[network], self.irc_settings)
            for network in self.networks
        }

    def main_loop(self, message):
        if message:
            target, source, payload = message
            if target[0] in self.children:
                self.children[target[0]].write_to((target[1:], source, payload))
            else:
                newsource = [self.name] + source
                self.tell_parent((target, newsource, payload))

        for network, child in list(self.children.items()):
            if message and target[0] == self.name and source[0] == network \
                        and payload == 'kill me':
                del self.children[network]

            # respawn your children if they died!
            # (but not if they asked to be stopped...)
            elif not child.is_alive():
                self.children[network] = \
                    spawn_actor(IRCConnectionActor, self.inbox, network,
                                self.networks[network], self.irc_settings)



        # if there are no more children that are supposed to run,
        # you can just as well kill yourself :(
        # this might be changed into a stop message, possibly,
        # so that the parent process doesn't try to restart
        # everything again, perpetuating some morbid circle.
        if not self.children:
            self.tell_parent((['master'], [self.name], 'quit'))
            self.stop()
