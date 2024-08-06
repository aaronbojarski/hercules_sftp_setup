import json
from dataclasses import dataclass


@dataclass
class Config:
    target_ip: str = ""
    username: str = ""
    ssh_key_file: str = ""
    temp_dir: str = ""
    target_dir: str = ""
    hercules_path: str = ""
    hercules_interface: str = ""
    hercules_local_address: str = ""
    hercules_destination_address: str = ""

    def load(self, filename: str):
        with open(filename, "r") as f:
            file_content = json.load(f)
        for key, value in file_content.items():
            if key == "target_ip":
                self.target_ip = value
            if key == "username":
                self.username = value
            if key == "ssh_key_file":
                self.ssh_key_file = value
            if key == "temp_dir":
                self.temp_dir = value
            if key == "target_dir":
                self.target_dir = value
            if key == "hercules_path":
                self.hercules_path = value
            if key == "hercules_interface":
                self.hercules_interface = value
            if key == "hercules_local_address":
                self.hercules_local_address = value
            if key == "hercules_destination_address":
                self.hercules_destination_address = value
