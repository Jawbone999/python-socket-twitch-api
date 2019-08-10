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
Within the `input` folder, there are a few files which allow for bot configuration.

### `commands.json`
In this folder holds all the commands and their aliases. To add an alias, simply add to the list of strings under the desired command. Do **not** edit the main command name unless you know what you're doing.

### `admins.json`
While the bot prevents non-moderators from using every command, you can allow specific users full access using this file. Simply add their name to the list.

### `poll.json`
This poll is used if the _createpoll_ command is run with the argument _auto_. Change it how you like.

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

You can also edit the `run.bat` file and use that.
