from .irc import Irc
from time import sleep
import logging
import sys

class TwitchBot:
	def __init__(self, url, port, user, token, chan, prefix):
		self.irc = Irc(url, port, user, token, chan)
		self.prefix = prefix
		self.poll = {}
		
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
		user = data['user']
		command = args[0].lower()
		args.pop(0)
		if command == 'vote':
			self.vote(user, args)
		elif command == 'createpoll':
			if data['mod']:
				self.createpoll(user, args)
		elif command == 'endpoll':
			if data['mod']:
				self.endpoll(user)
		elif command == 'ping':
			if data['mod']:
				logging.info(f'Received command PING from moderator {user}')
				self.irc.send_channel('Pong!')
		elif command == 'quit' or command == 'leave' or command == 'exit':
			if data['mod']:
				logging.info(f'Received command QUIT from moderator {user}')
				self.irc.close()
				logging.debug('Disconnected from IRC server.')
				sys.exit()
			
	def createpoll(self, user, args):
		# Usage: createpoll (auto | TITLE,RANDOM,CHOICE1,CHOICE2,CHOICE3)
		self.poll = {
			'title': '',
			'random': True,
			'choices': []
		}


    
	def endpoll(self, user):
		pass

	def vote(self, user, args):
		pass