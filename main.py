from Hercules import Hercules
import pysftp
import os
from time import sleep
from alive_progress import alive_bar

USERNAME = "moltres"
SSH_KEY_FILE = ...
TARGET_IP = ...
TARGET_DIR = "/home/moltres/aaron/test"
OUT_DIR = "./out/"


def check_for_new_files(files, sftp):
    current_files = sftp.listdir()
    for f in current_files:
        size = sftp.stat(f).st_size
        mtime = sftp.stat(f).st_mtime

        if f in files:
            if size != files[f]["size"] or mtime != files[f]["mtime"]:
                files[f] = {"mtime": mtime, "size": size, "copied": False, "sent": False}
        else:
            print(f"Found new file: {f}")
            files[f] = {"mtime": mtime, "size": size, "copied": False, "sent": False}


def copy_files(files, sftp):
    for name, metadata in files.items():
        if metadata["copied"]:
            continue
        with alive_bar(metadata["size"], manual=True) as bar:
            sftp.get(name, OUT_DIR + name, callback=(lambda a, b: bar(a / b)))
            files[name]["copied"] = True


def send_files(files, hercules):
    for name, metadata in files.items():
        if not metadata["sent"]:
            hercules.transfer("CERN", name)
            files[name]["sent"] = True


def cleanup(files):
    for name, metadata in files.items():
        if metadata["sent"] and os.path.isfile(OUT_DIR + name):
            print(f"Removing temp file: {name}")
            os.remove(OUT_DIR + name)


def loop(sftp, hercules):
    files = {}
    while True:
        with sftp.cd(TARGET_DIR):
            check_for_new_files(files, sftp)
            copy_files(files, sftp)
        send_files(files, hercules)
        cleanup(files)
        sleep(1)


def main():
    hercules = Hercules("hercules_path")
    with pysftp.Connection(TARGET_IP, username=USERNAME, private_key=SSH_KEY_FILE) as sftp:
        print("CONNECTED")
        loop(sftp, hercules)


if __name__ == "__main__":
    main()
