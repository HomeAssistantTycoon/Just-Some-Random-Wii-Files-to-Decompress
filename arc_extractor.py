#!/usr/bin/env python3
import os
import sys
import struct

def read_u32(f):
    return struct.unpack(">I", f.read(4))[0]  # Big endian, adjust if needed

def extract_arc(arc_file, out_dir="output"):
    os.makedirs(out_dir, exist_ok=True)
    with open(arc_file, "rb") as f:
        data = f.read()
    
    # Simple heuristic based on first bytes you provided
    # Adjust offsets if necessary
    file_count = struct.unpack(">I", data[0x0C:0x10])[0]  # guess file count
    print(f"Detected {file_count} files (may be approximate)")

    # Start scanning after header (assume header is 0x40 bytes for now)
    ptr = 0x40
    idx = 0
    while ptr < len(data):
        if ptr + 8 > len(data):
            break
        # try to read file offset/size (heuristic)
        file_offset = struct.unpack(">I", data[ptr:ptr+4])[0]
        file_size = struct.unpack(">I", data[ptr+4:ptr+8])[0]
        ptr += 8

        # sanity check
        if file_offset + file_size > len(data):
            break
        if file_size == 0:
            continue

        # dump file
        filename = os.path.join(out_dir, f"file_{idx:04d}.bin")
        with open(filename, "wb") as out_f:
            out_f.write(data[file_offset:file_offset+file_size])
        print(f"Extracted {filename}, {file_size} bytes")
        idx += 1

    print(f"Extraction completed into '{out_dir}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_arc.py <file.arc>")
        sys.exit(1)

    extract_arc(sys.argv[1])
