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
        self.sftp_connection = pysftp.Connection(
            config.ldh_ip, username=config.ldh_username, private_key=config.ldh_ssh_key_file
        )
        self.outgoing_state_file = config.lth_out_temp_dir + "/outgoing_state.json"
        self.incoming_state_file = config.lth_hercules_rcv_dir + "/incoming_state.json"
        self.outgoing_filemanager = Filemanager(config.lth_out_temp_dir)
        self.outgoing_filemanager.load_state(self.outgoing_state_file)
        self.incoming_filemanager = Filemanager(config.lth_hercules_rcv_dir)
        self.incoming_filemanager.load_state(self.incoming_state_file)
        self.hercules = Hercules(config)
        self.config = config

    def start(self):
        while self.connection_retries < MAX_RECONNECTION_RETRIES:
            try:
                with self.sftp_connection.cd(self.config.ldh_observe_dir):
                    self.check_outgoing_files()
                    self.copy_outgoing_files()
                with self.sftp_connection.cd(self.config.ldh_write_dir):
                    self.check_incoming_files()
                    self.copy_incoming_files()
            except (SSHException, OSError, AttributeError) as e:
                print(e)
                self.connection_retries += 1
                print(f"Trying to reconnect. Retry {self.connection_retries}/{MAX_RECONNECTION_RETRIES}")
                try:
                    self.sftp_connection = pysftp.Connection(
                        self.config.ldh_ip, username=self.config.ldh_username, private_key=self.config.ldh_ssh_key_file
                    )
                except Exception as e:
                    print(e)

            self.send_outgoing_files()
            self.check_sending_status()
            self.remove_incoming_temp_files()
            self.remove_outgoing_temp_files()
            sleep(3)

    def check_outgoing_files(self):
        current_files = self.sftp_connection.listdir()
        for f in current_files:
            metadata = self.sftp_connection.stat(f)
            self.outgoing_filemanager.update(f, metadata.st_size, metadata.st_mtime)
        self.outgoing_filemanager.cleanup_state(current_files)

    def copy_outgoing_files(self):
        for file in self.outgoing_filemanager.files:
            if file.status == FileStatus.READY:
                with alive_bar(file.size, manual=True) as bar:
                    self.sftp_connection.get(file.name, file.local_path, callback=(lambda a, b: bar(a / b)))
                file.status = FileStatus.COPIED

    def check_incoming_files(self):
        current_files = os.listdir(self.config.lth_hercules_rcv_dir)
        for f in current_files:
            metadata = os.stat(self.config.lth_hercules_rcv_dir + "/" + f)
            self.incoming_filemanager.update(f, metadata.st_size, metadata.st_mtime)
        self.incoming_filemanager.cleanup_state(current_files)

    def copy_incoming_files(self):
        for file in self.incoming_filemanager.files:
            if file.status == FileStatus.READY:
                with alive_bar(file.size, manual=True) as bar:
                    self.sftp_connection.put(file.local_path, file.name, callback=(lambda a, b: bar(a / b)))
                file.status = FileStatus.COPIED

    def send_outgoing_files(self):
        for file in self.outgoing_filemanager.files:
            if file.status == FileStatus.COPIED:
                self.hercules.transfer(file)
                file.status = FileStatus.SENDING

    def check_sending_status(self):
        for file in self.outgoing_filemanager.files:
            if file.status == FileStatus.SENDING:
                if self.hercules.status(file) == FileStatus.SENT:
                    file.status = FileStatus.SENT

    def remove_temp_files(self, filemanager: Filemanager):
        for file in filemanager.files:
            if file.status == FileStatus.SENT and os.path.isfile(file.local_path):
                print(f"Removing temp file: {file.local_path}")
                os.remove(file.local_path)
                file.status = FileStatus.DELETED

    def remove_outgoing_temp_files(self):
        for file in self.outgoing_filemanager.files:
            if file.status == FileStatus.SENT and os.path.isfile(file.local_path):
                print(f"Removing temp file: {file.local_path}")
                os.remove(file.local_path)
                file.status = FileStatus.DELETED
        self.incoming_filemanager.save_state(self.incoming_state_file)

    def remove_incoming_temp_files(self):
        for file in self.incoming_filemanager.files:
            if file.status == FileStatus.COPIED and os.path.isfile(file.local_path):
                print(f"Removing temp file: {file.local_path}")
                os.remove(file.local_path)
                file.status = FileStatus.DELETED
        self.outgoing_filemanager.save_state(self.outgoing_state_file)
