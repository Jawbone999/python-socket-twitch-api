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

   USER = *Your bot's Twitch account name*

   PASS = *oauth:1k4j4njnuh2o41jo1j4jjj11io23jo (not this exactly, but what you received earlier)*

   CHAN = *Twitch channel you want the bot to chat in*

__NOTE: Your Twitch bot must be [verified](https://dev.twitch.tv/limit-increase) to make full use of this API__

# Configuring your bot
Within `bot/data`, there are a few files which allow for bot configuration. All of these may be modified through the bot in chat, or directly through a text editor.

### `command_aliases.json`
In this folder holds all the commands and their aliases. To add an alias, simply add to the list of strings under the desired command. Do **not** edit the main command key unless you know what you're doing.

One exception to the standard format within this file is the key `customsay`. Executing the chat command `[PREFIX]customsay [KEY]` will make the bot reply with `[VALUE]`. 

This file has some pre-built aliases within it, but it can be removed at one's discretion.

### `admins.json`
While the bot prevents non-moderators from using every command, you can allow specific users full access using this file. Simply add their name to the list.

### `badges.json`
This file assigns numerical value to each badge level. It is only used when calculating "Total permission level". So, for example, someone who is a VIP sub has the same total permission level as a moderator by default. This metric is not used anywhere by default in the bot, however.

## Py File Modifications
You can also modify the source code, though it is recommended you know what you're doing. Below are some places to look for different modifications.

#### Add commands
Inside `bot.py`, the function `handle_command` has an if statement checking for each command.

#### Change logging level
Inside `main.py`, change the logging configuration level.

#### Edit permission levels
Inside `bot.py`, the function `handle_command` performs all permission checks before running a command.

# Running your bot
Once you're happy with the configurations, simply navigate to the directory of `main.py` and run `python main.py`.

If you're not used to command line, edit `setup.bat` and `run.bat`, then run those two files in that order.

# Bot Commands

## Ping
A simple test to see that the bot is connected to the chat.
Usage: `$ping`
Response: `Pong!`

# Echo
Make the bot say exactly what you say.
Usage: `$echo {MESSAGE}`
Response: `{MESSAGE}`

# ReplyTo
Make the bot reply to any specific chat message whenever it appears.
Usage: `$replyto {MESSAGE} | {REPLY}`
Response: None
Later...
User: `{MESSAGE}`
Bot: `{REPLY}`

# AutoMessage
The bot will periodically send this message every _ minutes.
Usage: `$automessage {MESSAGE} | {MINUTES}`
Reply: None
{MINUTES} Later...
Bot: `{MESSAGE}`
