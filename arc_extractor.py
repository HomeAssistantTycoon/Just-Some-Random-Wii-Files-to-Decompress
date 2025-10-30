#!/usr/bin/env python3
import os
import sys
import struct

def extract_u8_arc(arc_path, output_dir="output"):
    with open(arc_path, "rb") as f:
        data = f.read()

    # Allow headers that start with zeros
    if data[0:4] != b'\x55\xaa\x38\x00':  # standard U8 magic
        print("Warning: nonstandard header detected, attempting extraction anyway")

    # Find root node offset
    # Standard: 0x08 points to the root node
    root_node_offset = struct.unpack(">I", data[0x08:0x0C])[0]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def process_node(offset, parent_path=""):
        node_type = data[offset]  # 0: file, 1: folder
        name_offset = struct.unpack(">I", data[offset+0xC:offset+0x10])[0]
        name_end = data.find(b'\x00', name_offset)
        name = data[name_offset:name_end].decode('utf-8', errors='replace')
        path = os.path.join(parent_path, name)

        if node_type == 0:  # File
            file_start = struct.unpack(">I", data[offset+0x10:offset+0x14])[0]
            file_end   = struct.unpack(">I", data[offset+0x14:offset+0x18])[0]
            content = data[file_start:file_end]
            full_path = os.path.join(output_dir, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as out_file:
                out_file.write(content)
        elif node_type == 1:  # Folder
            child_offset = struct.unpack(">I", data[offset+0x10:offset+0x14])[0]
            child_count  = struct.unpack(">I", data[offset+0x14:offset+0x18])[0]
            for i in range(child_count):
                child_node_offset = struct.unpack(">I", data[child_offset + i*0x14 : child_offset + i*0x14 + 4])[0]
                process_node(child_node_offset, parent_path=path)

    process_node(root_node_offset)
    print(f"Extraction completed into '{output_dir}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_arc.py <file.arc>")
        sys.exit(1)
    arc_file = sys.argv[1]
    extract_u8_arc(arc_file)
