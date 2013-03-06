import common
import time

class InputActor(common.Actor):
    def main_loop(self, irrelevant_message):
        self.tell_parent('TIME: {}'.format(time.clock()))
