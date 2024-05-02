import socket
import FeatureEx as FeatureEx
import ModelTraining as train
import os
import pickle


# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 64852


# Function to send a message to the server
def send_message(message):
    try:
        client_socket.send(message.encode())
    except (BrokenPipeError, OSError):
        print("Error sending message. Closing the connection.")
        client_socket.close()

# Function to send a data structure to the server
def send_data_structure(data):
    try:
        client_socket.send(pickle.dumps(data))
    except (BrokenPipeError, OSError):
        print("Error sending data structure. Closing the connection.")
        client_socket.close()

# Function to receive a message from the server
def receive_message():
    try:
        data = client_socket.recv(1024)
        return data.decode()
    except (ConnectionResetError, OSError):
        print("Error receiving message. Closing the connection.")
        client_socket.close()

# Function to receive a data structure from the server
def receive_data_structure():
    try:
        data = client_socket.recv(1024)
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
    extractor = FeatureEx.KeyExtractor(data_path)
    
    extractor.process_files()
    while not (receive_message() == "key list request"):
        pass
    send_message(extractor.list_of_keys)
    send_message("global key request")
    extractor.list_of_keys = list(dict.fromkeys(receive_message().split()))
    extractor.make_csv(extractor.make_binary_input(),extractor.list_of_keys,output_file)
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
    client_data_path = ""
    outFile = client_data_path + "output.csv"
    extractor = extract_keys(client_data_path,outFile)
    client_socket.connect((host, port))
