import irc

class TwitchBot:
	def __init__(self, url, port, user, client, token, chan):
		server = irc.bot.ServerSpec(url, port=port, password=token)
		self.url = url
		self.port = port
		self.user = user
		self.client = client
		self.token = token
		self.channel = chan
		
		response = requests.get(self.url, headers=headers).json()
		self.channel_id = response['users'][0]['_id']

		irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], '', 'username')

	def run(self):
		while True:
			messages = self.irc.recv_messages(1024)

			if not messages:
				continue
			
			for message in messages:
				print(message)

	def on_public_message(self):
		print("gotmessage")