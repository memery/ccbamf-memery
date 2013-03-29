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
    def __init__(self, master_inbox, name, *args):
        super().__init__()
        self.inbox = Inbox()
        self.master_inbox = master_inbox
        if master_inbox:
            self.master_inbox.write(('master', name, 'birth', self.inbox))
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

    def make_babies(self, *names_and_classes, use_family_name=True):
        """
        Take a pile of tuple arguments with the structure
        (name, class[, *args]) and create actors from them.

        Add the parents name as a prefix if not told not to.
        """
        prefix = self.name + ':' if use_family_name else ''
        return {
            prefix+name: spawn_actor(class_, self.master_inbox, prefix+name, *args)
            for name, class_, *args in names_and_classes
        }

    def stop(self):
        self.running = False

    def write_to(self, message):
        self.inbox.write(message)

    def send(self, message):
        self.master_inbox.write(message)


def spawn_actor(actor_constructor, master_inbox, name, *args):
    actor = actor_constructor(master_inbox, name, *args)
    actor.start()
    return actor


def read_json(text):
    without_comments = [line for line in text.splitlines()
                        if not line.startswith('#')]
    return json.loads('\n'.join(without_comments))

def read_file_or_die(fname):
    """
    Read a file and return the raw data.
    Throws exception if it doesn't exist.
    """
    with open(fname, encoding='utf-8') as f:
        return f.read()
