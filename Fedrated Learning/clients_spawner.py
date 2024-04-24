import subprocess

# Define the number of clients to spawn
num_clients = 10

# Spawn the clients
for i in range(num_clients):
    subprocess.Popen(["python", "nit_research/Fedrated Learning/FL-client.py"])
