Hotswapping of threads
======================

The IRC connection threads can send messages about `'reload irc_connection'` to
the IRC thread, in which a flag may be raised which indicates that during the
next reconnect, a reload also should be performed. (May reload be done
direction without affecting the running functions? Maybe works.) It's
unnecessary to reconnect automagically during a reload, because if the bot
fills a vital role in some other channel (this gets awkward on multiple
channels on the same network...) it's a good idea to decide whether to update
and whether to reconnect separately.

If the message instead asks for `'reload irc'`, the IRC thread must save it's
children, send them in a message to master, which restarts the IRC thread and
gives it its children back. This may be done either in an argument or via a
message of some sort. The IRC process should preferably get to use the same
inbox as before, right?

If the message is `'reload master'`, have fun.

If the message is `'reload logger'`, the IRC thread should send a message to
logger about logger having to save whatever it's doing and then ask to be
restarted, after which it should be restarted *with the same inbox as before*!
This is because things shouldn't disappear into cyberspace while it restarts.
When it gets back online, it just continues from where it left off.

If the message is `'reload memery'`, the IRC thread should send a message to
memery about memery asking to be restarted, and then memery just gets to die
when the current computations are done. The new memery can just as well use the
same inbox as before, as long as the old one doesn't get to read stuff from it
before it dies.

Important points:

 *  No thread may kill its children! A thread may only ask its children to stop
 or restart, but the children themselves get the final say because they know
 more about the situation they're in.

 *  Some threads must, when they are restarted, continue to use their old
 inbox. This is to avoid losing information. Is this really important though?

 *  To be able to reload IRC without losing connections it's required that IRC
 saves its children so the next IRC may inherit them without having to start
 new one.

