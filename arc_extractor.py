#!/usr/bin/env python3
import os
import sys
import struct

def extract_arc(arc_file, out_dir="output"):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open(arc_file, "rb") as f:
        # Read header
        magic = f.read(4)
        if magic != b'ARCH':
            print("Not a valid ARC file!")
            return

        # Number of files
        num_files, = struct.unpack(">I", f.read(4))
        # File table offset
        table_offset, = struct.unpack(">I", f.read(4))

        # Seek to file table
        f.seek(table_offset)

        file_entries = []
        for _ in range(num_files):
            name_bytes = f.read(32)
            name = name_bytes.split(b'\x00')[0].decode("utf-8")
            offset, size = struct.unpack(">II", f.read(8))
            file_entries.append((name, offset, size))

        # Extract files
        for name, offset, size in file_entries:
            f.seek(offset)
            data = f.read(size)
            out_path = os.path.join(out_dir, name)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "wb") as out_file:
                out_file.write(data)
            print(f"Extracted: {name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python arc_extractor.py <file.arc> [output_dir]")
        sys.exit(1)
    arc_file = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    extract_arc(arc_file, out_dir)
