# Marcio Amaral
# This file Decrypts all file types sequentially


import os
import hashlib
from Crypto.Cipher import AES
import time
import shutil
from tqdm import tqdm

# ----- User Input -----
folder_name = input("Enter the name of the encrypted folder to decrypt: ")
base_path = r"C:\Users\luini\Downloads"
encrypted_folder = os.path.join(base_path, folder_name)
decrypted_folder = os.path.join(base_path, f"decrypted_{folder_name}")

# ----- AES Key Setup -----
password = "mypassword"
key = hashlib.sha256(password.encode()).digest()

def decrypt_file(input_path, output_path, key):
    with open(input_path, "rb") as f:
        iv = f.read(16)
        encrypted_data = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_data).rstrip(b" ")
    with open(output_path, "wb") as f:
        f.write(decrypted)

# ----- Prepare Output Folder -----
if os.path.exists(decrypted_folder):
    shutil.rmtree(decrypted_folder)
os.makedirs(decrypted_folder)

# ----- Decrypt Files -----
extensions = ('.txt', '.pdf', '.jpg', '.png', '.jpeg', '.bmp', '.webp', '.gif', '.tiff', '.mp3', '.mp4')
files = [f for f in os.listdir(encrypted_folder) if f.endswith(".bin")]
start_dec = time.time()
for file_name in tqdm(files, desc="Decrypting", unit="file"):
    for ext in extensions:
        if file_name.endswith(ext + ".bin"):
            original_ext = ext
            break
    else:
        original_ext = ".txt"
    input_path = os.path.join(encrypted_folder, file_name)
    output_name = file_name.replace(".bin", "")
    output_path = os.path.join(decrypted_folder, output_name)
    decrypt_file(input_path, output_path, key)
end_dec = time.time()

print(f"\n✅ Decrypted {len(files)} files in {end_dec - start_dec:.4f} seconds.")
