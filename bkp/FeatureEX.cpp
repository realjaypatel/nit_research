#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <filesystem>
#include <unordered_map>
#include <libs/json.hpp>
#include <sstream>
#include <algorithm>

namespace fs = std::filesystem;
using json = json;

class KeyExtractor {
    private:
        std::string data_path;
        std::vector<std::string> json_files;
        std::vector<std::string> delimiters = {";", "/", "&", "?", "(", ")", "{", "}", "[", "]", "\\x", "\\t", "%", "\"", "'", ":", "="};
        std::vector<std::string> skip = {"recon", "adverti", "brand", "model", "Nexus 6", "sdk", "\\"};
        std::vector<std::string> pii = {"Location", "AndroidId", "FirstName", "Location", "Username", "SerialNumber", "AndroidId", "City", "IMSI"};
        std::vector<std::string> adv = {"Advertiser ID", "AdvertiserId", "Zipcode"};
        std::unordered_map<std::string, std::pair<int, int>> master_key_map;
        std::unordered_map<std::string, std::pair<int, std::vector<std::string>>> packet_key_dict;
        std::vector<std::string> list_of_keys;
        std::vector<std::string> pii_list;
        std::vector<std::string> adv_list;
        int total_packets = 0;

    public:
        KeyExtractor(const std::string& path) : data_path(path) {
            if (fs::is_directory(data_path)) {
                for (const auto& entry : fs::recursive_directory_iterator(data_path)) {
                    if (entry.path().extension() == ".json") {
                        json_files.push_back(entry.path());
                    }
                }
            } else {
                json_files.push_back(data_path);
            }
        }

        std::vector<std::string> split(const std::string& s, const std::string& delimiter) {
            std::vector<std::string> tokens;
            std::string token;
            size_t pos = 0, start = 0, delim_length = delimiter.length();
            while ((pos = s.find(delimiter, start)) != std::string::npos) {
                token = s.substr(start, pos - start);
                if (!token.empty()) tokens.push_back(token);
                start = pos + delim_length;
            }
            token = s.substr(start);
            if (!token.empty()) tokens.push_back(token);
            return tokens;
        }

        bool isNumber(const std::string& s) {
            return !s.empty() && find_if(s.begin(), s.end(), [](unsigned char c) { return !std::isdigit(c); }) == s.end();
        }

        std::vector<std::string> extract_keys(const std::string& packet_string, const std::vector<std::string>& delimiters) {
            std::vector<std::string> keys = {packet_string};
            for (const auto& delimiter : delimiters) {
                std::vector<std::string> temp;
                if (delimiter == "=") {
                    for (const auto& x : keys) {
                        size_t pos = x.find('=');
                        if (pos != std::string::npos) {
                            temp.push_back(x.substr(0, pos));
                        } else {
                            temp.push_back(x);
                        }
                    }
                    keys = temp;
                } else {
                    temp.clear();
                    for (const auto& key : keys) {
                        auto sub_keys = split(key, delimiter);
                        for (const auto& sub_key : sub_keys) {
                            if (!isNumber(sub_key)) {
                                temp.push_back(sub_key);
                            }
                        }
                    }
                    keys = temp;
                }
            }

            keys.erase(remove_if(keys.begin(), keys.end(), [this](const std::string& x) {
                return find(skip.begin(), skip.end(), x) != skip.end() || find_if(skip.begin(), skip.end(), [&x](const std::string& skipWord) { return x.find(skipWord) != std::string::npos; }) != skip.end();
            }), keys.end());

            return keys;
        }

        std::vector<std::string> listKeys(const json& packet) {
            std::vector<std::string> keys;
            for (auto& [key, value] : packet.items()) {
                if (key == "pii_types") {
                    continue;
                }
                if (value.is_string()) {
                    auto extractedKeys = extract_keys(value, delimiters); // Assuming extract_keys is correctly implemented and delimiters is available in the scope
                    keys.insert(keys.end(), extractedKeys.begin(), extractedKeys.end());
                } else if (value.is_object() && !value.empty()) {
                    auto nestedKeys = listKeys(value);
                    keys.insert(keys.end(), nestedKeys.begin(), nestedKeys.end());
                }
            }
            return keys;
        }

        void processFiles() {
            for (const auto& file_path : json_files) {
                std::ifstream file(file_path);
                json packetz;
                file >> packetz;

                registerKeys(packetz);
            }
            // Additional processing can be added here
        }

        void registerKeys(const json& packetz) {
                for (auto& packet : packetz) {
                total_packets++;
                auto key_list = listKeys(packet.second); // Assuming listKeys is implemented and returns std::vector<std::string>
                bool ad = false;
                bool pii = false;

                for (auto& x : packet.second["pii_types"]) {
                    if (find(pii_list.begin(), pii_list.end(), x) != pii_list.end()) {
                        pii = true;
                    }
                    if (find(adv_list.begin(), adv_list.end(), x) != adv_list.end()) {
                        ad = true;
                    }
                }

                int category = 0;
                if (pii && ad) {
                    category = 3;
                } else if (ad) {
                    category = 2;
                } else {
                    category = 1;
                }
                packet_key_dict[packet.first] = std::make_pair(category, key_list);

                for (auto& key : key_list) {
                    auto it = find(list_of_keys.begin(), list_of_keys.end(), key);
                    if (it != list_of_keys.end()) {
                        master_key_map[key].first++;
                    } else {
                        master_key_map[key] = std::make_pair(1, 0);
                        list_of_keys.push_back(key);
                    }

                    // Assuming packet.second["pii_types"] is a std::vector<std::string>
                    if (!packet.second["pii_types"].empty()) {
                        master_key_map[key].second++;
                    }
                }
            }
        }

        void makeCSV(const std::string& output_path) {
            std::ofstream file(output_path + "output.csv");
            // CSV writing logic based on the Python code
        }
};

int main() {
    std::string dataDir = "path/to/your/data";
    std::string outputPath = "path/to/output/";

    KeyExtractor keyExtractor(dataDir);
    keyExtractor.processFiles();
    keyExtractor.makeCSV(outputPath);

    return 0;
}