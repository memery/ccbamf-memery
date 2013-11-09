from imp import reload
import threading
import queue
import sys
import traceback

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
    def __init__(self, master_inbox, parent, name, *args, oldvars=None):
        """
        This should never be overloaded!

        Use constructor() and/or initialize() instead.
        """
        super().__init__()
        self.inbox = Inbox()
        self.master_inbox = master_inbox
        if master_inbox:
            self.master_inbox.write(('master', name, 'birth', self.inbox))
            self.independent = False
        else:
            self.independent = True
            self.address_book = {}
        self.parent = parent
        self.name = name

        self.daemon = True # Temporary
        self.wait_for_message = True
        self.keep_the_kids_alive = False
        self.child_data = {}
        self.children = {}
        # Call constructor with all the subclass-specific arguments.
        self.constructor(*args)
        # Use the last incarnation's state if possible
        if oldvars:
            newvars = vars(self)
            for k,v in oldvars.items():
                if k in newvars and not k.startswith('_'):
                    setattr(self, k, v)
        self.start()

    def run(self):
        """
        This should never be overloaded, except in very VERY extreme
        circumstances. Use the overloadable functions below instead.
        """
        self.initialize()
        self.running = True
        while self.running:
            try:
                if self.wait_for_message:
                    msg = self.inbox.read_wait()
                else:
                    msg = self.inbox.read()
                if self.keep_the_kids_alive:
                    self.check_on_the_kids(msg)
                if self.independent:
                    self.manage_address_book(msg)
                self.manage_reloading(msg)
                self.main_loop(msg)
            except Exception as e:
                target = 'logger:errors'
                subject = 'log'
                payload = 'Actor crashed in or before main_loop: {}, {}'.format(type(e), e)
                traceback.print_exc(file=sys.stdout)
                if self.independent:
                    self.address_book[target].write((target, self.name,
                                                     subject, payload))
                else:
                    self.send(target, subject, payload)
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

    def make_babies(self, *names_and_modules, use_family_name=True):
        """
        Take a pile of tuple arguments with the structure
        (name, module[, *args]) and create actors from them.

        Add the parents name as a prefix if not told not to.
        """
        if self.children:
            return

        # Give new names to the kids, using the parent's name as prefix
        if use_family_name:
            names_and_modules = [
                [self.name + ':' + name] + rest
                for name, *rest in names_and_modules
            ]

        # Save the raw data to be able to revive the babies if they die
        self.child_data = {
            name: args
            for name, *args in names_and_modules
        }

        # If this IS the master, use your own inbox as master inbox
        master_inbox = self.inbox if self.independent else self.master_inbox

        def get_class(module):
            classname = ''.join([x.capitalize()
                                for x in module.__name__.split('_')])
            return getattr(module, classname)

        # Make the babies!
        self.children = {
            name: get_class(module)(master_inbox, self, name, *args)
            for name, module, *args in names_and_modules
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
                class_, *args = self.child_data[name]
                self.children[name] = class_(self.master_inbox, name, *args)

    # ========================================================================

    # ======== Manage your address book =========================================

    def manage_address_book(self, message):
        """
        Manage the central directory of subactors to this one,
        removing actors as they die and adding them as they are
        born. Also responsible for passing messages on to the
        correct subactor as long as it is registered.
        """
        target, source, subject, payload = message
        if target == self.name:
            if subject == 'quit':
                self.stop()
                for inbox in self.address_book.values():
                    inbox.write((None, self.name, subject, payload))
            if subject == 'birth':
                self.address_book[source] = payload
            if subject == 'death' and source in self.address_book:
                del self.address_book[source]
        elif target in self.address_book:
            self.address_book[target].write(message)

    # ========================================================================

    def stop(self):
        """
        Stop the actor gracefully.
        """
        # Master doesn't need to tell itself that it's dead
        if not self.independent:
            self.send('master', 'death', None)
        self.running = False

    def send(self, *args, sender=None):
        """
        Send a message to master for delivery to the specified target

        sender is the actor itself if not specified. It should not be
        specified at all most of the times.
        """
        if not sender:
            sender = self.name
        target, subject, payload = args
        message = (target, sender, subject, payload)
        if self.independent:
            self.address_book[target].write(message)
        else:
            self.master_inbox.write(message)

    def report_error(self, message):
        self.send('logger:errors', 'log', message)

    # ========================================================================

    # ======== Reloading =====================================================

    def manage_reloading(self, message):
        if not message:
            return
        target, sender, subject, payload = message
        if target == self.name and subject == 'reload':
            self.reload()

    def reload(self):
        if not hasattr(self, 'module_name'):
            self.report_error('[reload] No module name specified in class')
            return
        try:
            module = sys.modules[self.module_name]
        except KeyError:
            self.report_error('[reload] No such module')
            return
        if not hasattr(module, 'mainclass'):
            self.report_error('[reload] No reincarnation class specified in module')
            return
        try:
            reload(module)
        except SyntaxError:
            self.report_error('[reload] Syntax error when reloading, aborting')
        else:
            myvars = vars(self)
            reincarnation = module.mainclass(None, self.parent,
                                                  self.name, oldvars=myvars)
            self.parent.children[self.name] = reincarnation
            for child in self.children.values():
                child.parent = reincarnation
            self.send('logger:raw', 'log', '[reload] Done reloading, killing myself')
            # Don't use self.stop() here since it deregisters the actor
            # with master after the new class has already registered
            self.running = False

    # ========================================================================
