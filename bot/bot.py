from .irc import TwitchIrc
from time import sleep
import logging
from sys import exit
import json
from random import randint, sample
import operator
from traceback import format_exception_only
import emoji
from datetime import datetime, timedelta

class TwitchBot:
	"""
	This is a class for receiving and executing commands through Twitch chat.

	Attributes:
		irc (TwitchIrc): The IRC connection to the Twitch server.
		prefix (string): The prefix that all bot commands begin with.
		current_poll (dict): The data for the currently running poll. This data includes:
			title (string): The title of the poll.
			choices (list): A list of strings representing options on the poll.
			random (boolean): Whether or not randomized/arbitrary voting is allowed (just for fun).
		start_time (datetime): The time at which the bot is started. Used for automated messaging.
		permission_values (dict): The numeric value assigned to different Twitch badges for easy comparison.
		command_map (dict): A dictionary with command names and their corresponding functions. Acts as a switch statement for evaluating command messages.
		admins (list): A list of users who do not need badge permissions to control the bot.
		custom_commands 




	"""

	def __init__(self, url, port, user, token, chan, prefix):
		self.irc = TwitchIrc(url, port, user, token, chan)
		self.irc.connect()

		self.prefix = prefix
		self.current_poll = {'open': False}
		self.start_time = datetime.now()

		self.read_data_files()
		
		self.permission_values = {
			'broadcaster': 4,
			'moderator': 3,
			'vip': 2,
			'subscriber': 1
		}

	def generate_command_map(self, commands):
		self.command_map = {}
		for command, aliases in commands.items():
			for alias in aliases:
				self.command_map[alias] = eval(f'self.{command}')

	def read_data_files(self):
		with open('bot/data/admins.json') as f:
			self.admins = json.load(f)

		with open('bot/data/custom_commands.json') as f:
			self.custom_commands = json.load(f)

		with open('bot/data/auto_replies.json') as f:
			self.auto_replies = json.load(f)
		
		with open('bot/data/auto_messages.json') as f:
			self.autoMessages = json.load(f)

		with open('bot/data/command_aliases.json') as f:
			commands = json.load(f)
		self.generate_command_map(commands)

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
							elif msg['message'] in self.autoMessages:
								logging.info(f'Replying to {msg["message"]}...')
								self.irc.send_channel(self.autoMessages[msg['message']])
				minsPassed = round((datetime.now() - self.start_time).total_seconds() / 60)
				for auto_message, timeInfo in self.autoMessages.items():
					if minsPassed % timeInfo['Timer'] == 0 and minsPassed - timeInfo['LastTime'] >= timeInfo['Timer']:
						timeInfo['LastTime'] = minsPassed
						self.irc.send_channel(auto_message)
			except (KeyboardInterrupt, SystemExit):
				raise
			except Exception as e:
				logging.fatal(f'Exception Caught: {" ".join(format_exception_only(type(e), e))}')

	def handle_command(self, data):
		"""

		"""
		args = data['message'].split()
		user = data['user']
		badges = data['badges']
		command = args.pop(0).lower()

		self.command_map[command](user, badges, args)


	def ping(self, user, badges, args):
		if self.has_permission(user, badges):
			logging.info(f'Received command PING from {user}')
			self.irc.send_channel('Pong!')
		else:
			self.irc.send_private(user, 'PermissionError')
	
	def disconnect(self, user, badges, args):
		if self.has_permission(user, badges):
			logging.info(f'Received command DISCONNECT from {user}')
			self.irc.close()
			logging.debug('Disconnected from IRC Server')
			exit()
		else:
			self.irc.send_private(user, 'PermissionError')

	def poll(self, user, badges, args):
		if not args:
			return self.irc.send_private(user, f'NoArgError')
		function = args.pop(0).lower()
		if function == 'create':
			self.create_poll(user, badges, args)
		elif function == 'end':
			self.end_poll(user, badges)
		elif function == 'display':
			self.display_poll(user, badges)
		else:
			self.irc.send_private(user, 'BadArgError')

	def create_poll(self, user, badges, args):
		if not self.has_permission(user, badges):
			return self.irc.send_private(user, 'PermissionError')

		if not args:
				# The user failed to give any arguments
				return self.irc.send_private(user, f'NoArgError')

		try:
			if args[0].lower() == 'auto':
				# Generate a poll using the input file
				with open('poll.json') as f:
					new_poll = json.load(f)
			else:
				# Rejoin the args and generate a poll using them
				args = ' '.join(args)
				new_poll = json.loads(args)
			self.current_poll['title'] = new_poll['title']
			self.current_poll['random'] = new_poll['random']
			self.current_poll['votes'] = {}
			self.current_poll['choices'] = new_poll['choices']
			if not self.current_poll['choices']:
				raise Exception('No options in poll')
			self.current_poll['open'] = True
			logging.info(f'Created poll by {user}: {self.current_poll}')
		except:
			logging.error(f'Failed to create poll by {user}')
			self.irc.send_private(user, 'Error creating poll - check your arguments!')
	
	def end_poll(self, user, badges):
		if not self.has_permission(user, badges):
			return self.irc.send_private(user, 'PermissionError')

		if not self.current_poll['open']:
			# There is not an open poll to end
			return self.irc.send_private(user, "BadStateError")

		# Close the poll
		self.current_poll['open'] = False
		games = {i : 0 for i in range(len(self.current_poll['choices']))}
		for choice in self.current_poll['votes'].values():
			games[choice - 1] += 1
		displayList = {game : count for game, count in zip(self.current_poll['choices'], games.values())}
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

	def display_poll(self, user, badges):
		if not self.has_permission(user, badges, minimum='subscriber'):
			return self.irc.send_private(user, 'PermissionError')

		if not self.current_poll['open']:
			return self.irc.send_private(user, 'BadStateError')

		displayString = self.current_poll['title'] + f' ({self.prefix}vote) - Choices: '
		displayString += ' | '.join([f'{num+1}. {opt}' for num, opt in enumerate(self.current_poll['choices'])])
		if self.current_poll['random']:
			displayString += f' -- You can also throw your vote away using {self.prefix}vote random'

		self.irc.send_channel(displayString)

	def echo(self, user, badges, args):
		if not self.has_permission(user, badges):
			return self.irc.send_private(user, 'PermissionError')
		
		if not args:
			return self.irc.send_private(user, 'NoArgsError')
		
		logging.info(f'Received command ECHO from {user}: "{emoji.demojize(" ".join(args))}"')
		message = ' '.join(args)
		self.irc.send_channel(message)

	def custom_reply(self, user, args):
		logging.info(f'Received command REPLYTO from {user}')
		args = (' '.join(args)).split(' | ')
		if len(args) != 2:
			self.irc.send_private(user, f'Error - REPLYTO requires two | separated arguments.')
		else:
			self.auto_replies[args[0]] = args[1]
			with open('bot/data/auto_replies.json', 'w') as f:
				json.dump(self.auto_replies, f)

	def has_permission(self, user, badges, minimum='moderator'):
		if user in self.admins:
			return True
		perms = []
		for badge in badges:
			perms.append(self.permission_values.get(badge, -1))
		return max(perms) >= self.permission_values[minimum]

	
	def vote(self, user, args):
		logging.info(f'Received command VOTE from {user}')
		if not args:
			return self.irc.send_private(user, 'Error casting vote - please send a choice!')
		pick = args[0].lower()
		if self.current_poll['open']:
			if pick == 'random':
				if self.current_poll['random']:
					pick = randint(1, len(self.current_poll['choices']))
				else:
					self.irc.send_private(user, 'Error casting vote - random voting is not allowed for this poll.')
					return
			try:
				pick = int(pick)
				if pick <= 0 or pick > len(self.current_poll['choices']):
					raise Exception('Invalid vote value')
				self.current_poll['votes'][user] = pick
			except:
				self.irc.send_private(user, 'Error casting vote - please send a valid choice!')
		else:
			self.irc.send_private(user, 'Error - there are no polls in progress!')