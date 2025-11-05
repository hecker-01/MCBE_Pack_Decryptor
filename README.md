# MCBE_Pack_Decryptor
A Python CLI that decrypts encrypted Minecraft marketplace packs (Valid key needed)

## Usage
1. Install the "pycryptodome" package from pip
`pip install pycryptodome`
2. Make sure you have the right files in the right locations.
![Correct file structure](https://github.com/user-attachments/assets/9a80dced-f6c9-4ab9-9ff9-bac2b89b04dd)
```
folder/
├── encrypted-resource-pack/
|   ├── contents.json
│   └── Other resouce-pack files...
├── encrypted-resource-pack.key (same name as folder, with a .key file extension)
└── mcbe_pack_decryptor.py
```
3. Start the script
`python3 mcbe_pack_decryptor.py`
4. Enable verbose logging to see all files get decrypted (off by default)
5. Watch the magic happen:
![Example output](https://github.com/user-attachments/assets/c069f0ed-1039-40aa-9773-f45d0d242b58)
