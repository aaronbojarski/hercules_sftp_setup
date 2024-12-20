import json
from dataclasses import dataclass


@dataclass
class Config:
    ldh_ip: str = ""
    ldh_username: str = ""
    ldh_ssh_key_file: str = ""
    ldh_observe_dir: str = ""
    ldh_write_dir: str = ""
    lth_state_file_dir: str = ""
    lth_hercules_rcv_dir: str = ""
    lth_out_temp_dir: str = ""
    hercules_monitor_address: str = "localhost:8000"
    rth_address: str = ""
    rth_target_dir: str = ""

    def load(self, filename: str):
        with open(filename, "r") as f:
            file_content = json.load(f)
        for key, value in file_content.items():
            if key == "ldh_ip":
                self.ldh_ip = value
            if key == "ldh_username":
                self.ldh_username = value
            if key == "ldh_ssh_key_file":
                self.ldh_ssh_key_file = value
            if key == "ldh_observe_dir":
                self.ldh_observe_dir = value
            if key == "ldh_write_dir":
                self.ldh_write_dir = value
            if key == "lth_state_file_dir":
                self.lth_state_file_dir = value
            if key == "lth_hercules_rcv_dir":
                self.lth_hercules_rcv_dir = value
            if key == "lth_out_temp_dir":
                self.lth_out_temp_dir = value
            if key == "hercules_monitor_address":
                self.hercules_monitor_address = value
            if key == "rth_address":
                self.rth_address = value
            if key == "rth_target_dir":
                self.rth_target_dir = value
