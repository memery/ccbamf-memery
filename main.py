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


if __name__ == "__main__":
    class Parent():
        def __init__(self):
            self.children = {}
    p = Parent()
    p.children['master'] = MasterActor(None, p, 'master')
