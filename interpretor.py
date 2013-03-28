from common import Actor

class InterpretorActor(Actor):

    def main_loop(self, message):
        target, source, payload = message

        destination, author, content = payload

        parsed_msg = temp_parse(content)
        if not parsed_msg:
            return

        # you bet yo ass this is temporary
        content = author + ': ' + parsed_msg

        self.tell_parent((source, self.name, (destination, content)))


def temp_parse(text):
    pairs = {
        '.ping': 'pong',
        'hai': 'hay'
    }
    if text in pairs:
        return pairs[text]
