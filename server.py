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


class Server:
    """
    Handles the TCP server socket and client connections.
    """
    def __init__(self, ip: str, port: int, sender: str = "SERVER", buffer_size: int = 1024):
        self.ip = ip
        self.port = port
        self.sender_name = sender
        self.buffer_size = buffer_size
        self.encoding = "utf-8"
        self.debug = Debug()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        self.client_address = None
        self.connected = False

    def start(self) -> bool:
        """
        Starts the server and waits for a client connection.
        
        Returns:
            bool: True if connection succeeded, False otherwise
        """
        try:
            self.debug.log("Starting server...", self.sender_name, MessageState.NORMAL)
            self.socket.bind((self.ip, self.port))
            self.socket.listen(1)  # Allow 1 queued connection
            self.debug.log(f"Server listening on {self.ip}:{self.port}", 
                         self.sender_name, MessageState.SUCCESS)
            
            self.debug.log("Waiting for client connection...", self.sender_name, MessageState.NORMAL)
            self.connection, self.client_address = self.socket.accept()
            self.connected = True
            self.debug.log(f"Connection from {self.client_address}", 
                         self.sender_name, MessageState.SUCCESS)
            return True
        except Exception as e:
            self.debug.log(f"Server error: {e}", self.sender_name, MessageState.ERROR)
            return False

    def send(self, message: str) -> bool:
        """
        Sends a message to the connected client.
        
        Args:
            message: The message to send
            
        Returns:
            bool: True if send succeeded, False otherwise
        """
        if not self.connected:
            self.debug.log("No client connected", self.sender_name, MessageState.WARN)
            return False

        try:
            self.connection.sendall(message.encode(self.encoding))
            return True
        except Exception as e:
            self.debug.log(f"Send failed: {e}", self.sender_name, MessageState.ERROR)
            self.connected = False
            return False

    def receive(self) -> str:
        if not self.connected:
            return ""

        try:
            data = self.connection.recv(self.buffer_size)
            if not data:  # Connection closed by client
                self.connected = False
                return ""
            return data.decode(self.encoding)  # Return raw message without formatting
        except Exception as e:
            self.debug.log(f"Receive failed: {e}", self.sender_name, MessageState.ERROR)
            self.connected = False
            return ""

def _receive_loop(self):
    """Handles receiving messages in a loop."""
    while self.running:
        message = self.server.receive()
        if not message:
            self.stop()
            break
            
        # Format the message just once here
        self.debug.log(message, "CLIENT", MessageState.NORMAL)
        if message.lower() == self.disconnect_word:
            self.stop()

    def close(self):
        """Closes the connection and server socket gracefully."""
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                self.debug.log(f"Error closing connection: {e}", self.sender_name, MessageState.ERROR)
        
        try:
            self.socket.close()
        except Exception as e:
            self.debug.log(f"Error closing server socket: {e}", self.sender_name, MessageState.ERROR)
        
        self.connected = False


class PeerToPeerServer:
    """
    Manages the peer-to-peer server functionality with separate threads
    for sending and receiving messages.
    """
    def __init__(self, ip: str, port: int, sender: str, disconnect_word: str = "disconnect"):
        self.server = Server(ip, port, sender)
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
                    
                if not self.server.send(user_input):
                    break
                    
                if user_input.lower() == self.disconnect_word:
                    self.stop()
            except (KeyboardInterrupt, EOFError):
                self.stop()
                break

    def _receive_loop(self):
        """Handles receiving messages in a loop."""
        while self.running:
            message = self.server.receive()
            if not message:
                self.stop()
                break
                
            self.debug.log(message, "CLIENT", MessageState.NORMAL)
            if message.lower() == self.disconnect_word:
                self.stop()

    def start(self):
        """
        Starts the server and messaging service.
        """
        if not self.server.start():
            return False

        self.running = True
        
        # Create and start threads
        sender_thread = threading.Thread(target=self._send_loop, daemon=True)
        receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        
        sender_thread.start()
        receiver_thread.start()
        
        # Wait for threads to complete
        sender_thread.join()
        receiver_thread.join()
        
        return True

    def stop(self):
        """Stops the server gracefully."""
        if self.running:
            self.running = False
            self.server.socket.close()


def main():
    # Configuration
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 5050
    SERVER_NAME = "Server"  # Change as needed

    # Create and start server
    server = PeerToPeerServer(HOST, PORT, SERVER_NAME)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        print("\nServer terminated by user.")


if __name__ == "__main__":
    main()