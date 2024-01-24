import os
import hashlib
import csv
import sys

def hash_file(filename):
    h = hashlib.blake2b()
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def hash_directory(directory, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["File Path", "BLAKE2 Hash"])
        for root, dirs, files in os.walk(directory):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    file_hash = hash_file(file_path)
                    writer.writerow([file_path, file_hash])
                except (IOError, PermissionError):
                    print(f"Error processing {name}")

if len(sys.argv) != 2:
    print("Usage: python script.py directory_path")
else:
    directory = sys.argv[1]
    hash_directory(directory, 'dir_hashes_blake2.csv')
