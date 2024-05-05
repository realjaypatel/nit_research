import FeatureEx as FeatureEx


KeyExtractor = FeatureEx.KeyExtractor()
data_file1 = "nit_research/data/antshield_public_dataset/raw_data/auto_anteater/batch1/HTTP/com.abtnprojects.ambatana.json"
data_file2 = "nit_research/data/antshield_public_dataset/raw_data/auto_anteater/batch1/HTTP/com.walmart.android.json"

out_path = "nit_research/output/outtest.csv"


KeyExtractor.process_files(data_file1)
print(KeyExtractor.list_of_keys)

KeyExtractor.process_files(data_file2)

binary_input = KeyExtractor.make_binary_input()
KeyExtractor.make_csv(binary_input,out_path)

print("finised running")