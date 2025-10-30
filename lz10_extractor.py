#!/usr/bin/env python3
import sys
from struct import unpack
from lz10_extractor import decompress_file  # your existing decompressor functions

def main():
    if len(sys.argv) != 3:
        print("Usage: python lz10_to_arc.py <input.lz10/lz7> <output.arc>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        with open(input_file, "rb") as f:
            decompressed_data = decompress_file(f)

        with open(output_file, "wb") as out:
            out.write(decompressed_data)

        print(f"Success: Decompressed {input_file} → {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
