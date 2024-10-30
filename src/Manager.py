from src.Hercules import Hercules
from src.Filemanager import Filemanager
from src.File import ItemStatus, File, Directory
from src.Config import Config
import paramiko
from paramiko.ssh_exception import SSHException
import os
import stat
from time import sleep
from alive_progress import alive_bar
from typing import Tuple

MAX_RECONNECTION_RETRIES = 5


class Manager:
    def __init__(self, config: Config) -> None:
        self.connection_retries = 0
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.key = paramiko.RSAKey.from_private_key_file(config.ldh_ssh_key_file)
        self.ssh.connect(config.ldh_ip, username=config.ldh_username, pkey=self.key)
        self.sftp_connection = self.ssh.open_sftp()
        self.outgoing_state_file = config.lth_state_file_dir + "/outgoing_state.json"
        self.incoming_state_file = config.lth_state_file_dir + "/incoming_state.json"
        self.outgoing_filemanager = Filemanager(config.lth_out_temp_dir)
        self.outgoing_filemanager.load_state(self.outgoing_state_file)
        self.incoming_filemanager = Filemanager(config.lth_hercules_rcv_dir)
        self.incoming_filemanager.load_state(self.incoming_state_file)
        self.hercules = Hercules(config)
        self.config = config

    def start(self):
        while self.connection_retries < MAX_RECONNECTION_RETRIES:
            try:
                self.sftp_connection.chdir(self.config.ldh_observe_dir)
                self.check_outgoing_files()
                self.copy_outgoing_files()
                self.copy_outgoing_directories()
                self.sftp_connection.chdir(self.config.ldh_write_dir)
                self.check_incoming_files()
                self.copy_incoming_files()
            except (SSHException, OSError, AttributeError) as e:
                print(e)
                self.connection_retries += 1
                print(f"Trying to reconnect. Retry {self.connection_retries}/{MAX_RECONNECTION_RETRIES}")
                try:
                    self.ssh.connect(self.config.ldh_ip, username=self.config.ldh_username, pkey=self.key)
                    self.sftp_connection = self.ssh.open_sftp()
                except Exception as e:
                    print(e)

            self.send_outgoing_files()
            self.check_sending_status()
            self.remove_incoming_temp_files()
            self.remove_outgoing_temp_files()
            sleep(5)

    def check_outgoing_files(self):
        dir_content = self.sftp_connection.listdir()
        for item in dir_content:
            metadata = self.sftp_connection.stat(item)
            if stat.S_ISDIR(metadata.st_mode):
                mod_time, total_size = self.traverse_outgoing_dir(f"./{item}")
                self.outgoing_filemanager.update_dir(item, total_size, mod_time)
            elif stat.S_ISREG(metadata.st_mode):
                self.outgoing_filemanager.update(item, metadata.st_size, metadata.st_mtime)
            else:
                print(f"No file or directory. Ignoring '{item}'")
        self.outgoing_filemanager.cleanup_state(dir_content)

    def traverse_outgoing_dir(self, base_name) -> Tuple[int, int]:
        mod_time, total_size = 0, 0
        dir_content = self.sftp_connection.listdir(base_name)
        for item in dir_content:
            metadata = self.sftp_connection.stat(base_name + "/" + item)
            if stat.S_ISDIR(metadata.st_mode):
                mod_time, total_size = self.traverse_outgoing_dir(f"{base_name}/{item}")
            elif stat.S_ISREG(metadata.st_mode):
                mod_time = max(mod_time, metadata.st_mtime)
                total_size += metadata.st_size
            else:
                print(f"No file or directory. Ignoring '{item}'")
        return mod_time, total_size

    def copy_outgoing_files(self):
        for file in self.outgoing_filemanager.files:
            if file.status == ItemStatus.READY:
                with alive_bar(file.size, manual=True) as bar:
                    self.sftp_connection.get(file.name, file.local_path, callback=(lambda a, b: bar(a / b)))
                file.status = ItemStatus.COPIED

    def copy_outgoing_directories(self):
        for directory in self.outgoing_filemanager.dirs:
            if directory.status == ItemStatus.READY:
                self.copy_traverse_outgoing_directories(f"./{directory.name}")
                directory.status = ItemStatus.COPIED

    def copy_traverse_outgoing_directories(self, base_path):
        dir_content = self.sftp_connection.listdir(base_path)
        if not os.path.exists(f"{self.config.lth_out_temp_dir}/{base_path[2:]}"):
            os.makedirs(f"{self.config.lth_out_temp_dir}/{base_path[2:]}")
        for item in dir_content:
            metadata = self.sftp_connection.stat(f"{base_path}/{item}")
            if stat.S_ISDIR(metadata.st_mode):
                self.copy_traverse_outgoing_directories(f"{base_path}/{item}/")
            elif stat.S_ISREG(metadata.st_mode):
                with alive_bar(metadata.st_size, manual=True) as bar:
                    file_name = f"{base_path[2:]}/{item}"
                    self.sftp_connection.get("./" + file_name, self.config.lth_out_temp_dir + "/" + file_name, callback=(lambda a, b: bar(a / b)))

    def check_incoming_files(self):
        current_files = os.listdir(self.config.lth_hercules_rcv_dir)
        for f in current_files:
            metadata = os.stat(self.config.lth_hercules_rcv_dir + "/" + f)
            self.incoming_filemanager.update(f, metadata.st_size, metadata.st_mtime)
        self.incoming_filemanager.cleanup_state(current_files)

    def copy_incoming_files(self):
        for file in self.incoming_filemanager.files:
            if file.status == ItemStatus.READY:
                with alive_bar(file.size, manual=True) as bar:
                    self.sftp_connection.put(file.local_path, file.name, callback=(lambda a, b: bar(a / b)))
                file.status = ItemStatus.COPIED

    def send_outgoing_files(self):
        for file in self.outgoing_filemanager.files:
            if file.status == ItemStatus.COPIED:
                self.hercules.transfer_file(file)
                file.status = ItemStatus.SENDING
        for directory in self.outgoing_filemanager.dirs:
            if directory.status == ItemStatus.COPIED:
                self.hercules.transfer_directory(directory)
                directory.status = ItemStatus.SENDING

    def check_sending_status(self):
        for file in self.outgoing_filemanager.files:
            if file.status == ItemStatus.SENDING:
                transfer_status = self.hercules.status(file)
                if transfer_status == ItemStatus.ERROR:
                    file.status = ItemStatus.UPDATING
                else:
                    file.status = transfer_status

    def remove_outgoing_temp_files(self):
        for file in self.outgoing_filemanager.files:
            if file.status == ItemStatus.SENT and os.path.isfile(file.local_path):
                print(f"Removing temp file: {file.local_path}")
                os.remove(file.local_path)
                file.status = ItemStatus.DELETED
        for directory in self.outgoing_filemanager.dirs:
            if directory.status == ItemStatus.SENT and os.path.isdir(directory.local_path):
                os.remove(file.local_path)
                directory.status = ItemStatus.DELETED

        self.incoming_filemanager.save_state(self.incoming_state_file)

    def remove_incoming_temp_files(self):
        for file in self.incoming_filemanager.files:
            if file.status == ItemStatus.COPIED and os.path.isfile(file.local_path):
                print(f"Removing temp file: {file.local_path}")
                os.remove(file.local_path)
                file.status = ItemStatus.DELETED
        self.outgoing_filemanager.save_state(self.outgoing_state_file)
