import json
import os
import shutil
import sys
import tarfile
import subprocess


# TODO: class and possibly try/catch ?
# TODO: complete documentation
def at_exit(dest, tmp_loc):
    """
    Remove temporary directories
    :param dest: full system path
    :param tmp_loc: full system path
        e.g. /var/tmp/hello
    """
    shutil.rmtree(tmp_loc)
    shutil.rmtree(dest)


def untar(file, dest):
    """
    Extract (.tar) to destination location
    Removes destination if already exists!
    :param file: Source (tar file)
    :param dest: Destination (directory)
    """
    # check if destination exists and delete old
    if os.path.isdir(dest):
        shutil.rmtree(dest)

    tar = tarfile.open(file, "r:")
    tar.extractall(dest)
    tar.close()


def untar_gz(file, dest):
    """
    Extract (.tar.gz) to destination location
    Removes destination if already exists!
    :param file: Source (tar.gz file)
    :param dest: Destination (directory)
    """
    # check if destination exists and delete old
    if os.path.isdir(dest):
        shutil.rmtree(dest)

    tar = tarfile.open(file, "r:gz")
    tar.extractall(dest)
    tar.close()


# TODO: add progress bar
def tarup_gz(dest):
    print("\nCompressing --> " + dest + ".tar.gz")
    with tarfile.open(dest + ".tar.gz", "w:gz") as tar:
        for f in next(os.walk(dest))[1]:
            tar.add(dest + "/" + f, arcname=os.path.basename(dest + "/" + f))


def extract_all_layers(layers, tmp_loc, dest):
    """

    :param layers:
    :param tmp_loc:
    :param dest:
    """
    unpack_tar = tmp_loc + "/blobs/sha256/"
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.mkdir(dest)
    print("\nExtracting layers...")
    for l in layers:
        # for each layer, unpack -> temporary location
        # Copy all files from temp location to destination
        # Remove unnecessary files/folders once finished
        file_name = unpack_tar + l
        print(l + " --> " + dest)
        untar_gz(file_name, tmp_loc + dest)
        os.remove(file_name)
        # TODO: Remove hardcoded path
        bash = ["cp", "-r", (tmp_loc + dest), "/var/tmp"]
        p = subprocess.Popen(bash, stdout=subprocess.PIPE)
        p.communicate()
    tarup_gz(dest)


def get_main_digest_location(loc):
    """
    Obtain main addressable identifier that will defined
    the structure of the container
    :param loc: Path to extracted img save
    :return: Full path + name of digest (json)
    """
    f = open((loc + "/index.json"), "r")
    data = json.load(f)
    digest = (data["manifests"][0]["digest"])[7:]
    f.close()
    return loc + "/blobs/sha256/" + digest


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


# TODO: clean up & verify input
def main(argv):
    if len(argv) < 2 or sys.argv[1] == ("help" or "-h" or "--help"):
        print ("To flatten image saved via img save ...")
        print ("\t<program>.py source destination")
        print ("\tsource -> file (no .tar extension)")
        print ("\tdestination -> desired file name (absolute path!)")
        print ("\tExample: flatten_img.py /home/paul/cchello /var/tmp/newhello")
        exit()

    source = sys.argv[1]
    destination = sys.argv[2]
    print('Source file = ' + source)
    print('Destination file = ' + destination)

    tmp_loc = "/var/tmp/flat_tmp"
    os.mkdir(tmp_loc)

    untar(source, tmp_loc)
    layers = create_layer_list(tmp_loc)
    extract_all_layers(layers, tmp_loc, destination)

    at_exit(destination, tmp_loc)


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    main(sys.argv[1:])
