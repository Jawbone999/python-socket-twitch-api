import requests
import irc.bot

class TwitchBot(irc.bot.SingleServerIRCBot):
	def __init__(self, id, token, channel):
		self.id = id
		self.token = token
		self.channel = '#' + channel

		url = 'https://api.twitch.tv/kraken/users?login=' + channel
		headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
		response = requests.get(url, headers=headers).json()
		self.channel_id = response['users'][0]['_id']

		server = 'irc.chat.twitch.tv'
		port = 6667
		irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], '', 'username')

	def on_public_message(self):
		pass