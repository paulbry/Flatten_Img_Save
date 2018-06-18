package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
)

func atexit(tmpdir string) {
	err := os.Remove(tmpdir)
	if err != nil {
		log.Fatal(err)
	}
}

func main() {
	var source, target string
	var version bool
	flag.StringVar(&source, "source", "", "Source of tarball")
	flag.StringVar(&target, "target", "", "Target for flattened tarball")
	flag.BoolVar(&version, "version", false, "Display version")

	flag.Parse()

	if version {
		fmt.Println("Version 0.1")
		return
	}

	// check flag requirements
	// TODO: cleaner way? Check # of arguments
	if source == "" {
		fmt.Println("Please define a source")
		return
	}

	tmpdir, err := ioutil.TempDir("","flat-store")
	if err != nil {
		log.Fatal(err)
		return
	}
}
