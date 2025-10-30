#!/usr/bin/env python3
import sys
import os
import struct

def parse_u8(data, base_path="output"):
    # Create output folder if it doesn't exist
    os.makedirs(base_path, exist_ok=True)

    # Header
    magic = data[0:4]
    if magic != b'U8\x00\x00':
        raise ValueError("Not a U8 archive")

    # Header offsets
    header_size = struct.unpack(">I", data[4:8])[0]
    data_offset = struct.unpack(">I", data[8:12])[0]
    root_node_offset = 12

    # Recursively parse directory
    def parse_node(offset, path):
        node_type = data[offset]
        name_offset = struct.unpack(">I", data[offset+1:offset+4])[0]
        size = struct.unpack(">I", data[offset+4:offset+8])[0]
        data_off = struct.unpack(">I", data[offset+8:offset+12])[0]

        # Name
        name_end = data.find(b'\x00', name_offset)
        name = data[name_offset:name_end].decode('utf-8')
        full_path = os.path.join(path, name)

        if node_type == 0x00:  # File
            file_data = data[data_off:data_off+size]
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(file_data)
        elif node_type == 0x01:  # Directory
            os.makedirs(full_path, exist_ok=True)
            # The next 4 bytes after size points to child node count
            child_count = struct.unpack(">I", data[offset+12:offset+16])[0]
            child_offset = offset + 16
            for i in range(child_count):
                parse_node(child_offset + i*32, full_path)

    parse_node(root_node_offset, base_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_arc.py <file.arc>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    parse_u8(data)
    print(f"All files extracted to output/")
