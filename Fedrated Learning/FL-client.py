import socket
import time

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 64852
client_socket.connect((host, port))

# Function to send a message to the server
def send_message(message):
    client_socket.send(message.encode())

# Function to receive a message from the server
def receive_message():
    data = client_socket.recv(1024)
    return data.decode()

# Loop to send real-time timestamp when the server asks for the time
while True:
    received_data = receive_message()
    if received_data == "time":
        current_time = str(time.ctime())
        send_message(current_time)

# Close the connection
client_socket.close()