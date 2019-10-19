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
from copy import deepcopy

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
		custom_commands (dict): A dictionary of custom prefixed commands and their responses.
		auto_replies (dist): A dictionary of messages to automatically reply to.
		auto_messages (dict): A dictionary of messages to send every _ minutes.
	"""

	def __init__(self, url, port, user, token, chan, prefix):
		"""
		The constructor for the TwitchBot class.

		Parameters:
			url (string): The IRC address to connect to - typically = 'irc.twitch.tv'
            port (string or int): The IRC address port - typically = 6667
            user (string): The bot account's username.
            token (string): The 'oauth:' prepended string of characters used for the bot account password.
            chan (string): The lowercase username of the Twitch channel to connect to.
			prefix (string): The command prefix to signify the beginning of a command message.
		"""

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
		"""
		This function generates a dictionary to utilize as a sort of switch for commands.
		Allows the bot to evaluate commands faster than using if-elif statements.
		After this, command_map will contain aliases as keys and functions as values.

		Parameters:
			commands (dict): A dictionary of command names and aliases.
		
		Returns:
			None
		"""

		self.command_map = {}
		for command, aliases in commands.items():
			for alias in aliases:
				self.command_map[alias] = eval(f'self.{command}')

	def read_data_files(self):
		"""
		This function opens and stores the contents of multiple files within the data directory.

		Parameters:
			None

		Returns:
			None
		"""

		with open('bot/data/admins.json') as f:
			self.admins = json.load(f)

		with open('bot/data/custom_commands.json') as f:
			self.custom_commands = json.load(f)

		with open('bot/data/auto_replies.json') as f:
			self.auto_replies = json.load(f)

		with open('bot/data/auto_messages.json') as f:
			self.auto_messages = json.load(f)

		with open('bot/data/commands.json') as f:
			commands = json.load(f)
		self.generate_command_map(commands)

	def run(self):
		"""
		This function is the main driver for the TwitchBot class.
		It constantly receives message from the IRC and parses them.
		It also checks if it is time to send an automated message, and replies to messages in self.auto_replies.

		Parameters:
			None

		Returns:
			None
		"""

		while True:
			try:
				messages = self.irc.recv_messages()
				if messages:
					for msg in messages:
						if msg:
							if msg['message'].startswith(self.prefix):
								msg['message'] = msg['message'][1:]
								self.handle_command(msg)
							elif msg['message'] in self.auto_replies:
								logging.info(f'Replying to {msg["message"]}...')
								self.irc.send_channel(self.auto_replies[msg['message']])

				minsPassed = round((datetime.now() - self.start_time).total_seconds() / 60)
				for autoMessage, timeInfo in self.auto_messages.items():
					if minsPassed % timeInfo['Timer'] == 0 and minsPassed - timeInfo['LastTime'] >= timeInfo['Timer']:
						timeInfo['LastTime'] = minsPassed
						self.irc.send_channel(autoMessage)
			except (KeyboardInterrupt, SystemExit):
				raise
			except Exception as e:
				logging.fatal(f'Exception Caught: {" ".join(format_exception_only(type(e), e))}')

	def handle_command(self, data):
		"""
		This function executes the command given by a user message.

		Parameters:
			data (dict): Data about the message received. Contains:
				"message" (string): The user's message. Should be in the form "$COMMAND [ARGS]"
				"user" (string): The user's username.
				"badges" (dict): The user's badge data, taken from tags.

		Returns:
			None
		"""

		args = data['message'].split()
		user = data['user']
		badges = data['badges']

		command = args.pop(0).lower()

		if command in self.custom_commands:
			self.irc.send_channel(self.custom_commands[command])
		else:
			self.command_map.get(command, self.unknown_command)(user, badges, args)

	def unknown_command(self, user, badges, args):
		"""
		This function runs when the user calls an unknown command.
		It sends them a private message explaining their error.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		self.irc.send_private(user, f'Error: Unknown command. Try "{self.prefix}help" to receive documentation.')

	def ping(self, user, badges, args):
		"""
		This function handles execution of a basic ping command.
		It simply sends "Pong!" to the channel.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not self.has_permission(user, badges):
			self.irc.send_private(user, 'PermissionError')

		logging.info(f'Received PING command from {user}')

		self.irc.send_channel('Pong!')

	def disconnect(self, user, badges, args):
		"""
		This function gracefully disconnects the bot from the IRC server.
		It also signals the end of the program.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not self.has_permission(user, badges):
			self.irc.send_private(user, 'PermissionError')

		logging.info(f'Received DISCONNECT command from {user}')

		self.irc.close()

		logging.debug(f'Disconnected from IRC Server. ({self.irc.url}:{self.irc.port})')

		exit()

	def echo(self, user, badges, args):
		"""
		This function handles the execution of a basic echo command.
		It simply repeats the message given to it by the user.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not self.has_permission(user, badges):
			return self.irc.send_private(user, 'PermissionError')

		if not args:
			return self.irc.send_private(user, 'NoArgsError')

		message = ' '.join(args)

		logging.info(f'Received ECHO command from {user}: "{emoji.demojize(message)}"')

		self.irc.send_channel(message)

	def poll(self, user, badges, args):
		"""
		This function handles all functions related to polls.
		It calls the functions to create and start, display, or end polls.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

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
		"""
		This function creates and starts a poll given user parameters.
		Either uses the poll stored in poll.json, or creates one using a passed string argument.
		It also displays the poll.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not self.has_permission(user, badges):
			return self.irc.send_private(user, 'PermissionError')

		if not args:
				return self.irc.send_private(user, f'NoArgError')

		try:
			if args[0].lower() == 'auto':
				# Generate a poll using the input file
				with open('poll.json') as f:
					new_poll = json.load(f)
			else:
				# Rejoin the args and use them to generate a poll
				args = ' '.join(args)
				new_poll = json.loads(args)

			self.current_poll['title'] = new_poll['title']
			self.current_poll['random'] = new_poll['random']
			self.current_poll['votes'] = {}
			self.current_poll['choices'] = new_poll['choices']

			if not self.current_poll['choices']:
				return self.irc.send_private(user, 'Error creating poll - "choices" must have some elements.')

			logging.info(f'Received command POLL CREATE from {user}')

			self.current_poll['open'] = True

			logging.info(f'Opened poll: {self.current_poll}')

			self.display_poll(user, badges)
		except:
			self.irc.send_private(user, f'Error creating poll - check your arguments, or use "{self.prefix}help" to receive documentation.')

	def end_poll(self, user, badges):
		"""
		This function ends the currently running poll and calculates the winner.
		It sends the results to the channel.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
		
		Returns:
			None
		"""

		if not self.has_permission(user, badges):
			return self.irc.send_private(user, 'PermissionError')

		if not self.current_poll['open']:
			return self.irc.send_private(user, "BadStateError")

		# Close the poll
		self.current_poll['open'] = False

		# Calculate the winner
		games = {i : 0 for i in range(len(self.current_poll['choices']))}
		for choice in self.current_poll['votes'].values():
			games[choice - 1] += 1

		ranking = {}
		displayList = {game : count for game, count in zip(self.current_poll['choices'], games.values())}
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

		logging.info(f'Received command POLL END from {user}')

		self.irc.send_channel(displayString)

	def display_poll(self, user, badges):
		"""
		This function displays the currently running poll in the channel chat.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).

		Returns:
			None
		"""

		if not self.has_permission(user, badges, minimum='subscriber'):
			return self.irc.send_private(user, 'PermissionError')

		if not self.current_poll['open']:
			return self.irc.send_private(user, 'BadStateError')

		displayString = self.current_poll['title'] + f' ({self.prefix}vote) - Choices: '
		displayString += ' | '.join([f'{num+1}. {opt}' for num, opt in enumerate(self.current_poll['choices'])])
		if self.current_poll['random']:
			displayString += f' -- You can also throw your vote away using {self.prefix}vote random'

		logging.info(f'Received command POLL DISPLAY from {user}')

		self.irc.send_channel(displayString)

	def vote(self, user, badges, args):
		"""
		This function counts votes on the currently running poll.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			args (list): A list of strings sent by the user along with their command.
		
		Returns:
			None
		"""

		if not self.current_poll['open']:
			return self.irc.send_private(user, 'BadStateError')

		if not args:
			return self.irc.send_private(user, 'NoArgsError')

		pick = args[0].lower()

		if pick == 'random':
			if not self.current_poll['random']:
				return self.irc.send_private(user, 'BadStateError')

			pick = randint(1, len(self.current_poll['choices']))

		try:
			pick = int(pick)

			if pick <= 0 or pick > len(self.current_poll['choices']):
				return self.irc.send_private(user, 'BadArgError')

			self.current_poll['votes'][user] = pick

			logging.info(f'Received command VOTE from {user}: {pick}')
			
			self.irc.send_private(user, 'Your vote has been receieved.')
		except:
			self.irc.send_private(user, 'BadArgError')

	def reply(self, user, badges, args):
		"""
		This function handles functions regarding the reply command.
		Can add or remove strings for the bot to automatically reply to.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			args (list): A list of strings sent by the user along with their command.
		
		Returns:
			None
		"""

		if not args:
			return self.irc.send_private(user, 'NoArgError')

		if not self.has_permission(user, badges):
			return self.irc.send_private(user, 'PermissionError')

		function = args.pop(0).lower()

		if function == 'create':
			self.create_reply(user, args)
		elif function == 'delete':
			self.delete_reply(user, args)
		elif function == 'display':
			self.display_reply(user)
		else:
			self.irc.send_private(user, 'BadArgError')

	def create_reply(self, user, args):
		"""
		This function creates a reply to a specified message in chat.
		When any user enters the specified phrase, the bot will send a specified response.
		Adds the reply-response object to bot/data/auto_replies.json

		Parameters:
			user (string): The user who called the command.
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not args:
			return self.irc.send_private(user, 'NoArgsError')
		
		args = ' '.join(args).split(' | ')

		if len(args) != 2:
			return self.irc.send_private(user, 'BadArgsError')

		self.auto_replies[args[0]] = args[1]

		with open('bot/data/auto_replies.json', 'w') as f:
			json.dump(self.auto_replies, f)

		logging.info(f'Received command REPLY CREATE from {user}: {args[0]}: {args[1]}')

	def delete_reply(self, user, args):
		"""
		This function deletes a reply to a specified message in chat.
		Before this function, any user enters the specified phrase, the bot will send a specified response.
		After this function, it is no longer the case for that specific message.
		Adds the modified reply-response object to bot/data/auto_replies.json
		Accepts multiple | separated arguments for messages.
		Does not throw an error if message isn't in self.auto_replies

		Parameters:
			user (string): The user who called the command.
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not args:
			return self.irc.send_private(user, 'NoArgsError')

		args = ' '.join(args).split(' | ')

		for msg in args:
			response = self.auto_replies.pop(msg, None)

			if response:
				logging.info(f'Recevied command REPLY DELETE from {user}: {msg}: {response}')

		with open('bot/data/auto_replies.json', 'w') as f:
			json.dump(self.auto_replies, f)

	def display_reply(self, user):
		"""
		This function displays all message-response data.

		Parameters:
			user (string): The user who called the command.

		Returns:
			None
		"""

		displayString = ''
		for msg, rply in self.auto_replies.items():
			displayString += f'{msg}: {rply} | '

		displayString = displayString[:-3]

		if not displayString:
			displayString = 'Error - No replies to display.'

		self.irc.send_private(user, displayString)

		logging.info(f'Recevied command REPLY DISPLAY from {user}')

	def schedule(self, user, badges, args):
		"""
		This function handles functions pertaining to scheduled messaging.
		Can create, delete, or display automated messages.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not args:
			return self.irc.send_private(user, 'NoArgError')

		if not self.has_permission(user, badges):
			return self.irc.send_private(user, 'PermissionError')

		function = args.pop(0).lower()

		if function == 'create':
			self.create_schedule(user, args)
		elif function == 'delete':
			self.delete_schedule(user, args)
		elif function == 'display':
			self.display_schedule(user)
		else:
			self.irc.send_private(user, 'BadArgError')

	def create_schedule(self, user, args):
		"""
		This function creates a scheduled message to send every x minutes in chat.
		Adds the message-timeInfo object to bot/data/auto_messages.json

		Parameters:
			user (string): The user who called the command.
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not args:
			return self.irc.send_private(user, 'NoArgsError')

		args = ' '.join(args).split(' | ')

		if len(args) != 2:
			return self.irc.send_private(user, 'BadArgsError')

		args[1] = int(args[1])

		if args[1] <= 0:
			return self.irc.send_private(user, 'BadArgsError')

		try:
			self.auto_messages[args[0]] = {
				"LastTime": 0,
				"Timer": args[1]
			}
		except:
			self.irc.send_private(user, 'BadArgsError')

		# Create a deep copy for json writing purposes.
		# We don't want to interfere with established LastTime values.
		autoMsgs = deepcopy(self.auto_messages)
		for msg in autoMsgs:
			autoMsgs[msg]['LastTime'] = 0

		with open('bot/data/auto_messages.json', 'w') as f:
			json.dump(autoMsgs, f)

		logging.info(f'Received command SCHEDULE CREATE from {user}: {args[0]}: {args[1]}')

	def delete_schedule(self, user, args):
		"""
		This function deletes a scheduled message.
		Takes any number of | separated messages.
		Does not throw an error if a given message does not exist.

		Parameters:
			user (string): The user who called the command.
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not args:
			return self.irc.send_private(user, 'NoArgsError')

		args = ' '.join(args).split(' | ')

		for msg in args:
			timeData = self.auto_messages.pop(msg, None)

			if timeData:
				logging.info(f'Recevied command SCHEDULE DELETE from {user}: {msg}: {timeData["Timer"]}')

		# Create a deep copy for json writing purposes.
		# We don't want to interfere with established LastTime values.
		autoMsgs = deepcopy(self.auto_messages)
		for msg in autoMsgs:
			autoMsgs[msg]['LastTime'] = 0

		with open('bot/data/auto_messages.json', 'w') as f:
			json.dump(self.auto_messages, f)

	def display_schedule(self, user):
		"""
		This function displays all scheduled message data.

		Parameters:
			user (string): The user who called the command.

		Returns:
			None
		"""

		displayString = ''
		for msg, timeData in self.auto_messages.items():
			displayString += f'{msg}: {timeData["Timer"]} | '

		displayString = displayString[:-3]

		if not displayString:
			displayString = 'Error - No schedules to display.'

		self.irc.send_private(user, displayString)

		logging.info(f'Received command SCHEDULE DISPLAY from {user}')

	def command(self, user, badges, args):
		"""
		This function handles functions pertaining to custom commands.
		Can create, delete, or display custom commands.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not args:
			return self.irc.send_private(user, 'NoArgError')

		if not self.has_permission(user, badges):
			return self.irc.send_private(user, 'PermissionError')

		function = args.pop(0).lower()

		if function == 'create':
			self.create_command(user, args)
		elif function == 'delete':
			self.delete_command(user, args)
		elif function == 'display':
			self.display_command(user)
		else:
			self.irc.send_private(user, 'BadArgError')

	def create_command(self, user, args):
		"""
		This function creates a custom command.
		Adds the command-response object to bot/data/custom_commands.json

		Parameters:
			user (string): The user who called the command.
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not args:
			return self.irc.send_private(user, 'NoArgsError')

		if len(args) < 2:
			return self.irc.send_private(user, 'BadArgsError')

		msg = ' '.join(args[1:])

		self.custom_commands[args[0]] = msg

		with open('bot/data/custom_commands.json', 'w') as f:
			json.dump(self.custom_commands, f)

		logging.info(f'Received command COMMAND CREATE from {user}: {args[0]}: {args[1:]}')

	def delete_command(self, user, args):
		"""
		This function deletes a custom command.
		Takes any number of commands as arguments.

		Parameters:
			user (string): The user who called the command.
			args (list): A list of strings sent by the user along with their command.

		Returns:
			None
		"""

		if not args:
			return self.irc.send_private(user, 'NoArgsError')

		for cmd in args:
			msg = self.custom_commands.pop(cmd, None)

			if msg:
				logging.info(f'Recevied command COMMAND DELETE from {user}: {args}: {msg}')

		with open('bot/data/custom_commands.json', 'w') as f:
			json.dump(self.custom_commands, f)

	def display_command(self, user):
		"""
		This function displays all custom command data.

		Parameters:
			user (string): The user who called the command.

		Returns:
			None
		"""

		displayString = ''
		for cmd, res in self.custom_commands.items():
			displayString += f'{cmd}: {res} | '

		displayString = displayString[:-3]

		if not displayString:
			displayString = 'Error - No commands to display.'

		self.irc.send_private(user, displayString)

		logging.info(f'Received command COMMAND DISPLAY from {user}')

	def has_permission(self, user, badges, minimum='moderator'):
		"""
		This function determines if the user, given their badges, has permission to proceed with command execution.
		If the user is in the admins list, they bypass this check.

		Parameters:
			user (string): The user who called the command.
			badges (dict): A dictionary of badges and their corresponding level (or 1 if it has no levels).
			minimum (string): The minimum permission level required to pass the check.

		Returns:
			comparison (bool): True if highest user permission > minimum or if user in self.admins
		"""

		if user in self.admins:
			return True

		perms = []
		for badge in badges:
			perms.append(self.permission_values.get(badge, -1))

		return max(perms) >= self.permission_values[minimum]