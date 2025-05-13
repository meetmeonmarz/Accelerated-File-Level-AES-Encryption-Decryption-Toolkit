# Marcio Amaral
# This file Encrypts all file types using parallel processing (MPI)



from mpi4py import MPI
import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
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
    folder_name = input("Enter the folder to encrypt: ")
else:
    folder_name = None
folder_name = comm.bcast(folder_name, root=0)

# ----- Input/Output Folder Setup -----
base_path = r"C:\Users\luini\Downloads"
input_folder = os.path.join(base_path, folder_name)
output_folder = os.path.join(base_path, f"encrypted_{folder_name}")

if rank == 0:
    if not os.path.exists(input_folder):
        print("Folder not found.")
        comm.Abort()
    if os.path.exists(output_folder):
        import shutil
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)
comm.Barrier()

# ----- Encrypt One File -----
def encrypt_file(input_path, output_path, key, extension):
    with open(input_path, "rb") as f:
        data = f.read()
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    ext_bytes = extension.encode()
    ext_len = len(ext_bytes).to_bytes(1, 'big')
    with open(output_path, "wb") as f:
        f.write(iv + ext_len + ext_bytes + encrypted)

# ----- Filter Supported File Types -----
allowed_exts = ('.txt', '.pdf', '.jpg', '.png', '.jpeg', '.bmp', '.webp', '.gif', '.tiff', '.mp3', '.mp4')
all_files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith(allowed_exts)])
chunk = all_files[rank::size]

# ----- Encrypt Files -----
start = time.time()
for file in tqdm(chunk, desc=f"[Proc {rank}] Encrypting", unit="file"):
    input_path = os.path.join(input_folder, file)
    name, ext = os.path.splitext(file)
    output_path = os.path.join(output_folder, name + ".bin")
    encrypt_file(input_path, output_path, key, ext)
end = time.time()
print(f"[Process {rank}] Encrypted {len(chunk)} files in {end - start:.4f} seconds.")

# ----- Report Total Time -----
all_durations = comm.gather(end - start, root=0)
comm.Barrier()
if rank == 0:
    print(f"\nTotal parallel encryption time: {max(all_durations):.4f} seconds.")
