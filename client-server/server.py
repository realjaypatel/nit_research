import socket
import pickle

# Function to receive model from client
def receive_model(client_socket):
    # Receive model
    received_data = b""
    while True:
        packet = client_socket.recv(4096)
        if not packet:
            break
        received_data += packet

    # Deserialize received model
    received_model = pickle.loads(received_data)

    print("Model received successfully!")

    # Do something with the received model
    # For demonstration purposes, let's just print the model
    print("Received model:")
    print(received_model)

# Main server function
def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen(5)

    print("Server listening...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} has been established.")
        
        # Handle client's request in a separate thread or process
        receive_model(client_socket)
        client_socket.close()

if __name__ == "__main__":
    server()
