#!/usr/bin/env python3
import sys
from struct import unpack

class DecompressionError(ValueError):
    pass

# ----------------------------
# LZSS decompression helpers
# ----------------------------
def bits(byte):
    return ((byte >> 7) & 1,
            (byte >> 6) & 1,
            (byte >> 5) & 1,
            (byte >> 4) & 1,
            (byte >> 3) & 1,
            (byte >> 2) & 1,
            (byte >> 1) & 1,
            byte & 1)

def decompress_raw_lzss10(indata, decompressed_size):
    data = bytearray()
    it = iter(indata)
    def writebyte(b): data.append(b)
    def copybyte(): data.append(next(it))
    def readbyte(): return next(it)
    def readshort(): return (readbyte() << 8) | readbyte()

    while len(data) < decompressed_size:
        b = readbyte()
        flags = bits(b)
        for flag in flags:
            if flag == 0:
                copybyte()
            else:
                sh = readshort()
                count = (sh >> 12) + 3
                disp = (sh & 0xFFF) + 1
                for _ in range(count):
                    data.append(data[-disp])
            if len(data) >= decompressed_size:
                break
    if len(data) != decompressed_size:
        raise DecompressionError("decompressed size mismatch")
    return data

def decompress_raw_lzss11(indata, decompressed_size):
    data = bytearray()
    it = iter(indata)
    def writebyte(b): data.append(b)
    def copybyte(): data.append(next(it))
    def readbyte(): return next(it)

    while len(data) < decompressed_size:
        b = readbyte()
        flags = bits(b)
        for flag in flags:
            if flag == 0:
                copybyte()
            else:
                b1 = readbyte()
                indicator = b1 >> 4
                if indicator == 0:
                    b2 = readbyte()
                    count = ((b1 << 4) | (b2 >> 4)) + 0x11
                    disp = ((b2 & 0xF) << 8) + readbyte() + 1
                elif indicator == 1:
                    b2 = readbyte()
                    b3 = readbyte()
                    count = (((b1 & 0xF) << 12) | (b2 << 4) | (b3 >> 4)) + 0x111
                    disp = ((b3 & 0xF) << 8) + readbyte() + 1
                else:
                    count = indicator + 1
                    disp = ((b1 & 0xF) << 8) + readbyte() + 1
                for _ in range(count):
                    data.append(data[-disp])
            if len(data) >= decompressed_size:
                break
    if len(data) != decompressed_size:
        raise DecompressionError("decompressed size mismatch")
    return data

# ----------------------------
# LZ file handling
# ----------------------------
def decompress_file(f):
    header = f.read(4)
    if header[0] == 0x10:
        decompress_raw = decompress_raw_lzss10
    elif header[0] == 0x11:
        decompress_raw = decompress_raw_lzss11
    else:
        raise DecompressionError("Not LZ10/LZ11 compressed")
    decompressed_size, = unpack("<L", header[1:] + b'\x00')
    data = f.read()
    return decompress_raw(data, decompressed_size)

# ----------------------------
# Main script
# ----------------------------
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
