import socket
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050

def log(msg, sender='SERVER'):
    print(f"[{sender}] {msg}")

def send(connection):
    user = input("[SERVER]: ")
    
    connection.sendall(user.encode("utf-8"))
    if  user == "disconnect":
        connection.close()

def recieve(connection):
    
    client = connection.recv(1024)
    if  client.decode("utf-8") == "disconnect":
            connection.close()
                
    log(client.decode("utf-8"), "CLIENT")



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    log("Binding the socket...")
    s.bind((HOST, PORT))
    log("Socket binded to host address.")
    log("Listening...")
    s.listen()
    
    
    connection, addr = s.accept()
    send_thread = threading.Thread(target=send, args=[connection])
    recieve_thread = threading.Thread(target=recieve, args=[connection])
    
    send_thread.start()
    recieve_thread.start()
    
log("Session closed.")
