import common
import random

def run(nick, message, cmd_prefix):
    arg = common.get_plugin_argument(message, cmd_prefix, 'choose')
    if arg is None:
        return

    if not arg:
        return '{}: nothing to choose from'.format(nick)

    result = random.choice(arg.strip().split(' | ')).strip()
    return '{}: {}'.format(nick, result)
