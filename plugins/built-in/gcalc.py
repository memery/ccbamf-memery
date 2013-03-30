import codecs, re
import common

def help():
    return {'authors':     ['kqr', 'slaeshjag', 'nycz'],
            'years':       ['2012', '2013'],
            'version':     '1.0',
            'description': 'Interface till Google calc-API:et.',
            'argument':    '<uttryck>'}

def run(nick, message, cmd_prefix):
    arg = common.get_plugin_argument(message, cmd_prefix, 'c')
    if arg is None:
        return None
    return "{0}: {1}".format(nick, calc(arg))

def calc(args):
    content = common.read_url("http://www.google.com/ig/calculator?h=en&q=", args)

    lhs = sanitise(re.search(r'lhs: "(.*?)"', content).group(1))
    rhs = sanitise(re.search(r'rhs: "(.*?)"', content).group(1))
    err = sanitise(re.search(r'error: "(.*?)"', content).group(1))

    if err:
        return "Ogiltigt uttryck enligt Google! (Felkod: {0})".format(err)
    else:
        return "{0} = {1}".format(lhs, rhs)


def sanitise(text):
    # nbsp ugly shit hack
    text = text.replace('\xa0', '')
    text = common.unescape_html(codecs.getdecoder('unicode_escape')(text)[0])
    # Note the special ⁄-char (not a regular slash) between </sup> and <sub>
    text = re.sub(r'<sup>(\d+)</sup>⁄<sub>(\d+)</sub>', r' \1/\2', text)
    return text.replace('<sup>', '^(').replace('</sup>',')').replace('( ', '(')

