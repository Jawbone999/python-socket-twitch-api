from .irc import Irc
from time import sleep
import logging
import sys
import json
from random import randint

class TwitchBot:
	def __init__(self, url, port, user, token, chan, prefix):
		self.irc = Irc(url, port, user, token, chan)
		self.prefix = prefix
		self.poll = {'open': False}
		with open('lib/commands.json') as f:
			self.commands = json.load(f)
		
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
		if command in self.commands['vote']:
			self.vote(user, args)
		elif command in self.commands['createpoll']:
			if data['mod']:
				self.createpoll(user, args)
		elif command in self.commands['endpoll']:
			if data['mod']:
				self.endpoll(user)
		elif command in self.commands['showpoll']:
			if data['mod']:
				self.showpoll(user, args)
		elif command in self.commands['ping']:
			if data['mod']:
				logging.info(f'Received command PING from moderator {user}')
				self.irc.send_channel('Pong!')
		elif command in self.commands['disconnect']:
			if data['mod']:
				logging.info(f'Received command QUIT from moderator {user}')
				self.irc.close()
				logging.debug('Disconnected from IRC server.')
				sys.exit()
		elif command in self.commands['echo']:
			if data['mod']:
				logging.info(f'Received command ECHO from moderator {user}')
				self.irc.send_channel(' '.join(args))
			
	def createpoll(self, user, args):
		# Usage: createpoll (auto | json mimicking input/poll.json)
		try:
			if not args:
				# The user failed to give any arguments
				return self.irc.send_private(user, f'Usage: {self.prefix}createpoll auto or ADD other stuff')
			if args[0].lower() == 'auto':
				# Generate a poll using the input file
				with open('input/poll.json') as f:
					autoPoll = json.load(f)
			else:
				# Rejoin the args and generate a poll using them
				args = ' '.join(args)
				autoPoll = json.loads(args)
			self.poll['title'] = autoPoll['title']
			self.poll['random'] = autoPoll['random']
			self.poll['votes'] = {}
			self.poll['choices'] = autoPoll['choices']
			if not self.poll['choices']:
				raise Exception('No options in poll')
			self.poll['open'] = True
			logging.info(f'Created poll by {user}: {self.poll}')
		except:
			logging.error(f'Failed to create poll by {user}')
			self.irc.send_private(user, 'Error creating poll - check your arguments!')
	
	def showpoll(self, user, args):
		# Usage: $showpoll
		if self.poll['open']:
			displayString = self.poll['title'] + f' ({self.prefix}vote) - Choices: '
			displayString += ' | '.join([f'{num+1}. {opt}' for num, opt in enumerate(self.poll['choices'])])
			if self.poll['random']:
				displayString += f' -- You can also throw your vote away using {self.prefix}vote random'
			self.irc.send_channel(displayString)
		else:
			self.irc.send_private(user, "Error - there are no polls in progress!")

	def endpoll(self, user):
		# Usage: $endpoll
		if not self.poll['open']:
			# There's no created poll whatsoever
			logging.debug(f'Failed to end poll as requested by {user} - no poll exists!')
			return self.irc.send_private(user, "Cannot end a poll that doesn't exist!")
		# Close the poll
		self.poll['open'] = False
		games = {i : 0 for i in range(len(self.poll['choices']))}
		for choice in self.poll['votes'].values():
			games[choice - 1] += 1
		displayList = {count : game for game, count in zip(self.poll['choices'], games.values())}
		winner = displayList[max(displayList)]
		displayString = f'Winner: {winner} --- '
		rankingString = '' # Problem: Have to unreverse displayList kv pairs because they are overlapping keys for votes
		# Need to get all tying top picks and randomly pick the winner in case of a tie
		# Basically, get list of top scorers, then do that random pick from list function on it
		# So if no ties, randomly samples from single item list which works fine for this
		for key in displayList:
			rankingString += f' | {displayList[key]}: {key}'
		displayString += rankingString[3:]
		self.irc.send_channel(displayString)


		
	def vote(self, user, args):
		if not args:
			return self.irc.send_private(user, 'Error casting vote - please send a choice!')
		pick = args[0].lower()
		if self.poll['open']:
			if pick == 'random':
				if self.poll['random']:
					pick = randint(1, len(self.poll['choices']))
				else:
					self.irc.send_private(user, 'Error casting vote - random voting is not allowed for this poll.')
					return
			try:
				pick = int(pick)
				if pick <= 0 or pick > len(self.poll['choices']):
					raise Exception('Invalid vote value')
				self.poll['votes'][user] = pick
			except:
				self.irc.send_private(user, 'Error casting vote - please send a valid choice!')
		else:
			self.irc.send_private(user, 'Error - there are no polls in progress!')