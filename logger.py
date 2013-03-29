import common

class LoggerActor(common.Actor):
    def initialize(self):
        self.children = self.make_babies(
            ('logger:errors', ErrorLogger),
            ('logger:chat', ChatLogger),
            ('logger:raw', RawLogger)
        )

class ErrorLogger(common.Actor):
    def main_loop(self, message):
        _, source, _, payload = message
        print('~~~ERROR in {}: {}\n'.format(source, payload))

class ChatLogger(common.Actor):
    def main_loop(self, message):
        _, source, _, payload = message
        origin, author, contents = payload
        print('{}/{} <{}> {}'.format(source, origin, author, contents))

class RawLogger(common.Actor):
    def main_loop(self, message):
        _, source, _, payload = message
        print('RAW {}> {}'.format('/'.join(source), payload))
