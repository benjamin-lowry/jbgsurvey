from json import load
from glob import glob
from os import makedirs
from os.path import join, basename, dirname
from sys import argv, stderr

def get_content_ids(file):
    return [content["id"] for content in load(file)["content"]]

def get_all_content_ids(manifest, content_path):
    content_ids = {}
    for content_type in load(manifest)["types"]:
        for language_folder in glob(join(content_path, "*/")):
            with open(join(language_folder, content_type + ".jet"), "r") as f:
                content_ids[basename(dirname(language_folder))] = get_content_ids(f)
    return content_ids

if __name__ == "__main__":
    if len(argv) != 2:
        stderr.write("usage: " + argv[0] + " [path to manifest.jet]\n")
        exit(1)
    makedirs("content_ids", exist_ok=True)
    with open(argv[1], "r") as manifest:
        for language, contents in get_all_content_ids(manifest, dirname(argv[1])).items():
            with open(join("content_ids", language + ".txt"), "w") as ids_file:
                for content_id in contents: ids_file.write(content_id + "\n")
