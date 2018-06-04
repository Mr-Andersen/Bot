# Bot
This bot is created mostly for channels' admins who don't want to put their true Telegram handle in channel header neither create their own bot for feedback:

Commands:

/new - generates new anonymous handle (can be used many times)

/del <handle> - disable handle. This won't delete a handle from database, but user won't receive letters sent on this handle

/from <handle> - set handle as default for writing letters

/list - list all user's handles

/send <handle> - send message to handle. Bot will offer you to send message next

/help - short help

/cancel - cancel current operation


*and*

When user receives a letter, he can reply to it with some <answer message> - and bot will send a letter to author of original message, signed as handle, which was put in "To" field (Wow, feature!)
