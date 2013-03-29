Message specification
=======================

Protocol agnostic messages need the following elements.

 1. `source`: where did the message come from? This corresponds to channels in
 IRC and a conversation ID of some kind in MSN.

 2. `author`: who wrote this message? This is for example nicks in IRC, and
 handles in MSN.

 3. `content`: the actual message.

This is very straight-forward, and ignores most capabilities of most protocols,
but it suffices for the time being. It could be useful to have some kind of
presence tracking in protocols that support it, for example MSN, IRC and XMPP.
In IRC, presence tracking is done via joins/parts/quits. The related protocol
agnostic message needs the following.

 1. `source`: where did the signal come from?

 2. `author`: who made this signal relevant?

 3. `present`: is the author still present? (An IRC join sets this to True, a
 part or quit sets it to False.)

This is not completely protocol agnostic (some protocols don't support presence
tracking, but see how much I care. Most protocols do support it.)

One problem with presence tracking in IRC is that the IRC parser must convert
quit messages to part messages in all the channels the parting user was online,
to avoid making a leaky abstraction. This may make everything a lot more
complicated, because the IRC parser then needs to know something about the
state of the IRC network... It could be a good idea to avoid presence tracking
until a Clever Solution™ exists.

