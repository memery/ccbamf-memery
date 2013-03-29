import common

class LoggerActor(common.Actor):
    def initialize(self):
        self.children = dict(
            errors = common.spawn_actor(ErrorLogger, self.inbox, 'errors'),
            chat = common.spawn_actor(ChatLogger, self.inbox, 'chat'),
            raw = common.spawn_actor(RawLogger, self.inbox, 'raw')
        )

    def main_loop(self, message):
        target, source, payload = message
        if target[0] in self.children:
            self.children[target[0]].write_to((target[1:], source, payload))
        else:
            newsource = [self.name] + source
            self.tell_parent((target, newsource, payload))


class ErrorLogger(common.Actor):
    def main_loop(self, message):
        _, source, payload = message
        print('~~~ERROR in {}: {}\n'.format(source, payload))

class ChatLogger(common.Actor):
    def main_loop(self, message):
        _, source, payload = message
        origin, author, contents = payload
        print('{}/{} <{}> {}'.format(source[-1], origin, author, contents))

class RawLogger(common.Actor):
    def main_loop(self, message):
        _, source, payload = message
        print('RAW {}> {}'.format('/'.join(source), payload))
