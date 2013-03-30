#!/usr/bin/env python3
from flatactors import Actor
from interpretor import InterpretorActor
from irc import IRCMainActor
from logger import LoggerActor

class MasterActor(Actor):

    def constructor(self):
        self.daemon = False

    def initialize(self):
        self.make_babies(
            ('interpretor', InterpretorActor),
            ('irc', IRCMainActor),
            ('logger', LoggerActor),
            use_family_name=False
        )

    def main_loop(self, message):
        pass


if __name__ == "__main__":
    main_actor = MasterActor(None, 'master')
