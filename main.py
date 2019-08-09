"""
A public example of the API's functionality using a Twitch Bot.
"""
from lib.bot import TwitchBot
from input import config
import logging

# Set up logging:
logging.basicConfig(filename=config.logFile, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
# Create bot object using tuple unpacking
myBot = TwitchBot(*config.DATA)

myBot.run()