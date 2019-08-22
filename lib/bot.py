from .irc import Irc
from time import sleep
import logging
import sys
import json
from random import randint, sample
import operator
from traceback import format_exception_only

class TwitchBot:
	def __init__(self, url, port, user, token, chan, prefix):
		self.irc = Irc(url, port, user, token, chan)
		self.prefix = prefix
		self.poll = {'open': False}

		with open('input/commands.json') as f:
			self.commands = json.load(f)
		
		with open('input/badges.json') as f:
			self.permissionValues = json.load(f)

		with open('input/admins.json') as f:
			self.admins = json.load(f)

	def run(self):
		while True:
			try:
				messages = self.irc.recv_messages()
				if messages:
					for msg in messages:
						if msg:
							if msg['message'].startswith(self.prefix):
								msg['message'] = msg['message'][1:]
								self.handle_command(msg)
			except (KeyboardInterrupt, SystemExit):
				raise 
			except Exception as e:
				logging.fatal(f'Exception Caught: {" ".join(format_exception_only(type(e), e))}')

	def handle_command(self, data):
		args = data['message'].split()
		user = data['user']
		badges = data['badges']
		command = args[0].lower()
		args.pop(0)
		if command in self.commands['vote']:
			self.vote(user, args)
		elif command in self.commands['createpoll']:
			if self.hasPerm(badges):
				self.createpoll(user, args)
		elif command in self.commands['endpoll']:
			if self.hasPerm(badges):
				self.endpoll(user)
		elif command in self.commands['showpoll']:
			if self.hasPerm(badges):
				self.showpoll(user, args)
		elif command in self.commands['ping']:
			if self.hasPerm(badges):
				logging.info(f'Received command PING from {user}')
				self.irc.send_channel('Pong!')
		elif command in self.commands['disconnect']:
			if user in self.admins or self.hasPerm(badges, minimum='broadcaster'):
				logging.info(f'Received command QUIT from {user}')
				self.irc.close()
				logging.debug('Disconnected from IRC server.')
				sys.exit()
		elif command in self.commands['echo']:
			if self.hasPerm(badges):
				logging.info(f'Received command ECHO from {user}')
				self.irc.send_channel(' '.join(args))
		elif command in self.commands['subtime']:
			if self.hasPerm(badges, minimum='subscriber', op=operator.eq):
				logging.info(f'Received command SUBTIME from {user}')
				# This is not exact whatsoever
				self.irc.send_private(user, f'You have been subscribed for at least {self.subTime(badges)} months.')
		elif command == 'customsay':
			if self.hasPerm(badges, minimum='vip') or user in self.admins:
				logging.info(f'Received command CUSTOMSAY from {user}')
				self.customSay(args)
		elif command == 'help':
			logging.info(f'Received command HELP from {user}')
			self.help(user, args)

	def help(self, user, args):
		if not args:
			message = ' | '.join(self.commands.keys())
		else:
			if args[0] not in self.commands:
				message = 'Error - Unknown command. USAGE: `help` or `help [command]`'
			else:
				message = 'Explanation of command' # TODO THIS
		self.irc.send_private(user, message)
#TODO: Fix the crash with colons?
	
	def customSay(self, args):
		words = ' '.join(args).lower()
		if words in self.commands['customsay'].keys():
			self.irc.send_channel(self.commands['customsay'][words])
			logging.info(f'Sent custom speech message: {words}')

	def highestPermission(self, badgeList):
		# badges.json MUST list badges in decreasing permission level order
		for badge in self.permissionValues:
			if badge in badgeList:
				logging.debug(f'Highest permission level: {badge} : {self.permissionValues[badge]}')
				return badge

	def totalPermission(self, badgeList):
		total = 0
		for badge in self.permissionValues:
			if badge in badgeList:
				total += self.permissionValues[badge]
		logging.debug(f'Total permission level: {total}')
		return total

	def subTime(self, badges):
		if 'subscriber' not in badges:
			return 0
		return badges['subscriber']

	def hasPerm(self, badges, minimum='moderator', op=operator.ge, sum=False):
		if sum:
			return op(self.totalPermission(badges), self.permissionValues[minimum])
		else:
			if op == operator.eq:
				return minimum in badges
			return op(self.permissionValues[self.highestPermission(badges)], self.permissionValues[minimum])

	def createpoll(self, user, args):
		# Usage: createpoll (auto | json mimicking input/poll.json)
		try:
			if not args:
				# The user failed to give any arguments
				return self.irc.send_private(user, f'Usage: {self.prefix}createpoll auto OR {self.prefix}createpoll [json string similar to poll.json]')
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
		displayList = {game : count for game, count in zip(self.poll['choices'], games.values())}
		ranking = {}
		for game, count in displayList.items():
			if count not in ranking:
				ranking[count] = []
			ranking[count].append(game)
		winner = sample(ranking[max(ranking.keys())], 1)[0]
		displayString = f'Winner: {winner} --- '
		rankingString = ''
		for key in displayList:
			rankingString += f' | {key}: {displayList[key]}'
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