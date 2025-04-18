
import socket 
import threading


class Debug:
    def __init__(self):
        self.Error = "\033[31m"   # Red text
        self.Success = "\033[32m" # Green text
        self.Warn = "\033[33m"    # Yellow text
        self.end = "\033[0m"      # Reset color

    def log(self, message="", sender="", state='success'):
        color_table = {
            "success": f"{self.Success}[{sender}] {message}{self.end}",
            "error": f"{self.Error}[{sender}] {message}{self.end}",
            "warn": f"{self.Warn}[{sender}] {message}{self.end}",
        }

        if state in color_table:
            print(color_table[state])
        else:
            print(f"[{sender}] {message}")

class Client:
    def __init__(self, ip, port, sender="CLIENT"):
        self.port = port
        self.ip = ip
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug = Debug()
        self.format = "utf-8"
        self.sender_name = sender

    def init(self):
        self.debug.log("Connecting to server.", sender=self.sender_name, state="normal")
        try:
            self.socket.connect((self.ip, self.port))
            self.debug.log("Connection succesful.", sender=self.sender_name, state="success")
        except Exception as e:
            self.debug.log(f"Connection failed: {e}", sender=self.sender_name, state="error")

    def send(self, message: str):
        in_bytes = message.encode(self.format)
        self.socket.sendall(in_bytes)

    def receive(self):
        message = self.socket.recv(1024)
        self.debug.log(message=message, sender=self.sender_name, state="")
        

    def close_connection(self):
        self.socket.close()


class PeerToPeerMessaging:
    def __init__(self, ip, port, sender):
        self.client = Client(ip=ip, port=port, sender=sender)
        self.client.init()
        self.end_word = 'disconnect'
        self.sender_name = sender
        self.debug = Debug()
        self.message_threads_running = True

    def send_loop(self):
        while self.message_threads_running:
            user = input(f"[{self.sender_name}]: ")
            self.client.send(message=user)
            if self.end_word == user:
                self.client.close_connection()
                self.message_threads_running = False

    def receive_loop(self):
        while self.message_threads_running:
            message = self.client.receive()
            self.debug.log(message=message, sender='SERVER', state="")
            if message == self.end_word:
                self.client.close_connection()
                self.message_threads_running = False

    def initialize_threads(self):
        self.sender_thread = threading.Thread(target=self.send_loop)
        self.receiver_thread = threading.Thread(target=self.receive_loop)
        return True

    def start(self):
        self.initialize_threads()
        self.receiver_thread.start()
        self.sender_thread.start()


ip = socket.gethostbyname(socket.gethostname())
port = 5050

ptp_chat = PeerToPeerMessaging(ip, port, "Sahal")
ptp_chat.start()
