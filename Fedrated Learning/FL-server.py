import time
from asyncio import wait
import socket
import threading
import random

clients_list = []
global_key_list = []
k=len(clients_list)*2//3

##################################################################
# setting up
##################################################################

def server_connection_loop(server_socket):
    while True:
        client_socket, addr = server_socket.accept()
        print(f'Connected to {addr}')
        clients_list.append((client_socket,addr))
        # client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        # client_thread.start()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 64852
server_socket.bind((host, port))
server_socket.listen(10)  # Listen for up to 10 connections
server_connection_thread = threading.Thread(target=server_connection_loop,args=(server_socket,))
server_connection_thread.start()


##################################################################
# functions for communication send receive and broadcast
##################################################################

# Function to send a message to a client
def send_message(client_socket, message):
    try:
        client_socket.send(message.encode())
    except (BrokenPipeError, OSError):
        print("Error sending message. Closing the connection.")
        client_socket.close()

# Function to receive a message from a client
def receive_message(client_socket):
    try:
        data = client_socket.recv(1024)
        return data.decode()
    except (ConnectionResetError, OSError):
        print("Error receiving message. Closing the connection.")
        client_socket.close()
    
def broadcast_message(message,sender):
    for client in clients_list:
        if client is sender:
            pass
        else:
            send_message(client[0], message)


##################################################################
# functions used in threads
##################################################################

def clean_clients_list():
    while True:
        for client in clients_list:
            if client[0]._closed:
                clients_list.remove(client)
                k=len(clients_list)*2//3
        time.sleep(1)  # Check every 1 seconds

def listen_for_new_keys():
    while True:
        for client in clients_list:
            message = receive_message(client)
            if message is "new_key":
                send_message("send_key")
                key = receive_message(client)
                global_key_list.append(key)

            

##################################################################
# Functions for working with clients
##################################################################

def ask_for_model(k):
    while True:
        print(f"Current time at server is: {time.ctime()}")
        selected_clients = random.sample(clients_list, k)
        for client in selected_clients:
            send_message(client[0],"model")
            received_time = receive_message(client[0])
            print(f"Received time from client {client[1]}: {received_time}")
        
        time.sleep(10)
            

        

if __name__ == "__main__":
    while not clients_list:
        continue
    cleaner_thread = threading.Thread(target=clean_clients_list)
    cleaner_thread.start()