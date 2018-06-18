import json
import os
import shutil
import sys
import tarfile
import subprocess


#TODO: document (class?)

# cleanup
def at_exit(dest):
    shutil.rmtree(os.getcwd() + "/tmp")
    shutil.rmtree(dest)
    shutil.rmtree("/tmp/flat")


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
    tmp_loc = tmp_loc + "/blobs/sha256/"
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.mkdir(dest)
    print("\nExtracting layers...")
    for l in layers:
        file_name = tmp_loc + l
        print(l + " --> " + dest)
        untar_gz(file_name, "/tmp/flat" + dest)
        os.remove(file_name)
        bash = ["cp", "-r", ("/tmp/flat" + dest), "/home/paul/"]
        p = subprocess.Popen(bash, stdout=subprocess.PIPE)
        p.communicate()
    # TODO: remove (or move) tmp location
    with tarfile.open(dest + ".tar.gz", "w:gz") as tar:
        tar.add(dest, arcname=os.path.basename(dest))
        # TODO: add progress bar

def get_main_digest_location(loc):
    f = open((loc + "/index.json"), "r")
    data = json.load(f)
    digest = (data["manifests"][0]["digest"])[7:]
    f.close()
    return loc + "/blobs/sha256/" + digest


# create ordered list for unpacking
def create_layer_list(loc):
    print("\nCreating ordered list of layers:")
    layers = []
    f = open(get_main_digest_location(loc), "r")
    data = json.load(f)
    data = data["layers"]
    for l in range(len(data)):
        lay = (data[l]["digest"])[7:]
        print("Layer " + str(l) + ": " + lay)
        layers.append(lay)
    f.close()
    return layers


def main(argv):
    if len(argv) < 2 or sys.argv[1] == ("help" or "-h" or "--help"):
        print ("To flatten image saved via img save ...")
        print ("\t<program>.py source destination")
        print ("\tsource -> file (no need for .tar extension)")
        print ("\tdestination -> desired file name")
        exit()
    source = sys.argv[1]
    destination = sys.argv[2]

    # TODO: clean up & verify input

    print('Source file = ' + source)
    print('Destination file = ' + destination)

    tmp_loc = os.getcwd() + "/tmp"

    untar(source, tmp_loc)
    layers = create_layer_list(tmp_loc)
    extract_all_layers(layers, tmp_loc, destination)

    at_exit(destination)


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    main(sys.argv[1:])
