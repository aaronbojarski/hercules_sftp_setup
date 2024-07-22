from time import sleep
from src.File import File


class Hercules:
    def __init__(self, binary):
        self.binary = binary

    def transfer(self, file: File):
        print(f"HERCULES: SENDING file {file.name} ({file.local_path}) to {file.remote_path}")
        sleep(1)
        print("HERCULES: Transfer complete")
