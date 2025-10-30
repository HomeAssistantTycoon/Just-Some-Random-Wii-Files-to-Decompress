#!/usr/bin/env python3
import sys
import struct

def detect_compression(file_path):
    with open(file_path, "rb") as f:
        header = f.read(4)

    if len(header) < 4:
        print("File too short to determine compression type.")
        return

    first_byte = header[0]

    if first_byte == 0x10:
        print("Detected: LZ10 compression (Wii common)")
        if len(header) >= 4:
            # LZ10 stores uncompressed size in bytes 1-3 (big endian)
            uncompressed_size = (header[1] << 16) | (header[2] << 8) | header[3]
            print(f"Uncompressed size: {uncompressed_size} bytes")
    elif first_byte == 0x11:
        print("Detected: LZ11 compression (less common)")
    elif header.startswith(b"LZ77"):
        print("Detected: LZ77 compression")
    else:
        print(f"Unknown or uncompressed file. First 4 bytes: {header.hex()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lz10_extractor.py <file>")
        sys.exit(1)

    detect_compression(sys.argv[1])
