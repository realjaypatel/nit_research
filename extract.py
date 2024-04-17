import glob
import os
import json
rootDir = ""
class KeyExtractor:
    def __init__(self, data_path):
        """
        Initializes the KeyExtractor object.

        Args:
        - directory (str): The directory path where the JSON files are located.
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

    def extract_keys(self, packet_string):
        """
        Extracts keys from a packet string by splitting it using delimiters.

        Args:
        - packet_string (str): The packet string to extract keys from.

        Returns:
        - keys (list): The list of extracted keys.
        """
        keys = [packet_string]
        for delimiter in self.delimiters:
            keys = [sub_key for key in keys for sub_key in key.split(delimiter) if not sub_key.isdigit()]
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
                keys.extend(self.extract_keys(packet[key]))

            elif isinstance(value, dict) and value:
                keys.extend(filter(None, self.list_keys(value)))
        return keys

    def register_keys(self):
        """
        Registers the keys from the packets and updates the master key map.

        Returns:
        - master_key_map (dict): The updated master key map.
        """
        for packet in self.packetz:
            key_list = self.list_keys(self.packetz[packet])
            self.packet_key_dict[packet] = key_list
            for key in key_list:
                if key in self.master_key_map:
                    self.master_key_map[key][0] += 1
                else:
                    self.master_key_map[key] = [1, 0]
                if isinstance(self.packetz[packet]["pii_types"], list):
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
        self.master_key_map = {key: value for key, value in self.master_key_map.items() if value[1] / value[0] >= threshold}
        return self.master_key_map

    def process_files(self):
        """
        Processes the JSON files in the specified directory.

        Returns:
        - master_key_map (dict): The final master key map.
        """
        json_files = self.json_files
        for json_file in json_files:
            print("processing..."+json_file)
            with open(json_file, 'r') as data_file:
                self.packetz = json.loads(data_file.read())
            self.register_keys()
            self.filter_keys(0.95)
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
        mkmap = self.master_key_map
        pkdict = self.packet_key_dict
        binary_input = {}
        for i in pkdict:
            print("generating binary output....." + i)
            binary_input[i] = {}
            for j in mkmap:
                if j in pkdict[i]:
                    binary_input[i][j] = 1
                else:
                    binary_input[i][j] = 0
        return binary_input

# Specify the directory you want to start from
data_Dir = rootDir + "antshield_public_dataset/raw_data/"
log_path = rootDir + "_output/log.txt"
out_path = rootDir + "_output/output.txt"

key_extractor = KeyExtractor(data_Dir)
key_extractor.process_files()
print("finised processing")

log = open(log_path, 'w')
log.write("master_key_Map : \n" + str(key_extractor.master_key_map) +"\npacket_key_dict : \n" +str(key_extractor.packet_key_dict))
log.close()

binary_input = key_extractor.make_binary_input()

outputFile = open(out_path, 'w')
outputFile.write(str(binary_input) + '\n')
outputFile.close()