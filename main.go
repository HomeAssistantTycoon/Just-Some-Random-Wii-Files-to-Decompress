package main

import (
	"fmt"
	"os"
	"lz10"
)

func main() {
	if len(os.Args) < 3 {
		fmt.Println("Usage: lz10decompress <input> <output>")
		os.Exit(1)
	}

	inFile := os.Args[1]
	outFile := os.Args[2]

	data, err := os.ReadFile(inFile)
	if err != nil {
		panic(err)
	}

	out, err := lz10.Decompress(data)
	if err != nil {
		panic(err)
	}

	os.WriteFile(outFile, out, 0644)
	fmt.Println("✅ Decompressed:", outFile)
}
