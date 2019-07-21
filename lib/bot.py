from .irc import Irc
from time import sleep
class TwitchBot:
	def __init__(self, url, port, user, token, chan):
		self.irc = Irc(url, port, user, token, chan)

	def run(self):
		self.irc.send('PRIVMSG testing')
		while True:
			messages = self.irc.recv_messages()
			if messages:
				for msg in messages:
					self.irc.parse_message(msg)
