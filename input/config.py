# Remove this:
import input.config_test as c

# The IRC Server URL
URL = 'irc.twitch.tv'

# Port for the IRC Server
PORT = 6667

# The name of the bot
USER = 'BOT USERNAME'

# The bots Oauth token
PASS = 'OAUTH TOKEN'

# The channel to moderate
CHAN = 'CHANNEL NAME'

# Bot command prefix
PREFIX = '$'

# Tuple holding bot info (just a shortcut)
DATA = URL, PORT, USER, PASS, CHAN, PREFIX

# File to append log data to
logFile ='logs/TwitchBotLogs.log'