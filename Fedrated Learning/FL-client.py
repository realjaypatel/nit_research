import socket

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

# Example of sending a message
send_message("Hello from the client")

# Example of receiving a message
received_data = receive_message()
print("Received from server:", received_data)

# Close the connection
client_socket.close()