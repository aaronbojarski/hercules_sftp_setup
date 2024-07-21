from Hercules import Hercules
from Filemanager import Filemanager
from File import FileStatus
import pysftp
import os
from time import sleep
from alive_progress import alive_bar

USERNAME = "moltres"
SSH_KEY_FILE = ...
TARGET_IP = ...
TARGET_DIR = "/home/moltres/aaron/test"
TEMP_DIR = "./out/"


def check_for_new_files(filemanager: Filemanager, sftp):
    current_files = sftp.listdir()
    for f in current_files:
        metadata = sftp.stat(f)
        filemanager.update(f, metadata.st_size, metadata.st_mtime)
    filemanager.cleanup_state(current_files)


def copy_files(filemanager: Filemanager, sftp):
    for file in filemanager.files:
        if file.status == FileStatus.READY:
            with alive_bar(file.size, manual=True) as bar:
                sftp.get(file.name, file.local_path, callback=(lambda a, b: bar(a / b)))
            file.status = FileStatus.COPIED


def send_files(filemanager: Filemanager, hercules: Hercules):
    for file in filemanager.files:
        if file.status == FileStatus.COPIED:
            hercules.transfer(file)
            file.status = FileStatus.SENT


def cleanup(filemanager: Filemanager):
    for file in filemanager.files:
        if file.status == FileStatus.SENT and os.path.isfile(file.local_path):
            print(f"Removing temp file: {file.local_path}")
            os.remove(file.local_path)
            file.status = FileStatus.DELETED


def start_loop(sftp, hercules: Hercules, filemanager: Filemanager):
    while True:
        with sftp.cd(TARGET_DIR):
            check_for_new_files(filemanager, sftp)
            copy_files(filemanager, sftp)
        send_files(filemanager, hercules)
        cleanup(filemanager)
        sleep(5)


def main():
    hercules = Hercules("hercules_path")
    filemanager = Filemanager(TEMP_DIR)
    with pysftp.Connection(TARGET_IP, username=USERNAME, private_key=SSH_KEY_FILE) as sftp:
        print("CONNECTED")
        start_loop(sftp, hercules, filemanager)


if __name__ == "__main__":
    main()
