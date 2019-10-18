###################################
# Change the four variables below #
###################################

# The name of the bot
USER = 'BOT USERNAME'

# The bots Oauth token
PASS = 'OAUTH TOKEN'

# The channel to moderate
CHAN = 'CHANNEL NAME'

# Bot command prefix
PREFIX = '$'

###################################################
# The variables below do not *need* to be changed #
###################################################

# The IRC Server URL
URL = 'irc.twitch.tv'

# Port for the IRC Server
PORT = 6667

# Logging Level Options:
# CRITICAL
# ERROR
# WARNING
# INFO
# DEBUG
LOGLEVEL = "DEBUG"

# File which holds the bot logs
LOGFILE ='TwitchBotLogs.log'

# Tuple holding bot info (just a shortcut)
DATA = LOGFILE, LOGLEVEL, URL, PORT, USER, PASS, CHAN, PREFIX