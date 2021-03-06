#message    =  [ ":" prefix SPACE ] command [ params ] crlf
#prefix     =  servername / ( nickname [ [ "!" user ] "@" host ] )
#command    =  1*letter / 3digit
#params     =  *14( SPACE middle ) [ SPACE ":" trailing ]
#           =/ 14( SPACE middle ) [ SPACE [ ":" ] trailing ]
#
#nospcrlfcl =  %x01-09 / %x0B-0C / %x0E-1F / %x21-39 / %x3B-FF
#                ; any octet except NUL, CR, LF, " " and ":"
#middle     =  nospcrlfcl *( ":" / nospcrlfcl )
#trailing   =  *( ":" / " " / nospcrlfcl )
#
#SPACE      =  %x20        ; space character
#crlf       =  %x0D %x0A   ; "carriage return" "linefeed"

import re

def split(text):
    mainregex = re.compile(r"""
    (:
        (?P<prefix>
            (?P<nickuserhost>
                \S+?        # nick
                ((!\S+?)?   # user
                @\S+        # host
                )?
            ) |
            (?P<servername>\S+)
        )
        \                   # space
    )?
    (?P<command> ([A-Za-z]+|[0-9]{3}))
    (
        (
            \               # space
            (?P<params> [^ :][^ ]*)
        )*
        (
            \ :             # space colon
            (?P<last>.*)
        )*
    )?
    $""", re.VERBOSE)

    out = mainregex.match(text)

    # pulled these out so they give more useful error
    # messages than "something went wrong"
    user = out.group('nickuserhost')
    command = out.group('command')
    arguments = out.group('params').split(' ') if out.group('params') else []
    if out.group('last'): arguments.append(out.group('last'))

    return user, command, arguments


def get_nick(user):
    """ Returns the nick part of a user mask (nick!user@host) """
    if not user:
        return None
    else:
        return re.sub(r'^~?(\S+?)!.*$', '\\1', user)


def make_privmsg(channel, content):
    return 'PRIVMSG {} :{}'.format(channel, content)
