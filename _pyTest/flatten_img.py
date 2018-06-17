import json
import os
import shutil
import sys
import tarfile


# cleanup
def at_exit():
    shutil.rmtree(os.getcwd() + "\\tmp")


# untar file
def untar(file, dest):
    # check if destination exists and delete old
    if os.path.isdir(dest):
        shutil.rmtree(dest)

    tar = tarfile.open(file, "r:")
    tar.extractall(dest)
    tar.close()

# untar file
def untar_gz(file, dest):
    # check if destination exists and delete old
    if os.path.isdir(dest):
        shutil.rmtree(dest)

    tar = tarfile.open(file, "r:gz")
    tar.extractall(dest)
    tar.close()


def extract_all_layers(layers, tmp_loc, dest):
    tmp_loc = tmp_loc + "\\blobs\\sha256\\"
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.mkdir(dest)
    print("\nExtracting layers...")
    for l in layers:
        file_name = tmp_loc + l
        os.rename(tmp_loc + l, file_name)
        print(l + " --> " + dest)
        untar_gz(file_name, dest)
    # TODO: tarball final

def get_main_digest_location(loc):
    f = open((loc + "\\index.json"), "r")
    data = json.load(f)
    digest = (data["manifests"][0]["digest"])[7:]
    f.close()
    return loc + "\\blobs\\sha256\\" + digest


# create ordered list for unpacking
def create_layer_list(loc):
    print("\nCreating orderd list of layers:")
    layers = []
    f = open(get_main_digest_location(loc), "r")
    data = json.load(f)
    data = data["layers"]
    for l in range(len(data)):
        lay = (data[l]["digest"])[7:]
        print("Layer " + str(l)  + ": " + lay)
        layers.append(lay)
    f.close()
    return layers


def main(argv):
    if sys.argv[1] == ("help" or "-h" or "--help"):
        print ("To flatten image saved via img save ...")
        print ("<program>.py source destination")
        print ("source -> file (no need for .tar extension)")
        print ("destination -> desired file name")
    source = sys.argv[1]
    destination = sys.argv[2]

    # TODO: clean up & verify input

    print('Source file = ' + source)
    print('Destination file = ' + destination)

    tmp_loc = os.getcwd() + "\\tmp"

    untar(source, tmp_loc)
    layers = create_layer_list(tmp_loc)
    extract_all_layers(layers, tmp_loc, destination)

    at_exit()


if __name__ == "__main__":
    main(sys.argv[1:])