from .irc import Irc
from time import sleep
import logging

class TwitchBot:
	def __init__(self, url, port, user, token, chan, prefix):
		self.irc = Irc(url, port, user, token, chan)
		self.prefix = prefix

	def run(self):
		while True:
			messages = self.irc.recv_messages()
			if messages:
				for msg in messages:
					if msg:
						if msg['message'].startswith(self.prefix):
							msg['message'] = msg['message'][1:]
							self.handle_command(msg)

	def handle_command(self, data):
		args = data['message'].split()
		command = args[0]
		args = args[1:]
		if command.lower() == 'vote':
			self.vote(user, args)
		elif command.lower() == 'createpoll':
			if data['mod']:
				self.createpoll(data)
		elif command.lower() == 'endpoll':
			if data['mod']:
				self.endpoll()
		elif command.lower() == 'ping':
			if data['mod']:
				logging.info(f'Received command PING from moderator {data['user']}')
				self.irc.send_channel('Pong!')
		elif command.lower() == 'quit':
			if data['mod']:
				logging.info(f'Received command QUIT from moderator {data['user']}')
				self.irc.sock.close()
				logging.debug('Disconnected from IRC server.')
				sys.exit()
			
	def createpoll(self, data):
		pass
    
	def endpoll(self):
		pass

	def vote(self, data):
		pass