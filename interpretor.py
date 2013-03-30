import threading
import queue

from flatactors import Actor

class InterpretorActor(Actor):
    def constructor(self):
        self.daemon = False

    def initialize(self):
        self.wait_for_message = False
        self.active_processes = []

    def main_loop(self, message):
        if message:
            target, source, subject, payload = message
            if subject == 'quit' and source == 'master':
                self.stop()
                return
            elif subject == 'interpret':
                destination, author, content = payload
                q = queue.Queue()
                worker = ParserWorker(source, destination, author, content, q)
                self.active_processes.append((q, worker))

        for item in list(self.active_processes):
            q, process = item
            try:
                data = q.get_nowait()
            except queue.Empty:
                pass
            else:
                target, destination, response = data
                self.send(target, 'response', (destination, response))
            if not process.is_alive():
                self.active_processes.remove(item)


class ParserWorker(threading.Thread):
    def __init__(self, source, destination, author, content, response_queue):
        super().__init__()
        self.source = source
        self.destination = destination
        self.author = author
        self.content = content
        self.response_queue = response_queue
        self.start()

    def run(self):
        pairs = {
            '.ping': 'pong',
            'hai': 'hay'
        }
        if self.content in pairs:
            out = (self.source, self.destination,
                   self.author + ': ' + pairs[self.content])
            self.response_queue.put(out)

