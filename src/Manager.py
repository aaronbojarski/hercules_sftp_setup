from src.Hercules import Hercules
from src.Filemanager import Filemanager
from src.File import FileStatus
import pysftp
import os
from time import sleep
from alive_progress import alive_bar


class Manager:
    def __init__(self, target_ip, username, ssh_key_file, temp_dir, hercules_path) -> None:
        self.sftp_connection = pysftp.Connection(target_ip, username=username, private_key=ssh_key_file)
        self.filemanager = Filemanager(temp_dir)
        self.hercules = Hercules(hercules_path)

    def start(self, target_dir):
        while True:
            with self.sftp_connection.cd(target_dir):
                self.check_for_new_files()
                self.copy_files()
            self.send_files()
            self.cleanup()
            sleep(5)

    def check_for_new_files(self):
        current_files = self.sftp_connection.listdir()
        for f in current_files:
            metadata = self.sftp_connection.stat(f)
            self.filemanager.update(f, metadata.st_size, metadata.st_mtime)
        self.filemanager.cleanup_state(current_files)

    def copy_files(self):
        for file in self.filemanager.files:
            if file.status == FileStatus.READY:
                with alive_bar(file.size, manual=True) as bar:
                    self.sftp_connection.get(file.name, file.local_path, callback=(lambda a, b: bar(a / b)))
                file.status = FileStatus.COPIED

    def send_files(self):
        for file in self.filemanager.files:
            if file.status == FileStatus.COPIED:
                self.hercules.transfer(file)
                file.status = FileStatus.SENT

    def cleanup(self):
        for file in self.filemanager.files:
            if file.status == FileStatus.SENT and os.path.isfile(file.local_path):
                print(f"Removing temp file: {file.local_path}")
                os.remove(file.local_path)
                file.status = FileStatus.DELETED
