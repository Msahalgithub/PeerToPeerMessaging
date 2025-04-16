import socket
import threading


HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050

def log(msg, sender='CLIENT'):
    print(f"[{sender}] {msg}")

def send(connection):
    while True:
        user = input("[SERVER]: ")    
        connection.sendall(user.encode("utf-8"))
        if user == "disconnect":
            connection.close()

def recieve(connection):
    while True:
        client = connection.recv(1024)
        if  client.decode("utf-8") == "disconnect":
            connection.close()
        log(client.decode("utf-8"), "CLIENT")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    log("Connecting to server")
    s.connect((HOST, PORT))
    log("Connection succesfully established")

    send_thread = threading.Thread(target=send, args=[s])
    recieve_thread = threading.Thread(target=recieve, args=[s])

    send_thread.start()
    recieve_thread.start()

    

log("session closed")