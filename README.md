# Bot
This is how it has to work:

=== Yours chat with bot ===

User: /init

Bot: Your new handle (1): `JajhO0vZr-DqoagPAQ7ZzH19kPdYi_w86mR47Kb1IJWwYWTFSHMOOiFjvfZdaf-Y` # first handle

U: /init

B: Your new handle (2): `5LEB5kiJPKRzbfL_wRvzWaIi2zQGiKYqmpDHkM4i4I4QgDVpK1GNUsm5cQtaIFgK` # second handle

U: /from 2 # this means that all your messages (until next "/from" command) will be signed with your second handle

U: /send IIPHDfGRCZKzvBdqoAJnhvPtqzsdHvWw9tLpIdoZBL87zFaW2SPh3doMZxJEv04- # send a message to user with given handle

B: Now send me message which will be resent to destination user

U: \*some message\*

=== Chat of bot and "destination" user ===

B: **From:** `5LEB5kiJPKRzbfL_wRvzWaIi2zQGiKYqmpDHkM4i4I4QgDVpK1GNUsm5cQtaIFgK`

\*some message which you have sent to bot\*

U-2: /send ...

_or_

U-2 replies to this message. Bot will reply to U message -- with given by U-2 \*some message\*
