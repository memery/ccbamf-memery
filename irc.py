from itertools import repeat

import flatactors
from common import read_json, read_file_or_die
import common
import irc_connection
import irc_parser

class Irc(flatactors.Actor):

    def constructor(self):
        self.module_name = 'irc'
        self.daemon = False

    def initialize(self):
        self.wait_for_message = False
        self.keep_the_kids_alive = True
        self.irc_settings = read_json(read_file_or_die('config/irc/irc.json'))
        self.networks = read_json(read_file_or_die('config/irc/networks.json'))

        self.make_babies(*zip(
            self.networks,
            repeat(irc_connection),
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
                            self.send(source, 'die', None)
                            del self.children[source]

                        if ircmessage.split()[1] == 'restart':
                            self.send(source, 'die', None)

                        # TODO: Remove this completely, of course
                        if ircmessage.split()[1] == 'ircexcept':
                            raise Exception

                        if ircmessage.split()[1] == 'reload':
                            self.send('master', 'testreload', None)

                        if ircmessage.split()[1] == 'lol':
                            self.send('master', 'test', None)

                    new_payload = (channel, nick, ircmessage)
                    self.send('interpretor', 'interpret', new_payload, sender=source)
                    self.send('logger:chat', 'log', new_payload, sender=source)
                else:
                    self.send('logger:raw', 'log', line, sender=source)



        # if there are no more children that are supposed to run,
        # you can just as well kill yourself :(
        # this might be changed into a stop message, possibly,
        # so that the parent process doesn't try to restart
        # everything again, perpetuating some morbid circle.
        if not self.children:
            self.send('master', 'quit', None)
            self.stop()
