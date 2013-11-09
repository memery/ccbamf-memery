#!/usr/bin/env python3
from imp import reload
import common
import flatactors
import interpretor
import irc
import main
import logger

class Main(flatactors.Actor):

    def constructor(self):
        self.module_name = 'main'
        self.daemon = False
        print("pling")

    def initialize(self):
        self.make_babies(
            ('interpretor', interpretor),
            ('irc', irc),
            ('logger', logger),
            use_family_name=False
        )

    def main_loop(self, message):
        target, source, subject, payload = message
        if subject == 'testreload':
            reload(flatactors)
            print(self.children['irc'].parent == self)
            self.reload()

        elif subject == 'test':
            # print(globals()['__name__'])
            # self.test()
            print([(k,v) for k,v in main.__dict__.items()])
            # self.send('logger', 'reload', None)
            # self.send('irc:gfu', 'response', ('#iaydica', huhu(1,2)))

def huhu(a,b):
    return "{}{} arst".format(a,b)


if __name__ == "__main__":
    class Parent():
        def __init__(self):
            self.children = {}
            self.child_data = {'master': Main}
    p = Parent()
    p.children['master'] = Main(None, p, 'master')
