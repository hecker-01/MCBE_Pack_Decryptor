import os
import json
import shutil
import sys

try:
    from Crypto.Cipher import AES
except ImportError:
    print("Error: pycryptodome module is not installed.")
    print("Please install it using: pip install pycryptodome")
    sys.exit(1)

def log(message):
    if VERBOSE:
        print(message)

def aes_cfb_decrypt(data, key, iv):
    try:
        cipher = AES.new(key, AES.MODE_CFB, iv=iv)
        return cipher.decrypt(data)
    except Exception as e:
        print(f"\033[91mDecryption failed: {e}\033[0m")
        return None

def load_json(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        print(f"\033[91mError parsing JSON: {e}\033[0m")
        return None

def validate_key(key):
    if len(key) != 32:
        print("\033[91mError: Key must be 32 bytes long.\033[0m")
        return False
    return True

def decrypt_file(input_path, output_path, key):
    with open(input_path, 'rb') as f:
        data = f.read()
    decrypted_data = aes_cfb_decrypt(data, key, key[:16])
    if decrypted_data is not None:
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        log(f"Decrypted: {input_path}")
    else:
        print(f"\033[91mError decrypting {input_path}, copying as is.\033[0m")
        shutil.copy2(input_path, output_path)

def decrypt_folder(decryption_key, input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    contents_json_path = os.path.join(input_folder, 'contents.json')
    
    if not os.path.isfile(contents_json_path):
        print("\033[91mError: Missing contents.json in input folder. (Already decrypted?)\033[0m")
        sys.exit(1)
    
    with open(contents_json_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = aes_cfb_decrypt(encrypted_data[0x100:], decryption_key, decryption_key[:16])
    
    if not decrypted_data:
        print("\033[91mError: Failed to decrypt contents.json!\033[0m")
        sys.exit(1)
    
    try:
        contents = load_json(decrypted_data.decode('utf-8'))
    except UnicodeDecodeError:
        print("\033[91mError: Invalid key, unable to decode contents.json.\033[0m")
        sys.exit(1)
    
    content_map = {info["path"]: info.get("key", "").encode() for info in contents.get("content", [])}

    print(f"Processing {input_folder}...")
    
    for root, _, files in os.walk(input_folder):
        if "subpacks" in os.path.relpath(root, input_folder).split(os.sep):
            continue  # Ignore subpacks initially
        
        new_root = os.path.join(output_folder, os.path.relpath(root, input_folder))
        os.makedirs(new_root, exist_ok=True)
        
        for file in files:
            if file in ['contents.json', '.DS_Store']:
                continue
            
            input_path = os.path.join(root, file)
            output_path = os.path.join(new_root, file)
            relative_path = os.path.relpath(input_path, input_folder).replace("\\", "/")
            
            key = content_map.get(relative_path, b"")
            if key:
                decrypt_file(input_path, output_path, key)
            else:
                log(f"No key for {relative_path}, copying as is.")
                shutil.copy2(input_path, output_path)
    
    print(f"✓ Successfully processed {input_folder}.")

def decrypt_subpacks(decryption_key, subpack_folder, output_folder):
    for subpack in filter(lambda d: os.path.isdir(os.path.join(subpack_folder, d)), os.listdir(subpack_folder)):
        decrypt_folder(decryption_key, os.path.join(subpack_folder, subpack), os.path.join(output_folder, 'subpacks', subpack))

def get_decryption_key(input_folder):
    key_file = f"{input_folder}.key"
    if os.path.isfile(key_file):
        with open(key_file, 'rb') as f:
            key = f.read().strip()
        print(f"Key loaded from {key_file}")
    else:
        key = input("Pack key (32 characters): ").encode()
    
    if not validate_key(key):
        key = input("Enter pack key manually (32 characters): ").encode()
        if not validate_key(key):
            print("\033[91mError: Invalid key. Exiting.\033[0m")
            sys.exit(1)
    return key

if __name__ == "__main__":
    print("┏┻┓┳┳┓┏┓ ┏┓┳┓  MCBE_Pack_Decryptor\n┗━┓┃┃┃┃  ┃┃┃┃  Version 1.0\n┗┳┛┛ ┗┗┛━┣┛┻┛  Made by @hecker-01\n")


    VERBOSE = input("Enable verbose logging? (y/N): ").strip().lower() == 'y'
    input_folder = input("Input folder (should be in the same directory as this script): ").strip()
    
    if not os.path.isdir(input_folder):
        print(f"\033[91mError: Input folder ./{input_folder} does not exist.\033[0m")
        sys.exit(1)
    
    key = get_decryption_key(input_folder)
    output_folder = f"{input_folder}-decrypted"
    decrypt_folder(key, input_folder, output_folder)
    
    subpack_folder = os.path.join(input_folder, "subpacks")
    if os.path.isdir(subpack_folder):
        decrypt_subpacks(key, subpack_folder, output_folder)
    else:
        log("No subpacks found.")
    
    print(f"\033[92mDecryption complete! Output folder: {os.path.abspath(output_folder)}\033[0m")
