import socket
import threading
import json

class Online:
    def __init__(self, game, host='127.0.0.1', port=5000, debug=False):
        self.game = game
        self.host = host
        self.port = port
        self.debug = debug
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_host = False
        self.player_id = None # 1 or 2 for now :)
        self.connected = False
        self.socket.bind((self.host, self.port))

    def start_host(self):
        if self.connected or self.is_host:
            return

        self.is_host = True
        self.player_id = 1
        threading.Thread(target=self._run_host, daemon=True).start()

    def _run_host(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            print(f'Host started on {self.host}:{self.port}. Waiting for connection to player 2...')
            self.conn, addr = self.socket.accept()
            print(f'connected to player {self.player_id}')
            self.connected = True

            # when connection to player 2, card seed gen and send
            self.game.sync_deck_seed()
            self._receive_loop()
        except Exception as e:
            print(f'Host error: {e}')

    def _accept_connection(self):
        self.conn, addr = self.socket.accept()
        self.connected = True
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def _connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.conn = self.socket
            self.connected = True
            threading.Thread(target=self._receive_loop, daemon=True).start()
        except Exception as e:
            print(f'Connection error: {e}')

    def send_action(self, action_type, data):
        if not self.connected:
            return
        payload = json.dumps(
            {
                'action': action_type,
                'player': self.player_id,
                'data': data,
            }
        ) + '\n'
        try:
            self.conn.sendall(payload.encode('utf-8'))
        except Exception as e:
            print(f'Sending error: {e}')

    def _receive_loop(self):
        buffer = ''
        while self.connected:
            try:
                data = self.conn.recv(1024).decode('utf-8')
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    parsed = json.loads(message)
                    self.game.handle_network_action(parsed)
            except Exception as e:
                break
        self.connected = False