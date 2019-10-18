import socket
import logging
import re
import emoji
import copy
from sys import exit

class TwitchIrc:
    """
    This is a class for connecting to a Twitch IRC channel.

    Attributes:
        url (string): The IRC address to connect to.
        port (int): The port to use while connecting.
        user (string): The username of the Twitch account to use while connecting.
        token (string): The 'oauth:' prepended string of characters used for the bot account password.
        channel (string): The '#' prepended lowercase username of the Twitch channel to connect to.
        attempts (int): The number of attempts made to connect to the IRC server.
        sock (socket): The socket connection to the IRC server.
    """

    def __init__(self, url, port, user, token, chan):
        """
        The constructor for the TwitchIrc class.

        Parameters:
            url (string): The IRC address to connect to - typically = 'irc.twitch.tv'
            port (string or int): The IRC address port - typically = 6667
            user (string): The bot account's username.
            token (string): The 'oauth:' prepended string of characters used for the bot account password.
            chan (string): The lowercase username of the Twitch channel to connect to.
        """

        self.url = url
        self.port = int(port)
        self.user = user.lower()
        self.token = token
        self.channel = '#' + chan
        self.attempts = 0

    def connect(self):
        """
        The function to connect to the Twitch IRC server address.
        Makes 3 attempts before giving up.

        Parameters:
            None
        
        Returns:
            None
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock
        sock.settimeout(10)

        # Attempt to establish a connection
        try:
            sock.connect((self.url, self.port))
            logging.info('Successfully connected to IRC server.')
        except socket.error:
            logging.error(f'Error connecting to IRC server. ({self.url}:{self.port}) ({self.attempts+1})')

            if self.attempts < 2:
                self.attempts += 1
                self.connect()
            else:
                logging.critical(f'Failed to connect to IRC server. ({self.url}:{self.port})')
                exit(f'Failed to connect to IRC server after {self.attempts} attempts. ({self.url}:{self.port})')

        # After establishing a connection, remain connected
        self.attempts = 0
        sock.settimeout(None)

        # Send credentials
        self.send(f'USER {self.user}')
        self.send(f'PASS {self.token}')
        self.send(f'NICK {self.user}')

        if self.logged_in(self.recv()):
            logging.info('Login successful.')
        else:
            logging.critical('Invalid login')
            exit('Failed to log in to IRC server.')

        self.send(f'JOIN {self.channel}')
        logging.info(f'Joined channel {self.channel}')

        self.get_permissions()
    
    def close(self):
        """
        The function to close the socket connection, and log the action.

        Parameters:
            None

        Returns:
            None
        """

        self.sock.close()
        logging.info('Closed connection to IRC server.')

    def get_permissions(self):
        """
        The function to gain permissions from the IRC server.
        These permissions are:
            Membership: Adds membership state event data.
            Tags: Adds IRC V3 message tags to messages.
            Commands: Enables several Twitch-specific commands.
        
        Parameters:
            None
        
        Returns:
            None
        """

        logging.debug('Gathering permissions...')
        self.send('CAP REQ :twitch.tv/membership')
        self.send('CAP REQ :twitch.tv/commands')
        self.send('CAP REQ :twitch.tv/tags')
    
    def send_channel(self, message):
        """
        The function to send a message to the connect channel's public chat.

        Parameters:
            message (string): The message to be sent.
        
        Returns:
            None
        """

        self.send(f'PRIVMSG {self.channel} :{message}')

    def send_private(self, user, message):
        """
        The function to privately send a message to a Twitch user.

        Parameters:
            message (string): The message to be sent.
        
        Returns:
            None
        """

        self.send(f'PRIVMSG {self.channel} :.w {user} {message}')
        

    def send(self, data):
        """
        The function to send raw encoded data to the IRC server through the socket connection.

        Parameters:
            data (string): The data to be sent.
        
        Returns:
            None
        """

        if data[-2:] == '\r\n':
            data = data[0:-2]
        logging.debug(f'Sent data: {emoji.demojize(data)}')
        self.sock.send(str.encode(data + '\r\n'))
    
    def ping(self, data):
        """
        The function to response to automatic Twitch IRC server ping messages.
        Failure to respond results in being kicked from the server.
        Checks to see if the message is a PING message, and replies accordingly.

        Parameters:
            data (bytes): The encoded message from the server.
        
        Returns:
            None
        """

        if data.startswith(b'PING'):
            self.sock.send(data.replace(b'PING', b'PONG'))
            logging.debug('Sent automated Ping to IRC server.')

    def recv(self, amount=1024):
        data = self.sock.recv(amount)

        dd = data.decode().split('\r\n')
        if not dd[-1]:
            dd.pop(-1)
        for line in dd:
            logging.debug(f'Received data: {emoji.demojize(line)}')

        return data

    def recv_messages(self, amount=1024):
        data = self.recv(amount)
        if not data:
            logging.error('Lost connection, reconnecting...')
            self.connect()

        self.ping(data)
        if self.check_has_message(data):
            return [self.parse_message(line) for line in data.split(b'\r\n')]

    def check_has_message(self, data):
        """
        The function to determine whether encoded data contains an IRC message using regular expressions.

        Parameters:
            data (bytes): The encoded data received from the IRC server.
        
        Returns:
            Boolean: True if a message is found in data, false otherwise.
        """

        return re.search(r':[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data.decode())

    def parse_message(self, data):
        """
        The function to parse a message and extract data from it.

        Parameters:
            data (bytes): The encoded data from the IRC server which contains a message.
        
        Returns:
            userData (dict): Information about the message, such as who sent it, their badges, and what it says.
        """

        if data:
            dd = data.decode('utf8')

            userData = {
                'user': re.search(r'!(\w+)@', dd).group(1),
                'message': re.search(r'PRIVMSG #\w+ :(.+)$', dd).group(1),
                'badges': {}
            }

            tagList = re.search(r';badges=((.)*?);', dd).group(1).split(',')
            for tag in tagList:
                tagData = tag.split('/')
                userData['badges'][tagData[0]] = int(tagData[1])

            # Create a demojized copy of the data so we can log it without crashing - log files can't handle emojis
            loggedData = copy.deepcopy(userData)
            loggedData['message'] = emoji.demojize(loggedData['message'])
            logging.debug(f'Parsed message data: {loggedData}')

            return userData

    def logged_in(self, data):
        """
        The function to determine if the credentials sent to the IRC server were accepted.

        Parameters:
            data (bytes): The data which may hold the authentication failure message.
        
        Returns:
            Boolean: False if the authentication has failed, true otherwise.
        """

        return not re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login authentication failed\r\n$', data.decode())