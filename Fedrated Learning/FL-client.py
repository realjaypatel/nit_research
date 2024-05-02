import socket
import time
import nit_research.FeatureEx_full as FeatureEx_full
import threading
import os

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

def extract_keys(data_path,output_path):
    extractor = FeatureEx_full.KeyExtractor(data_path)
    
    extractor.process_files()
    output = extractor.make_binary_input()
    extractor.make_csv(output,extractor.list_of_keys,output_path)


if __name__ == "__main__":
    client_data_path = ""

    key_extraction_thread = threading.Thread(extract_keys,args=client_data_path,client_data_path+"/output.csv")
    key_extraction_thread.start()