import os
import struct

def extract_arc(arc_path):
    """
    Extracts files from a custom ARC archive.
    - Parses the archive header (big-endian format).
    - Writes all extracted files to the 'output/' directory.
    - Falls back to signature scanning if header parsing is incomplete.
    """
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)

    with open(arc_path, 'rb') as f:
        header = f.read(64)
        if len(header) < 64:
            raise ValueError("ARC file header is too short")

        # Interpret header fields (big-endian)
        num_dirs         = struct.unpack('>H', header[10:12])[0]  # e.g. 17
        num_files        = struct.unpack('>H', header[14:16])[0]  # e.g. 88
        dir_table_offset = struct.unpack('>I', header[28:32])[0]
        file_table_offset= struct.unpack('>I', header[60:64])[0]
        # Heuristic: bytes 0x34–0x37 (offset 52–55) appear to be data offset
        data_offset      = struct.unpack('>I', header[52:56])[0]

        print(f"Detected {num_dirs} dirs, {num_files} files. "
              f"Dir table @ {dir_table_offset}, file table @ {file_table_offset}, data @ {data_offset}.")

        # Determine file size
        f.seek(0, os.SEEK_END)
        file_size = f.tell()

        # Validate data_offset
        if data_offset < 64 or data_offset > file_size:
            print("Warning: data offset out of range, defaulting to 64.")
            data_offset = 64

        # Read the data segment
        f.seek(data_offset)
        data = f.read()

        # Heuristic: find common file signatures in data
        signatures = {
            b'\x89PNG\r\n\x1a\n': '.png',
            b'\xff\xd8\xff': '.jpg',
            b'PK\x03\x04': '.zip',
            b'RIFF': '.wav',  # also marks WAV/AVI
            b'GIF8': '.gif',
            b'BM': '.bmp'
        }
        offsets = {data_offset}  # always include start of data
        extensions = {}

        for sig, ext in signatures.items():
            pos = data.find(sig)
            while pos != -1:
                off = data_offset + pos
                offsets.add(off)
                extensions[off] = ext
                pos = data.find(sig, pos+1)

        # If no signatures found, treat entire data as one binary chunk
        if len(offsets) == 1:
            offsets = {data_offset}
            extensions[data_offset] = '.bin'

        # Sort offsets and add file end sentinel
        offsets = sorted(offsets)
        offsets.append(file_size)

        # Extract each file chunk
        for i in range(len(offsets)-1):
            start = offsets[i]
            end   = offsets[i+1]
            ext   = extensions.get(start, '.bin')
            length = end - start
            f.seek(start)
            chunk = f.read(length)

            out_name = f"{i+1:03}{ext}"
            out_path = os.path.join('output', out_name)
            with open(out_path, 'wb') as out_f:
                out_f.write(chunk)
            print(f"Extracted file {i+1}: {out_path} ({length} bytes)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python extract_arc.py <archive_file.arc>")
    else:
        extract_arc(sys.argv[1])
