import sys
import struct

def lz10_decompress(data: bytes) -> bytes:
    # Validate header
    if len(data) < 4 or data[0] != 0x10:
        raise ValueError("Not an LZ10-compressed file")

    # Decompressed size (24-bit little endian)
    decompressed_size = struct.unpack("<I", data[0:4] + b'\x00')[0] >> 8
    output = bytearray()
    pos = 4

    while len(output) < decompressed_size:
        if pos >= len(data):
            break

        flags = data[pos]
        pos += 1

        for i in range(8):
            if flags & (0x80 >> i):
                # Compressed block
                if pos + 1 >= len(data):
                    break
                b1 = data[pos]
                b2 = data[pos + 1]
                pos += 2
                disp = ((b1 & 0xF) << 8) | b2
                length = (b1 >> 4) + 3
                for j in range(length):
                    output.append(output[-disp - 1])
            else:
                # Literal byte
                if pos >= len(data):
                    break
                output.append(data[pos])
                pos += 1

            if len(output) >= decompressed_size:
                break

    return bytes(output)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lz10_extractor.py <file.lz10>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = input_path + ".decompressed"

    with open(input_path, "rb") as f:
        compressed_data = f.read()

    decompressed_data = lz10_decompress(compressed_data)

    with open(output_path, "wb") as f:
        f.write(decompressed_data)

    print(f"Decompressed successfully → {output_path}")
