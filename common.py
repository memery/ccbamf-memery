import json
import multiprocessing
import os
import queue


# # Wrapper for queue, providing a non-blocking read.
class Inbox:
    def __init__(self):
        self.queue = multiprocessing.Queue()
    def write(self, message):
        self.queue.put(message)
    def read_wait(self):
        return self.queue.get()
    def read(self):
        try: return self.queue.get(True, 1)
        except queue.Empty: return None


class Actor(multiprocessing.Process):
    def __init__(self, parent_inbox):
        # TEMPORARY
        super().__init__()
        self.inbox = Inbox()
        self.parent_inbox = parent_inbox
        self.daemon = True

    def run(self):
        self.initialize()

        self.running = True
        while self.running:
            self.main_loop(self.inbox.read())

        self.terminate()

    def initialize(self):
        pass

    def main_loop(self, message):
        pass

    def terminate(self):
        pass

    def stop(self):
        self.running = False

    def write_to(self, message):
        self.inbox.write(message)

    def tell_parent(self, message):
        self.parent_inbox.write(message)


def spawn_actor(actor_constructor, parent_inbox, *args):
    actor = actor_constructor(parent_inbox, *args)
    actor.start()
    return actor


def read_json(text):
    without_comments = [line for line in text.splitlines()
                        if not line.startswith('#')]
    return json.loads('\n'.join(without_comments))

def read_file_or_die(fname):
    """ Read a file and return the raw data. Throws exception if it doesn't exist. """
    with open(fname, encoding='utf-8') as f:
        return f.read()
