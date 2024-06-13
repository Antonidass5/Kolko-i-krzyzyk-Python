import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5555))
server.listen(2)

rooms = {}
clients = []

def handle_client(client_socket):
    global rooms
    try:
        room_id = client_socket.recv(1024).decode('utf-8')
        if room_id == "CREATE_ROOM":
            room_id = str(len(rooms) + 1)
            rooms[room_id] = [client_socket]
            client_socket.send(f"ROOM_ID {room_id}".encode('utf-8'))
        elif room_id == "JOIN_ROOM":
            room_id = str(len(rooms))
            rooms[room_id].append(client_socket)
        else:
            room_id = None

        if room_id and len(rooms[room_id]) == 2:
            client_socket.send("START_GAME".encode('utf-8'))
            rooms[room_id][0].send("START_GAME".encode('utf-8'))

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message.startswith("MOVE"):
                broadcast(message, client_socket, room_id)
    except:
        clients.remove(client_socket)
        client_socket.close()

def broadcast(message, client_socket, room_id):
    for client in rooms[room_id]:
        if client != client_socket:
            client.send(message.encode('utf-8'))

print("Server started...")
while True:
    client_socket, addr = server.accept()
    clients.append(client_socket)
    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()
