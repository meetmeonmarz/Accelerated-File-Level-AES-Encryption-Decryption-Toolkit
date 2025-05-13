# Marcio Amaral
# This file Encrypts all file types sequentially

import os
import hashlib
from Crypto.Cipher import AES
import time
import shutil
from tqdm import tqdm

# ----- User Input -----
folder_name = input("Enter the name of the folder to encrypt: ")
base_path = r"C:\Users\luini\Downloads"
input_folder = os.path.join(base_path, folder_name)
output_folder = os.path.join(base_path, f"encrypted_{folder_name}")

# ----- AES Key Setup -----
password = "mypassword"
key = hashlib.sha256(password.encode()).digest()

def pad(data):
    while len(data) % 16 != 0:
        data += b" "
    return data

def encrypt_file(input_path, output_path, key):
    with open(input_path, "rb") as f:
        data = f.read()
    IV = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, IV)
    encrypted = cipher.encrypt(pad(data))
    with open(output_path, "wb") as f:
        f.write(IV + encrypted)

# ----- Prepare Output Folder -----
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
os.makedirs(output_folder)

# ----- Encrypt Files -----
valid_extensions = ('.txt', '.pdf', '.jpg', '.png', '.jpeg', '.bmp', '.webp', '.gif', '.tiff', '.mp3', '.mp4')
files = [f for f in os.listdir(input_folder) if f.lower().endswith(valid_extensions)]
start_enc = time.time()
for file_name in tqdm(files, desc="Encrypting", unit="file"):
    input_path = os.path.join(input_folder, file_name)
    output_path = os.path.join(output_folder, file_name + ".bin")
    encrypt_file(input_path, output_path, key)
end_enc = time.time()

print(f"\n✅ Encrypted {len(files)} files in {end_enc - start_enc:.4f} seconds.")
