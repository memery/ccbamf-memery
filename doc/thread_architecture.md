Process/thread architecture
===========================

    Master (1)
      |
      +--- IRC (2)
      |     |
      |     +--- Connection to Efnet
      |     +--- Connection to gfu
      |
      +--- Logger (3)
      |
      +--- memery (4)
             |
             +--- Title print for a slow web page
             +--- Long markov-chain style sentence generation
             +--- Quick .choose-calculation

The Master thread spawns one IRC-thread which is responsible for the IRC
protocol, one logger which accepts messages and logs them appropriately, and
one memery which contains all the behaviours of the bot.

The memery thread should be as protocol agnostic as possible. Administrative
functions related to IRC (stfu, op and so on) should probably be in the
connection threads. The connection threads will propagate their input to the
IRC process, which parses IRC messages into protocol agnostic internal chat
messages according to `ircparser` and then passes the messages on to memery and
logger.

The IRC thread has total responsibility over the connection threads, and
therefore has to restart them when they encounter errors they can't solve on
their own.

The logger thread receives protocol agnostic messages and logs them (here's a
problem -- logger won't be able to log OPs and stfu's and such things if logger
is protocol agnostic. AAaaaa!)

The memery thread, just like the logger thread, receives protocol agnostic
messages and possibly returns an answer. The memery thread may also send
messages on its own, which is the case with markov and similar things.

The IRC thread receives protocol agnostic messages, converts them with
ircparser and dispatches them to the correct connection process, which receives
it and jams it down the socket.

If logger is restarted by master, it has to be communicated to IRC (I think?)
so it can refresh itself with the new address to logger. If memery is
restarted, memery must be responsible for closing its threads (or does it?) and
then a new address must be communicated to IRC.

