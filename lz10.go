package lz10

import (
	"bytes"
	"encoding/binary"
	"errors"
)

const (
	FileMagic     = 0x10
	CompressedMin = 4
	CompressedMax = 128 * 1024 * 1024
)

var (
	ErrCompressedTooSmall = errors.New("compressed data too small")
	ErrCompressedTooLarge = errors.New("compressed data too large")
	ErrInvalidMagic       = errors.New("invalid magic byte")
)

// Decompress function (your same code)
func Decompress(data []byte) ([]byte, error) {
	compressed := bytes.NewBuffer(data)

	if CompressedMin > compressed.Len() {
		return nil, ErrCompressedTooSmall
	}
	if compressed.Len() > CompressedMax {
		return nil, ErrCompressedTooLarge
	}
	if compressed.Next(1)[0] != FileMagic {
		return nil, ErrInvalidMagic
	}

	fileSize := compressed.Next(3)
	header := make([]byte, 4)
	copy(header[:], fileSize[:])
	originalLen := binary.LittleEndian.Uint32(header)

	decompressed := new(bytes.Buffer)

	for decompressed.Len() < int(originalLen) {
		b := compressed.Next(1)[0]
		_bits := bits(b)
		for _, bit := range _bits {
			if bit == 1 {
				_val := compressed.Next(2)
				val := binary.BigEndian.Uint16(_val)
				count := (val >> 0xC) + 3
				disp := (val & 0xFFF) + 1
				for i := 0; i < int(count); i++ {
					length := decompressed.Len()
					decompressed.WriteByte(decompressed.Bytes()[length-int(disp)])
				}
			} else {
				decompressed.WriteByte(compressed.Next(1)[0])
			}
			if int(originalLen) <= decompressed.Len() {
				break
			}
		}
	}

	return decompressed.Bytes(), nil
}

func bits(passed byte) [8]byte {
	return [8]byte{
		(passed >> 7) & 1,
		(passed >> 6) & 1,
		(passed >> 5) & 1,
		(passed >> 4) & 1,
		(passed >> 3) & 1,
		(passed >> 2) & 1,
		(passed >> 1) & 1,
		passed & 1,
	}
}
