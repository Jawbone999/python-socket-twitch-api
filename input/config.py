# Remove this:
import input.config_test as c

# The IRC Server URL
URL = c.URL

# Port for the IRC Server
PORT = c.PORT

# The name of the bot
USER = c.USER

# The bots Oauth token
PASS = c.PASS

# The channel to moderate
CHAN = c.CHAN

# Bot command prefix
PREFIX = '$'

# Tuple holding bot info (just a shortcut)
DATA = URL, PORT, USER, PASS, CHAN, PREFIX

# File to append log data to
logFile = c.logFile