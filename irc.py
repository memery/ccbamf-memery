from itertools import repeat

from common import Actor, read_json, read_file_or_die
from irc_connection import IRCConnectionActor
import irc_parser

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

            if subject == 'irc line':
                line, nudge = payload
                user, command, arguments = irc_parser.split(line)
                nick = irc_parser.get_nick(user)

                if command == 'PRIVMSG' and source in self.children:
                    channel, ircmessage = arguments

                    ### some test codes:
                    # TODO: make these functions only available
                    # to admins... (and move them out of IRC
                    # god damn it! they might as well be protocol
                    # agnostic as long as there's a way for
                    # IRC to tell interpretor that the admin
                    # is authenticated.)

                    # TODO: These were previously
                    #     if ircmessage and self.state ...
                    # why the ircmessage check?

                    # this stops the current irc thread
                    # and prevents it from being respawned
                    if nudge:
                        if ircmessage.split()[1] == 'stop':
                            self.send((source, self.name, 'die', None))
                            del self.children[source]

                        if ircmessage.split()[1] == 'restart':
                            self.send((source, self.name, 'die', None))

                    new_payload = (channel, nick, ircmessage)
                    self.send(('interpretor', self.name, 'interpret', new_payload))
                    self.send(('logger:chat', source, 'log', new_payload))
                else:
                    self.send(('logger:raw', source, 'log', line))


            if subject == 'response':
                # TODO: Implement this properly in interpretor
                # before opening the flood gates here.
                # Or don't, and use it as a playground for a
                # resilient irc.py...
                pass
                # (recipient, channel, content) = payload
                # self.send((recipient, self.name, 'response', irc_parser.make_privmsg(channel, content)))


        for name, child in list(self.children.items()):
            # respawn your children if they died!
            if not child.is_alive():
                # Ditch the 'irc:' prefix to get the network name
                network = name.split(':', 1)[1]
                self.children[name] = self.make_a_baby(
                    network,
                    IRCConnectionActor,
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
