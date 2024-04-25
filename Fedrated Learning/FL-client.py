import socket
import time

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 64852
client_socket.connect((host, port))

# Function to send a message to the server
def send_message(message):
    try:
        client_socket.send(message.encode())
    except (BrokenPipeError, OSError):
        print("Error sending message. Closing the connection.")
        client_socket.close()

# Function to receive a message from the server
def receive_message():
    try:
        data = client_socket.recv(1024)
        return data.decode()
    except (ConnectionResetError, OSError):
        print("Error receiving message. Closing the connection.")
        client_socket.close()

def report_new_key(key):
    send_message("new_key")
    while True:
        message = receive_message()
        if message == "send_key":
            send_message(key)
            break

# Loop to send real-time timestamp when the server asks for the time
while True:
    received_data = receive_message()
    if received_data == "model":   
        send_message()

    elif receive_message == "quit":
        # Close the connection
        client_socket.close()
        exit()

