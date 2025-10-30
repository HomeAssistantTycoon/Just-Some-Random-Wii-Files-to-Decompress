#!/usr/bin/env python3
import os
import sys
import struct

ARC_FILE = sys.argv[1] if len(sys.argv) > 1 else "wwwlib-rvl.arc"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(ARC_FILE, "rb") as f:
    data = f.read()

# Parse file table
# Adjust this according to your ARC structure if needed
# We'll assume 8-byte entries: 4 bytes offset, 4 bytes size
file_entries = []

# Start parsing after the first 16 bytes (you can tweak this if needed)
cursor = 0x10
while cursor + 8 <= len(data):
    start, size = struct.unpack(">II", data[cursor:cursor+8])
    # Ignore empty entries
    if start == 0 and size == 0:
        cursor += 8
        continue
    if start + size > len(data):
        break
    file_entries.append((start, size))
    cursor += 8

# Extract files
for i, (start, size) in enumerate(file_entries):
    file_data = data[start:start+size]
    out_path = os.path.join(OUTPUT_DIR, f"file_{i}.bin")
    with open(out_path, "wb") as out_file:
        out_file.write(file_data)

print(f"Extracted {len(file_entries)} files to {OUTPUT_DIR}/")
