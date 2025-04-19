import socket
import threading
from enum import Enum


class MessageState(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARN = "warn"
    NORMAL = "normal"


class Debug:
    """
    Handles colored console output for different message states.
    """
    COLOR_CODES = {
        "error": "\033[31m",   # Red
        "success": "\033[32m", # Green
        "warn": "\033[33m",    # Yellow
        "end": "\033[0m"       # Reset
    }

    def log(self, message: str = "", sender: str = "", state: MessageState = MessageState.NORMAL):
        """
        Logs a message with appropriate coloring based on state.
        
        Args:
            message: The message to log
            sender: Identifier for the message source
            state: Message state (success, error, warn, normal)
        """
        if not message:
            return

        formatted_message = f"\n[{sender}] {message}" if sender else str(message)
        
        if state != MessageState.NORMAL:
            color_code = self.COLOR_CODES.get(state.value, "")
            end_code = self.COLOR_CODES["end"]
            formatted_message = f"{color_code}{formatted_message}{end_code}"
            
        print(formatted_message)


class Client:
    """
    Handles the TCP socket connection to a server.
    """
    def __init__(self, ip: str, port: int, sender: str = "CLIENT", buffer_size: int = 1024):
        self.ip = ip
        self.port = port
        self.sender_name = sender
        self.buffer_size = buffer_size
        self.encoding = "utf-8"
        self.debug = Debug()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self) -> bool:
        """
        Attempts to connect to the server.
        
        Returns:
            bool: True if connection succeeded, False otherwise
        """
        self.debug.log("Connecting to server...", self.sender_name, MessageState.NORMAL)
        try:
            self.socket.connect((self.ip, self.port))
            self.connected = True
            self.debug.log("Connection successful", self.sender_name, MessageState.SUCCESS)
            return True
        except Exception as e:
            self.debug.log(f"Connection failed: {e}", self.sender_name, MessageState.ERROR)
            return False

    def send(self, message: str) -> bool:
        
        if not self.connected:
            self.debug.log("Not connected to server", self.sender_name, MessageState.WARN)
            return False

        try:
            self.socket.sendall(message.encode(self.encoding))
            return True
        except Exception as e:
            self.debug.log(f"Send failed: {e}", self.sender_name, MessageState.ERROR)
            self.connected = False
            return False

    def receive(self) -> str:
        """
        Receives data from the server.
        
        Returns:
            str: The received message or empty string if error occurred
        """
        if not self.connected:
            return ""

        try:
            data = self.socket.recv(self.buffer_size)
            if not data:  # Connection closed by server
                self.connected = False
                return ""
            return data.decode(self.encoding)
        except Exception as e:
            self.debug.log(f"Receive failed: {e}", self.sender_name, MessageState.ERROR)
            self.connected = False
            return ""

    def close(self):
        """Closes the connection gracefully."""
        if self.connected:
            try:
                self.socket.close()
                self.connected = False
            except Exception as e:
                self.debug.log(f"Error closing connection: {e}", self.sender_name, MessageState.ERROR)


class PeerToPeerMessaging:
    """
    Manages the peer-to-peer messaging functionality with separate threads
    for sending and receiving messages.
    """
    def __init__(self, ip: str, port: int, sender: str, disconnect_word: str = "disconnect"):
        self.client = Client(ip, port, sender)
        self.disconnect_word = disconnect_word
        self.sender_name = sender
        self.debug = Debug()
        self.running = False

    def _send_loop(self):
        """Handles sending messages in a loop."""
        while self.running:
            try:
                user_input = input(f"[{self.sender_name}]: ").strip()
                if not user_input:
                    continue
                    
                if not self.client.send(user_input):
                    break
                    
                if user_input.lower() == self.disconnect_word:
                    self.stop()
            except (KeyboardInterrupt, EOFError):
                self.stop()
                break

    def _receive_loop(self):
        """Handles receiving messages in a loop."""
        while self.running:
            message = self.client.receive()
            if not message:
                self.stop()
                break
                
            self.debug.log(message, "SERVER", MessageState.NORMAL)
            if message.lower() == self.disconnect_word:
                self.stop()

    def start(self):
        """
        Starts the messaging service by connecting to server
        and launching send/receive threads.
        """
        if not self.client.connect():
            return False

        self.running = True
        
        # Create and start threads
        sender_thread = threading.Thread(target=self._send_loop, daemon=True)
        receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        
        sender_thread.start()
        receiver_thread.start()
        
        # Wait for threads to complete (they won't unless error occurs)
        sender_thread.join()
        receiver_thread.join()
        
        return True

    def stop(self):
        if self.running:
            self.running = False
            self.client.socket.close()


def main():
    # Configuration
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 5050
    CLIENT_NAME = "client"  # Change to "server" for the other peer

    # Create and start messaging service
    chat = PeerToPeerMessaging(HOST, PORT, CLIENT_NAME)
    try:
        chat.start()
    except KeyboardInterrupt:
        chat.stop()
        print("\nChat terminated by user.")


if __name__ == "__main__":
    main()