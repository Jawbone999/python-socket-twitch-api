# Python Socket Twitch API
A socket api for Twitch IRC servers.

# Usage
To use this bot, you must have Python 3.6+ installed. Run `pip install -r requirements.txt` to install all required modules.

To allow for use with Twitch, you must edit `config.py` to contain all your bot info. Obtaining this information is outlined below.

# Creating a Twitch Bot
To create a bot with which you may interface with Twitch, you must do the following things:

- Create a new Twitch account under the bot's name.
- Head to the [Twitch Chat OAuth Password Generator](twitchapps.com/tmi) and click generate. Ensure that you are logged in as the bot, then click authorize.
- You should now see an OAuth token that looks something like this:

   __oauth:1k4j4njnuh2o41jo1j4jjj11io23jo__

   Save this token somewhere secure, as it acts as a password to your bot account.

- You are now ready to fill in the `config.py` file.

   __USER__ = *Your bot's Twitch account name*

   __PASS__ = *Your bot's OAuth token*

   __CHAN__ = *The Twitch channel you want the bot to chat in*

   __PREFIX__ = *Any single character you wish to signify a command in chat (ex: !)*

__NOTE: Your Twitch bot must be [verified](https://dev.twitch.tv/limit-increase) to make full use of this API__

   You can also set a value for __LOGLEVEL__:
      - DEBUG: Records pretty much all bot connection information.
      - INFO: Records all command executions.
      - ERROR: Records connection losses.
      - CRITICAL: Records bot crashes.

   __Note: The default level is INFO. All levels also record those below them.__

# Configuring your bot
This script interacts with a number of `.json` files to perform its functions. Below are the descriptions for each file.

### `poll.json`
This file holds the default poll used when the user runs >poll create auto (read **Commands** below for more information.)
All polls must take the form of a dictionary with:
   - title: A string for the name of the poll
   - choices: A list of strings for options in the poll
   - random: A boolean to allow for randomize votes

### `bot/data/admins.json`
This file holds a list of bot admins. This list must be edited manually, and by default is empty.
If you want to give someone full access to the bot, add their Twitch username to this list.

### `bot/data/auto_messages.json`
This file contains a dictionary of messages to send periodically. The keys are messages, and their values contain the number of minutes between messages, and a dummy variable to track the last time the message was sent. This should always be zero.
The file can be edited manually, or through a bot command.

__Note: These periodic messages are only sent when an event in the chat is detected. This is likely a message, or the automated PING Twitch sends all clients every five minutes. So, times are not exact.__

### `bot/data/auto_replies.json`
This file contains a dictionary of messages the bot should reply to.
The key is the message to look for in chat, and the value is what the bot says in response.
This file can be edited manually, or through a command.

### `bot/data/commands.json`
This file contains the names of command functions as keys, and their chat aliases as listed values.
If you wish to add a command alias, simply add it to one of the lists manually.

### bot/data/custom_commands.json`
Similar to `auto_replies.json`, this makes the bot reply to single words, but only if they are entered as a command (prepended with the prefix).
It can be edited through commands or manually.

# Commands
The bot comes with a number of commands.
Examples of the commands will use `$` as the prefix.

### Ping
Used for testing if the bot is present in the chat.

User: `$ping`

Bot: `Pong!`

### Disconnect
Disconnects the bot from the IRC server and shuts the script down.

User: `$disconnect`

*Bot disconnects, and is no longer running.*

### Echo
The bot will repeat whatever is said to it.

User: `$echo I am a cool bot!`

Bot: `I am a cool bot!`

### Poll
Create/Start, End, or Display a poll in chat.

__Create:__
User: `$poll create auto`

*Bot sends the poll display string in chat.*

OR

User: `$poll create {"title": "Pick the game I'm going to play!","choices": ["Game X","Game Y","Game Z"],"random": false}`

*Bot sends the poll display string in chat.*

__End:__
User: `$poll end`

*Bot sends the poll results in chat.*

__Display:__
User: `$poll display`

*Bot sends the poll display string in chat.*

### Vote
Vote for an option in the poll.

User: *$vote 3*

*If there are at least three options on the poll, the vote is recorded.*

### Reply
Create, Delete, or Display automated replies.

__Create:__
User: `$reply create This bot sucks! | No u`

*Later...*

User: `This bot sucks!`

Bot: `No u`

__Delete:__
*Assume `This bot rocks!` is another automated reply*

User: `$reply delete This bot sucks! | This bot rocks!`

*Later...*

User: `This bot sucks!`

*Bot does not reply.*

User: `This bot rocks!`

*Bot does not reply.*

__Display:__
User: `$reply display`

*Bot sends all reply: response objects in a private message.*

### Schedule
Allows the creation, deletion, and display of scheduled automated messages.

__Create:__
User: `$schedule create Remember to drink water! | 5`

*Five minutes later...*

Bot: `Remember to drink water!`

__Delete:__
User: `$schedule delete Remember to drink water!`

*Five minutes later...*

*Bot does not send automated message.*

__Display:__
User: `$schedule display`

*Bot privately messages automated message dictionary.*

### Command
Create, delete, and display custom commands.

__Create:__
User: `$command create setup Computer, keyboard, and mouse.`

*Later...*

User: `$setup`

Bot: `Computer, keyboard, and mouse.`

__Delete:__
User: `$command delete setup`

*Later...*

User: `$setup`

*Bot does not reply.*

__Display:__
User: `$command display`

*Bot sends commands and replies privately to the user.*