import socket
import logging
import sys
import re

class Irc:
    def __init__(self, url, port, user, token, chan):
        self.url = url
        self.port = port
        self.user = user.lower()
        self.token = token
        self.channel = '#' + chan
        self.attempts = 0
        self.connect()
    
    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock
        sock.settimeout(10)

        try:
            sock.connect((self.url, self.port))
            logging.info('Successfully connected to IRC server.')
        except socket.error:
            logging.error(f'Error connecting to IRC server. ({self.url}:{self.port} ({self.attempts+1}')
            
            if self.attempts < 2:
                self.attempts += 1
                self.connect()
            else:
                logging.critical(f'Failed to connect to IRC server. ({self.url}:{self.port}')
                sys.exit()
        
        self.attempts = 0
        sock.settimeout(None)
        self.send(f'USER {self.user}')
        self.send(f'PASS {self.token}')
        self.send(f'NICK {self.user}')
        
        if self.logged_in(self.recv()):
            logging.info('Login successful.')
        else:
            logging.critical('Invalid login')
            sys.exit()
        
        self.send(f'JOIN {self.channel}')
        logging.info(f'Joined channel {self.channel}')
    
    def message_channel(self, message):
        self.send('PRIVMSG ' + message)

    def send(self, data):
        if data[-2:] == '\r\n':
            data = data[0:-2]
        logging.debug(f'Sent data: {data}')
        self.sock.send(str.encode(data + '\r\n'))
    
    def ping(self, data):
        if data.startswith(b'PING'):
            self.send(data.replace(b'PING', b'PONG'))

    def recv(self, amount=1024):
        data = self.sock.recv(amount)
        # Uncomment the following lines to log all chat messages
        """
        dd = data.decode().split('\r\n')
        if not dd[-1]:
            dd.pop(-1)
        for line in dd:
            logging.debug(f'Received data: {line}')
        """
        return data

    def recv_messages(self, amount=1024):
        data = self.recv(amount)
        if not data:
            logging.error('Lost connection, reconnecting...')
            return self.connect()

        self.ping(data)
        if self.check_has_message(data):
            return [self.parse_message(line) for line in data.split(b'\r\n')]
    
    def check_has_message(self, data):
        return re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data.decode())
    
    def parse_message(self, data):
        if data:
            dd = data.decode('utf8')
            user = re.findall(r'^:([a-zA-Z0-9_]+)\!', dd)[0]
            message = re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', dd)[0]
            if message.startswith('$'):
                message = message[1:]
                self.handle_command(user, message)
                
    def handle_command(self, user, msg):
        args = msg.split()
        command = args[0]
        if command.lower() == 'ping':
            logging.info('Received command: PING')
            self.send('Pong!')
        elif command.lower() == 'poll':
            logging.info('Received command: POLL')
            self.sock.send(b'POLL\r\n')

    def logged_in(self, data):
        return not re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data.decode())
    
    def has_message(self, data):
        return re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data.decode())
    
    


        