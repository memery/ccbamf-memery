
import socket
import ssl
from time import sleep
import common
import irc_parser


class Socket:

    """ A line buffered IRC socket interface. send(text) sends
        text as UTF-8 and appends a newline, read() reads text
        and returns a list of strings which are the read lines
        without a line separator."""

    def __init__(self, server, port, ssl_enabled, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # try to connect
        try: sock.connect((server, port))
        # try really, really hard
        except: sock.send(bytes('', 'utf-8'))

        if ssl_enabled:
            sock = ssl.wrap_socket(sock)

        sock.settimeout(timeout)

        self.ssl_enabled = ssl_enabled
        self.sock = sock

        # initialise an empty buffer
        self.buffer = b""

    def send(self, text):
        # this will contain more sanity checking later
        self.sock.send(bytes(text + '\n', 'utf-8'))

    def read(self):
        # Read new stuff to the buffer
        self.buffer += self.sock.read(4096) if self.ssl_enabled else self.sock.recv(4096)

        # prepare to return lines
        bytelines = self.buffer.split(b'\r\n')
        # don't return the (possibly) last unfinished line
        self.buffer = bytelines.pop()

        # auxiliary decoding function!
        def decode(text, encs):
            for enc in encs:
                try: return text.decode(enc)
                except: continue
            # fallback is latin-1
            return text.decode('latin-1', 'replace')

        # return the decoded lines as a list of strings!
        return [decode(byteline, ['utf-8', 'latin-1', 'cp1252'])
                for byteline in bytelines]


class IRCConnectionActor(common.Actor):

    def constructor(self, host, irc_settings):
        self.host = host
        self.irc_settings = irc_settings

    def initialize(self):
        self.wait_for_message = False
        try:
            # create a new line-buffered socket thingey
            self.irc = Socket(
                self.host['server'],
                self.host['port'],
                self.host['ssl'],
                0.01
            )
        except (socket.error, socket.herror, socket.gaierror):
            print('Connection to {}:{} failed, waiting for {} seconds...'.format(
                        self.host['server'],
                        self.host['port'],
                        self.irc_settings['reconnect_delay']))
            sleep(self.irc_settings['reconnect_delay'])
            return

        # send credentials
        self.irc.send('NICK {}'.format(self.irc_settings['nick']))
        self.irc.send('USER {0} 0 * :IRC bot {0}'.format(self.irc_settings['nick']))

        # and start listening on it
        # this is the easiest place to set-ify the channels
        # listen(inbox, parent, self.irc, self.irc_settings, set(self.host['channels']))

        self.state = {
            'nick': self.irc_settings['nick'],
            'channels': set([]),
        }

    def main_loop(self, message):
        channels = set(self.host['channels'])

        if message:
            target, source, subject, payload = message
            if subject == 'response':
                channel, content = payload
                self.irc.send(irc_parser.make_privmsg(channel, content))

        try:
            lines = self.irc.read()
        except socket.timeout:
            lines = []


        for line in lines:
            # extract the informations from the message
            user, command, arguments = irc_parser.split(line)
            nick = irc_parser.get_nick(user)

            if command == 'PING':
                self.irc.send('PONG :' + arguments[0])

            # make sure the current state of channels is updated
            if command == 'JOIN' and nick == self.state['nick']:
                self.state['channels'].add(arguments[0])
            if command == 'PART' and nick == self.state['nick']:
                self.state['channels'].discard(arguments[0])


            if command == 'PRIVMSG':
                channel, ircmessage = arguments

                ### some test codes:

                # this stops the current irc thread
                # and prevents it from being respawned
                if ircmessage and self.state['nick'] + ': stop' in ircmessage:
                    self.send(('irc', self.name, 'kill me', None))
                    self.stop()
                    return

                # this raises an exception,
                # and the thread will be respawned!
                if ircmessage and self.state['nick'] + ': except' in ircmessage:
                    raise Exception

                # this just exits the loop when it is done,
                # the thread will be respawned
                if ircmessage and self.state['nick'] + ': restart' in ircmessage:
                    self.stop()
                    return

                payload = (channel, nick, ircmessage)

                self.send(('interpretor', self.name, 'interpret', payload))
                self.send(('logger:chat', self.name, 'log', payload))
            else:
                self.send(('logger:raw', self.name, 'log', line))


        # try to join and part whatever channels applicable
        if self.state['channels'] != channels:
            joins = channels - self.state['channels']
            parts = self.state['channels'] - channels
            if joins:
                self.irc.send('JOIN {}'.format(','.join(joins)))
            if parts:
                self.irc.send('PART {}'.format(','.join(parts)))

    def terminate(self):
        self.irc.send('QUIT :termination beep blarp boop')
        self.irc.sock.close()
