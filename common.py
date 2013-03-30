import json
import threading
import queue


class Inbox:
    """
    Wrapper for queue, providing a non-blocking read.
    """
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
        """
        This should never be overloaded!

        Use constructor() and/or initialize() instead.
        """
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
        # Call constructor with all the subclass-specific arguments.
        self.constructor(*args)
        self.start()

    def run(self):
        """
        This should never be overloaded, except in very VERY extreme
        circumstances. Use the overloadable functions below instead.
        """
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

        self.before_death()

    # ======== Overloadable functions ========================================

    def constructor(self, *args):
        """
        init-things run BEFORE the actor's thread has begun running.

        This should be used instead of __init__ (which you should never
        overload).
        args are the subclass-specific arguments provided to __init__,
        ie. not those defined in Actor but in the inherited subclas.
        args may be no arguments at all.
        """
        pass

    def initialize(self):
        """
        Run initializing stuff AFTER the actor's thread has begun running.

        If you're wondering if you want to put something in constructor()
        or here, you most likely want it here.
        """
        pass

    def main_loop(self, message):
        """
        The main loop for the actor. Runs every tick (specified as the timeout
        of the inbox) or every time there is a new message.

        If self.wait_for_message is True, the inbox's read() will be blocking
        and message is guaranteed to be a message.
        If it is False, message may be None or a message.
        """
        pass

    def before_death(self):
        """
        Run stuff just before the actor dies. Usually only executed after
        stop() was called.

        This is not terribly useful but might be to some.
        """
        pass

    # ========================================================================

    # ======== Take care of the kids =========================================

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

    # ========================================================================

    def stop(self):
        """
        Stop the actor gracefully.
        """
        self.send('master', 'death', None)
        self.running = False

    def write_to(self, message):
        """ Useless/deprecated? """
        self.inbox.write(message)

    def send(self, *args, sender=None):
        """
        Send a message to master for delivery to the specified target

        sender is the actor itself if not specified. It should not be
        specified at all most of the times.
        """
        if not sender:
            sender = self.name
        target, subject, payload = args
        self.master_inbox.write((target, sender, subject, payload))


def read_json(text):
    """
    Convert the raw json-text to a python data structure, ignoring
    python-esque comments (lines starting with a #) since json doesn't
    have native comments.
    """
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
