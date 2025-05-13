# Marcio Amaral
# This file Decrypts all file types using parallel processing (MPI)

from mpi4py import MPI
import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import time
from tqdm import tqdm

# ----- MPI Setup -----
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# ----- AES Key Setup -----
key = hashlib.sha256("mypassword".encode()).digest()

# ----- User Input (Only Rank 0) -----
if rank == 0:
    folder_name = input("Enter the encrypted folder to decrypt: ")
else:
    folder_name = None
folder_name = comm.bcast(folder_name, root=0)

# ----- Decrypt One File -----
def decrypt_file(input_path, output_base):
    with open(input_path, "rb") as f:
        iv = f.read(16)
        ext_len = int.from_bytes(f.read(1), 'big')
        ext = f.read(ext_len).decode()
        encrypted = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
    with open(output_base + ext, "wb") as f:
        f.write(decrypted)

# ----- Setup Output Folder and File List -----
if rank == 0:
    if not os.path.exists(folder_name):
        print("Encrypted folder not found.")
        comm.Abort()
    file_list = [f for f in os.listdir(folder_name) if f.endswith('.bin')]
    if not file_list:
        print("No .bin files found.")
        comm.Abort()
else:
    file_list = None
file_list = comm.bcast(file_list, root=0)

output_folder = folder_name.replace("encrypted_", "decrypted_")
if rank == 0 and not os.path.exists(output_folder):
    os.makedirs(output_folder)
comm.Barrier()

# ----- Divide Files Among Processes -----
files_per_proc = len(file_list) // size
remainder = len(file_list) % size
start_idx = rank * files_per_proc + min(rank, remainder)
end_idx = start_idx + files_per_proc + (1 if rank < remainder else 0)
my_files = file_list[start_idx:end_idx]

# ----- Decrypt Files -----
start = time.time()
for file in tqdm(my_files, desc=f"[Proc {rank}] Decrypting", unit="file"):
    input_path = os.path.join(folder_name, file)
    name = os.path.splitext(file)[0]
    output_path = os.path.join(output_folder, name)
    decrypt_file(input_path, output_path)
end = time.time()
print(f"[Process {rank}] Decrypted {len(my_files)} files in {end - start:.4f} seconds.")

# ----- Report Total Time -----
all_durations = comm.gather(end - start, root=0)
comm.Barrier()
if rank == 0:
    print(f"\nTotal parallel decryption time: {max(all_durations):.4f} seconds.")
