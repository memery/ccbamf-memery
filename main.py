#!/usr/bin/env python3
from common import spawn_actor, Actor
import interpretor
import irc
import logger

class MasterActor(Actor):

    def constructor(self):
        self.daemon = False

    def initialize(self):
        self.children = {
            'interpretor': spawn_actor(interpretor.InterpretorActor, self.inbox, 'interpretor'),
            'irc': spawn_actor(irc.IRCMainActor, self.inbox, 'irc'),
            'logger': spawn_actor(logger.LoggerActor, self.inbox, 'logger')
        }

    def main_loop(self, message):
        target, source, payload = message
        if target[0] == self.name and payload == 'quit':
            self.stop()
            return
        elif target[0] in self.children:
            self.children[target[0]].write_to((target[1:], source, payload))

if __name__ == "__main__":
    main_actor = spawn_actor(MasterActor, None, 'master')
