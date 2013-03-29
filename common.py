import json
import threading
import os
import queue


# Wrapper for queue, providing a non-blocking read.
class Inbox:
    def __init__(self):
        self.queue = queue.Queue()
    def write(self, message):
        self.queue.put(message)
    def read_wait(self):
        return self.queue.get()
    def read(self):
        try: return self.queue.get(True, 0.1)
        except queue.Empty: return None


class Actor(threading.Thread):
    def __init__(self, parent_inbox, name, *args):
        super().__init__()
        self.inbox = Inbox()
        self.parent_inbox = parent_inbox
        self.name = name

        self.daemon = True # Temporary
        self.wait_for_message = True
        self.constructor(*args)

    def constructor(self, *args):
        pass

    def run(self):
        self.initialize()

        self.running = True
        while self.running:
            if self.wait_for_message:
                msg = self.inbox.read_wait()
            else:
                msg = self.inbox.read()
            self.main_loop(msg)

        self.terminate()

    # ======== Overloadable functions ==========

    def initialize(self):
        pass

    def main_loop(self, message):
        pass

    def terminate(self):
        pass

    # =========================================

    def stop(self):
        self.running = False

    def write_to(self, message):
        self.inbox.write(message)

    def tell_parent(self, message):
        self.parent_inbox.write(message)


def spawn_actor(actor_constructor, parent_inbox, name, *args):
    actor = actor_constructor(parent_inbox, name, *args)
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
