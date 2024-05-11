import time
import json
import pickle
import sys
from asyncio import wait
import socket
import random
import ModelAggregation as agg

client_num = 10
clients_list = []
client_models = []
global_key_list = set()
k = len(clients_list) * 2 // 3

##################################################################
# setting up
##################################################################
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 64852
server_socket.bind((host, port))
server_socket.listen(client_num)  # Listen for up to n connections
print("Listening for connection!!")



def server_connection_loop(server_socket):
    while len(clients_list) < client_num:
        print("Waiting for connection!!")
        client_socket, addr = server_socket.accept()
        print(f'Connected to {addr}')
        clients_list.append((client_socket, addr))
        send_message(client_socket, "key list request")
        while receive_message(client_socket) != "ready to send keys list":
            pass
        send_message(client_socket, "ready to receive keys list")
        client_keys = receive_data_structure(client_socket)
        send_message(client_socket, "received keys list successfully")
        for i in client_keys:
            global_key_list.add(i)

    broadcast_message("broadcasting global key list", server_socket)
    broadcast_data_structure(list(global_key_list), server_socket)





##################################################################
# functions for communication send receive and broadcast
##################################################################

# Function to send a message to a client
def send_message(client_socket, message):
    try:
        client_socket.send(message.encode('utf-8'))
    except (BrokenPipeError, OSError):
        print("Error sending message. Closing the connection.")
        client_socket.close()

# Function to receive a message from a client
def receive_message(client_socket):
    try:
        data = client_socket.recv(1024)
        print(data.decode())
        return data.decode('utf-8')
    except (ConnectionResetError, OSError):
        print("Error receiving message. Closing the connection.")
        client_socket.close()

# Function to send a data structure to the server
def send_data_structure(client_socket, data):
    try:
        payload = pickle.dumps(data)
        data_size = len(payload)
        size_header = data_size.to_bytes(4, byteorder='big')  # Use a 4-byte header for size
        client_socket.send(size_header)
        client_socket.send(payload)
    except (BrokenPipeError, OSError):
        print("Error sending data structure. Closing the connection.")
        client_socket.close()

# Function to receive a data structure from the server
def receive_data_structure(client_socket):
    try:
        size_header = client_socket.recv(4)  # Receive the size header
        data_size = int.from_bytes(size_header, byteorder='big')  # Convert the size header to integer
        data = b''
        while len(data) < data_size:
            packet = client_socket.recv(data_size - len(data))
            if not packet:
                return None
            data += packet
        return pickle.loads(data)
    except (ConnectionResetError, OSError):
        print("Error receiving data structure. Closing the connection.")
        client_socket.close()

def broadcast_message(message, sender):
    for client in clients_list:
        if client is sender:
            pass
        else:
            send_message(client[0], message)

def broadcast_data_structure(data_structure, sender):
    for client in clients_list:
        if client is sender:
            pass
        else:
            send_data_structure(client[0], data_structure)

##################################################################
# functions used in threads
##################################################################

def clean_clients_list():
    while True:
        for client in clients_list:
            if client[0]._closed:
                clients_list.remove(client)
                k = len(clients_list) * 2 // 3
        time.sleep(1)  # Check every 1 seconds

# def listen_for_new_keys():
#     while True:
#         for client in clients_list:
#             message = receive_message(client)
#             if message is "new_key":
#                 send_message("send_key")
#                 key = receive_message(client)
#                 global_key_list.append(key)

            

##################################################################
# Functions for working with clients
##################################################################

# def ask_for_model(k):
#     while True:
#         print(f"Current time at server is: {time.ctime()}")
#         selected_clients = random.sample(clients_list, k)
#         for client in selected_clients:
#             send_message(client[0], "model")
#             received_time = receive_message(client[0])
#             print(f"Received time from client {client[1]}: {received_time}")
        
#         time.sleep(10)

def round(sel_client):
    broadcast_message("Request for model",server_socket)
    for i in range(len(sel_client)):
        print(i,sel_client[i][0])
        send_message(sel_client[i][0], "ready to receive model")
        client_models[i] = receive_data_structure(sel_client[i][0])
    aggragator = agg.ModelTrainer()
    print(client_models)
    aggragator.global_aggregator(client_models)

        

if __name__ == "__main__":
    server_connection_loop(server_socket)
    round(clients_list)