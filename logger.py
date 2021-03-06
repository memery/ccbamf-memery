import flatactors

class LoggerActor(flatactors.Actor):
    def initialize(self):
        self.wait_for_message = False
        self.keep_the_kids_alive = True
        self.make_babies(
            ('errors', ErrorLogger),
            ('chat', ChatLogger),
            ('raw', RawLogger)
        )

class ErrorLogger(flatactors.Actor):
    def main_loop(self, message):
        _, source, _, payload = message
        print('~~~ERROR in {}: {}'.format(source, payload))

class ChatLogger(flatactors.Actor):
    def main_loop(self, message):
        _, source, _, payload = message
        origin, author, contents = payload
        print('{}/{} <{}> {}'.format(source, origin, author, contents))

class RawLogger(flatactors.Actor):
    def main_loop(self, message):
        _, source, _, payload = message
        print('RAW {}> {}'.format(source, payload))
