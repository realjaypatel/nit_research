import subprocess

# Define the number of clients to spawn
num_clients = 10

# Spawn the clients
for i in range(num_clients):
    i += 1
    print("Client" + str(i))
    subprocess.Popen(["python", "/home/kavi/Code/PacketMasti/nit_research/Fedrated Learning/FL-client.py", "/home/kavi/Code/PacketMasti/nit_research/data/antshield_public_dataset/raw_data/manual_anteater/batch" + str(i), "/home/kavi/Code/PacketMasti/nit_research/output/client" + str(i) + ".csv"])
