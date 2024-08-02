from src.Hercules import Hercules
from src.Filemanager import Filemanager
from src.File import FileStatus
from src.Config import Config
import pysftp
from paramiko.ssh_exception import SSHException
import os
from time import sleep
from alive_progress import alive_bar

MAX_RECONNECTION_RETRIES = 5


class Manager:
    def __init__(self, config: Config) -> None:
        self.connection_retries = 0
        self.state_file = config.temp_dir + "/state.json"
        self.target_ip = config.target_ip
        self.username = config.username
        self.ssh_key_file = config.ssh_key_file
        self.sftp_connection = pysftp.Connection(self.target_ip, username=self.username, private_key=self.ssh_key_file)
        self.filemanager = Filemanager(config.temp_dir)
        self.filemanager.load_state(self.state_file)
        self.hercules = Hercules(config)

    def start(self, target_dir: str):
        while self.connection_retries < MAX_RECONNECTION_RETRIES:
            try:
                with self.sftp_connection.cd(target_dir):
                    self.check_for_new_files()
                    self.copy_files()
            except (SSHException, OSError, AttributeError) as e:
                print(e)
                self.connection_retries += 1
                print(f"Trying to reconnect. Retry {self.connection_retries}/{MAX_RECONNECTION_RETRIES}")
                try:
                    self.sftp_connection = pysftp.Connection(
                        self.target_ip, username=self.username, private_key=self.ssh_key_file
                    )
                except Exception as e:
                    print(e)

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
        self.filemanager.save_state(self.state_file)
