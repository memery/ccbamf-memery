#!/usr/bin/env python3
from common import spawn_actor, Actor
from interpretor import InterpretorActor
from irc import IRCMainActor
from logger import LoggerActor

class MasterActor(Actor):

    def constructor(self):
        self.daemon = False

    def initialize(self):
        baby_names = (
            ('interpretor', InterpretorActor),
            ('irc', IRCMainActor),
            ('logger', LoggerActor)
        )

        self.children = {
            name: spawn_actor(class_, self.inbox, name)
            for name, class_ in baby_names
        }

        self.address_book = {}

    def main_loop(self, message):
        target, source, subject, payload = message
        if target == self.name:
            if subject == 'quit':
                self.stop()
                self.broadcast('quit', None)
                return
            elif subject == 'birth':
                self.address_book[source] = payload
        elif target in self.address_book:
            self.address_book[target].write(message)

    def broadcast(self, subject, payload):
        for inbox in self.address_book.values():
            inbox.write((None, self.name, subject, payload))


if __name__ == "__main__":
    main_actor = spawn_actor(MasterActor, None, 'master')
