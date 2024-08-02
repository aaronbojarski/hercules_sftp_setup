import subprocess
from time import sleep
from src.File import File
from src.Config import Config


class Hercules:
    def __init__(self, config: Config):
        self.binary = config.hercules_path
        self.interface = config.hercules_interface
        self.local_address = config.hercules_local_address
        self.destination_address = config.hercules_destination_address

    def transfer(self, file: File):
        print(f"HERCULES: SENDING file {file.name} ({file.local_path}) to {file.remote_path}")
        subprocess.call(
            [
                self.binary,
                "-i",
                self.interface,
                "-l",
                self.local_address,
                "-d",
                self.destination_address,
                "-t",
                file.local_path,
                "--mtu",
                "1440",
                "-p",
                "1048576",
                "-np",
                "4",
                "-nt",
                "4",
            ]
        )
        print("HERCULES: Transfer complete")
