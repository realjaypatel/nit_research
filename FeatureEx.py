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
        self.delimiters = [";", "/", "&", "?",  "(", ")", "{", "}", "[", "]", "\\x", "\\t",'%', '"' , "'",":", "=" ]
        # self.delimiters_2 = [":", "=",";", "/", "&", "?",  "(", ")", "{", "}", "[", "]", "\\x", "\\t",'%', '"' , "'", ]
        self.skip = ['recon' ,'adverti', 'brand' ,'model' ,'Nexus 6','sdk',"\\"]
        self.pii = ['Location','AndroidId','FirstName','Location','Username','SerialNumber','AndroidId','City','IMSI']
        self.adv = ['Advertiser ID','AdvertiserId','Zipcode']
        self.master_key_map = {}
        self.packet_key_dict = {}
        self.list_of_keys = []
        self.total_packetz = 0

    def extract_keys(self, packet_string,delimiters):
        """
        Extracts keys from a packet string by splitting it using delimiters.

        Args:
        - packet_string (str): The packet string to extract keys from.

        Returns:
        - keys (list): The list of extracted keys.
        """
        keys = [packet_string]
        for delimiter in delimiters:
            temp = []
            if delimiter == '=':
                for x in keys:
                    if '=' in x:
                        temp.append(x.split('=')[0])
                    else:
                        temp.append(x)
                    
                
                        
                keys[:] = temp


            else:
                keys[:] = [sub_key for key in keys for sub_key in key.split(delimiter) if not sub_key.isdigit()]
        
        temp = []
        for x in keys:
            if x.lower() in self.skip:
                # print(x)
                continue
            temp.append(x)
        return temp

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
                keys.extend(self.extract_keys(packet[key],self.delimiters))

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
        for packet in packetz:
            self.total_packetz += 1
            key_list = self.list_keys(packetz[packet])
            if isinstance(self.packetz[packet]["pii_types"], list):
                self.packet_key_dict[packet] = [1,key_list]
                # ad = False
                # pii = False
                # for x in self.packetz[packet]["pii_types"]:
                #     if x in self.pii:
                #         pii = True
                #     if x in self.adv:
                #         ad = True
                # if pii and ad:
                #     self.packet_key_dict[packet] = [3,key_list]
                # elif ad:
                #     self.packet_key_dict[packet] = [2,key_list]
                # else:
                #     self.packet_key_dict[packet] = [1,key_list]
            else:
                self.packet_key_dict[packet] = [0,key_list]
                
            for key in key_list:
                if key in self.list_of_keys:
                    self.master_key_map[key][0] += 1
                else:
                    self.master_key_map[key] = [1, 0]
                    self.list_of_keys.append(key)

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
        self.master_key_map = {key: value for key, value in self.master_key_map.items() if value[0] > 1 }  # if packet total_occu,pii_occur = >1 , >1 then only consider 
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
            self.register_keys(self.packetz)
        self.filter_keys(0.65)
        for i in self.master_key_map:
            self.list_of_keys.append(i)
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
        # binary_input = [0] * self.total_packetz
        binary_input =[]
        packet_no = 0
        for packetId in self.packet_key_dict:
            key_exist_bin_list = [0] * len(self.list_of_keys)   #value of each key in packet
            pii_exist = self.packet_key_dict[packetId][0]       #pii_exist value
            # print('pii_exist value',pii_exist)
            key_index = 0
            for i in self.list_of_keys:
                # if i != self.list_of_keys[key_index]:
                #     print("mismatch"+str(i)+ "and "+str(self.list_of_keys[key_index]))
                if i in self.packet_key_dict[packetId][1]:
                    key_exist_bin_list[key_index] = 1
                else:
                    key_exist_bin_list[key_index] = 0
                key_index += 1
            key_exist_bin_list.insert(0,packetId)
            key_exist_bin_list.insert(1,pii_exist)
            
            # binary_input[packet_no].extend(packetId)
            binary_input.append(key_exist_bin_list)
            # binary_input[packet_no].extend(pii_exist)
            packet_no += 1
            # print(binary_input[packet_no])'
                
        return binary_input
   
    def make_csv(self,binary_out,list_of_keys,output_path):
        
        """
        Creates a CSV file based on the binary input representation.

        Returns:
        - None
        """
        lok = list_of_keys
        lok.insert(0,"packetId")
        lok.insert(1,"pii_exist")

        # print(lok)
        with open(output_path + 'output_batchAll.csv', 'w',encoding="utf-8") as file:
            write = csv.writer(file,escapechar='\\')
            write.writerow(lok)
            write.writerows(binary_out)

        pass
    
# Specify the directory you want to start from
# rootDir = ""
# data_Dir = rootDir + "combined data"
# # data_Dir = rootDir + "antshield_public_dataset/1packettest.json"
# log_path = rootDir + "output/log.txt"
# out_path = rootDir + "output/"
    
rootDir = ""
data_Dir = rootDir + "data/antshield_public_dataset/raw_data/auto_anteater/"
log_path = rootDir + "output/log.txt"
out_path = rootDir + "output/"

key_extractor = KeyExtractor(data_Dir)
key_extractor.process_files()
print("finised processing")


binary_input = key_extractor.make_binary_input()
# print("_.>>",binary_input)
# print('------------------------------------------')
key_extractor.make_csv(binary_input,key_extractor.list_of_keys,out_path)


















