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
        """ __init__ should never be overloaded at all! """
        super().__init__()
        self.inbox = Inbox()
        self.master_inbox = master_inbox
        if master_inbox:
            self.master_inbox.write(('master', name, 'birth', self.inbox))
        self.name = name

        self.daemon = True # Temporary
        self.wait_for_message = True
        self.keep_the_kids_alive = False
        self.child_data = {}
        self.children = {}
        self.constructor(*args)
        self.start()

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
            if self.keep_the_kids_alive:
                self.check_on_the_kids(msg)
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

    # ======== Take care of the kids ==========

    def make_babies(self, *names_and_classes, use_family_name=True):
        """
        Take a pile of tuple arguments with the structure
        (name, class[, *args]) and create actors from them.

        Add the parents name as a prefix if not told not to.
        """
        # Give new names to the kids, using the parent's name as prefix
        if use_family_name:
            names_and_classes = [
                [self.name + ':' + name] + rest
                for name, *rest in names_and_classes
            ]

        # Save the raw data to be able to revive the babies if they die
        self.child_data = {
            name: [name] + args
            for name, *args in names_and_classes
        }

        # Make the babies!
        self.children = {
            name: class_(self.master_inbox, name, *args)
            for name, class_, *args in names_and_classes
        }

    def check_on_the_kids(self, message):
        """
        Make sure the children are alive if they want to be,
        and kill them if the want to die.

        Not even slightly morbid.
        """
        if message:
            _, source, subject, _ = message

        for name, child in list(self.children.items()):
            # Suicides are a-ok! If someone wants to die, let them.
            if message and source == name and subject == 'kill me':
                del self.children[name]

            # Resurrect dead kids
            elif not child.is_alive():
                name, class_, *args = self.child_data[name]
                self.children[name] = class_(self.master_inbox, name, *args)

    # =========================================


    def stop(self):
        self.send('master', 'death', None)
        self.running = False

    def write_to(self, message):
        self.inbox.write(message)

    def send(self, *args, sender=None):
        if not sender:
            sender = self.name
        target, subject, payload = args
        self.master_inbox.write((target, sender, subject, payload))


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
