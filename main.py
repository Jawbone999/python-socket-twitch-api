"""
A public example of the API's functionality using a Twitch Bot.
"""
from lib.bot import TwitchBot
from input import config

# Set up logging:

# Create bot object using tuple unpacking
myBot = TwitchBot(*config.DATA)

myBot.run()