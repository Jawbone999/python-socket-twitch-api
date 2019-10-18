from traceback import format_exception_only
from bot import TwitchBot
from config_test import DATA
from sys import exit
import logging

logFile, logLevel, *botData = DATA
logging.basicConfig(filename=logFile, level=logLevel, format='%(asctime)s %(levelname)s: %(message)s')

myBot = TwitchBot(*botData)

try:
    logging.debug('Starting bot...')
    myBot.run()
except(KeyboardInterrupt, SystemExit):
    logging.info('Received EXIT signal, exiting program...')
except Exception as e:
    logging.fatal(f'Program crashed: {" ".join(format_exception_only(type(e), e))}')
finally:
    logging.debug('Stopping bot...')
    exit()