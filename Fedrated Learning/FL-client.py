import socket
import FeatureEx as FeatureEx
import ModelTraining as train
import os
import json
import sys
import pickle


# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 64852


# Function to send a message to the server
def send_message(message):
    try:
        client_socket.send(message.encode('utf-8'))
    except (BrokenPipeError, OSError):
        print("Error sending message. Closing the connection.")
        client_socket.close()

# Function to receive a message from the server
def receive_message():
    try:
        data = client_socket.recv(1024)
        print(data)
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
def receive_data_structure():
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

def report_new_key(key):
    send_message("new_key")
    while True:
        message = receive_message()
        if message == "send_key":
            send_message(key)
            break

def listen_for_server():
    while True:
        received_data = receive_message()
        if received_data == "model":   
            send_message()

        elif receive_message == "quit":
            # Close the connection
            client_socket.close()
            exit()

def bfs_json_files(data_path):
    """
    This function performs a breadth-first search on the directory tree starting from the given data path.
    It yields the path of each JSON file found in the directory tree.
    """
    queue = [data_path]
    
    while queue:
        current_dir = queue.pop(0)
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if os.path.isdir(item_path):
                queue.append(item_path)
            elif item.endswith('.json'):
                yield item_path

def extract_keys(data_path,output_file):
    extractor = FeatureEx.KeyExtractor()
    
    for json_file in bfs_json_files(data_path):
        extractor.process_files(json_file)
    return extractor

def round(output_file):
    # data_prc = train.data_preprocessor(output_path)
    # data_prc.preprocess()
    trainer = train.ModelTrainer(epsilon=1000, delta=1e-2, data_file=output_file)
    trainer.test_size=0.2
    trainer.random_state=42
    trainer.preprocess()
    trainer.federated_learning(trainer.X_train, trainer.y_train_one_hot, trainer.X_test, trainer.y_test)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python FL-client.py <client_data_path> <output_file>")
        sys.exit(1)
    client_data_path = sys.argv[1]
    outFile = sys.argv[2]

    extractor = extract_keys(client_data_path,outFile)
    client_socket.connect((host, port))
    print(f"Connected to the server")
    while receive_message() != "key list request":
        pass
    send_message("ready to send keys list")
    while receive_message() != "ready to receive keys list":
        pass
    send_data_structure(client_socket,extractor.list_of_keys)
    local_keys = len(extractor.list_of_keys)
    while receive_message() != "received keys list successfully":
        pass
    while receive_message()!= "broadcasting global key list":
        pass
    extractor.list_of_keys = receive_data_structure()
    print(client_data_path[-7:],"Local keySet : " , local_keys ,"Global keySet : ",len(extractor.list_of_keys))
    extractor.make_csv(extractor.make_binary_input(),outFile)
    
    
