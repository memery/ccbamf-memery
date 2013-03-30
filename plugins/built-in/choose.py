import common
import random

def run(nick, message, cmd_prefix):
    if message.split(None, 1)[0] != cmd_prefix + 'choose':
        return None

    arg = message.lstrip(cmd_prefix + 'choose').strip()

    if not arg:
        return '{}: nothing to choose from'.format(nick)

    result = random.choice(arg.strip().split(' | ')).strip()
    return '{}: {}'.format(nick, result)
