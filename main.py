"""
A public example of the API's functionality using a Twitch Bot.
"""
from sys import exit
from input import config
import logging
from lib import TwitchBot
from traceback import format_exception_only

logging.basicConfig(filename=config.LOGFILE, level=config.LOGLEVEL, format='%(asctime)s %(levelname)s: %(message)s')
logging.info('Starting bot...')
myBot = TwitchBot(*config.DATA)
try:
    logging.info('Running bot...')
    myBot.run()
except(KeyboardInterrupt, SystemExit):
    logging.info('Received EXIT signal, exiting program...')
except Exception as e:
    logging.fatal(f'Program crashed: {" ".join(format_exception_only(type(e), e))}')
finally:
    myBot.stop()
    logging.info('Program Ended')
    exit()