import glob
import os
import json
import csv

class KeyExtractor:
    def __init__(self, data_path):
        """
        Initializes the KeyExtractor object.

        Args:
        - data_path (str): The directory path where the JSON files are located.
        """
        self.data_path = data_path
        if os.path.isdir(data_path):
            self.directory = data_path
            self.json_files = self.find_json_files(self.directory)
        else:
            self.json_files = [data_path]
        self.delimiters = [",", ";", "/", "&", "?", ":", "=", "(", ")", "{", "}", "[", "]", "\\x", "\\t"]
        self.master_key_map = {}
        self.packet_key_dict = {}
        self.list_of_keys = []
        self.total_packets = 0

    def extract_keys(self, packet_string):
        """
        Extracts keys from a packet string by splitting it using delimiters.

        Args:
        - packet_string (str): The packet string to extract keys from.

        Returns:
        - keys (list): The list of extracted keys.
        """
        # keys = [packet_string]
        # for delimiter in self.delimiters:
        #     keys[:] = [sub_key for key in keys for sub_key in key.split(delimiter) if not sub_key.isdigit()]
        # return keys
        keys = [packet_string]
        for delimiter in self.delimiters:
            if delimiter == '=':
                # print('+++',keys)
                keys[:] = [sub_key.split('=')[0].strip() for key in keys for sub_key in key.split(delimiter) if not sub_key.isdigit()]
                # print('->',keys)

            else:
                keys[:] = [sub_key for key in keys for sub_key in key.split(delimiter) if not sub_key.isdigit()]
        return keys

    def list_keys(self, packet):
        """
        Lists all the keys in a packet.

        Args:
        - packet (dict): The packet dictionary.

        Returns:
        - keys (list): The list of keys in the packet.
        """
        keys = []
        for key, value in packet.items():
            if key == "pii_types":
                continue
            if isinstance(value, str):
                keys.extend(self.extract_keys(value))
            elif isinstance(value, dict) and value:
                keys.extend(filter(None, self.list_keys(value)))
        return keys

    def register_keys(self, packetz):
        """
        Registers the keys from the packets and updates the master key map for a file.

        Args:
        - packetz (dict): The packet file.

        Returns:
        - master_key_map (dict): The updated master key map.
        """
        for packet_id, packet in packetz.items():
            self.total_packets += 1
            key_list = self.list_keys(packet)
            pii_types = packet.get("pii_types", [])
            self.packet_key_dict[packet_id] = [1 if isinstance(pii_types, list) else 0, key_list]
            for key in key_list:
                self.master_key_map.setdefault(key, [0, 0])
                self.master_key_map[key][0] += 1
                if isinstance(pii_types, list):
                    self.master_key_map[key][1] += 1
        return self.master_key_map
    
    def filter_keys(self, threshold):
        """
        Filters the keys in the master key map based on a threshold.

        Args:
        - threshold (float): The threshold value for filtering.

        Returns:
        - master_key_map (dict): The filtered master key map.
        """
        self.master_key_map = {key: value for key, value in self.master_key_map.items() if value[1] / value[0] >= threshold and value[0] > 1}
        return self.master_key_map

    def process_files(self):
        """
        Processes the JSON files in the specified directory.

        Returns:
        - master_key_map (dict): The final master key map.
        """
        json_files = self.json_files
        for json_file in json_files:
            print("processing..." + json_file)
            with open(json_file, 'r') as data_file:
                self.packetz = json.load(data_file)
            self.register_keys(self.packetz)
        self.filter_keys(0.65)
        self.list_of_keys.extend(self.master_key_map.keys())
        return self.master_key_map

    def find_json_files(self, directory):
        """
        Finds all the JSON files in the specified directory.

        Args:
        - directory (str): The directory path.

        Returns:
        - json_files (list): The list of JSON file paths.
        """
        json_files = []
        for file in glob.glob(os.path.join(directory, '**/*.json'), recursive=True):
            json_files.append(file)
        return json_files

    def make_binary_input(self):
        """
        Creates a binary input representation based on the master key map and packet key dictionary.

        Returns:
        - binary_input (dict): The binary input representation.
        """
        binary_input = []
        for packet_id, (pii_exist, key_list) in self.packet_key_dict.items():
            print("generating binary output...[{}]".format(packet_id))
            key_exist_bin_list = [int(key in key_list) for key in self.list_of_keys]
            binary_input.append([packet_id, pii_exist] + key_exist_bin_list)
        return binary_input
   
    def make_csv(self, binary_out, output_path):
        """
        Creates a CSV file based on the binary input representation.

        Returns:
        - None
        """
        headers = ["packetId", "pii_exist"] + self.list_of_keys
        with open(output_path + 'output.csv', 'w') as file:
            write = csv.writer(file, escapechar='\\')
            write.writerow(headers)
            write.writerows(binary_out)

# Specify the directory you want to start from
rootDir = ""
data_Dir = rootDir + "antshield_public_dataset/raw_data/auto_anteater/batch1"
log_path = rootDir + "output/log.txt"
out_path = rootDir + "output/"

key_extractor = KeyExtractor(data_Dir)
key_extractor.process_files()
print("finished processing")

# log = open(log_path, 'w')
# log.write("master_key_Map : \n" + str(key_extractor.master_key_map) +"\npacket_key_dict : \n" +str(key_extractor.packet_key_dict))
# log.close()

binary_input = key_extractor.make_binary_input()
key_extractor.make_csv(binary_input, out_path)
