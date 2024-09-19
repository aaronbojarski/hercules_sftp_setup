import requests
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
        infile = file.local_path + "/" + file.name
        outfile = file.remote_path + "/" + file.name
        resp = requests.get(f"localhost:8000/submit?file={infile}&destfile={outfile}&dest={self.destination_address}:8000")
        print("Hercules Response:", resp)
        # TODO: Set the transfer ID in the file to later be able to check

    def status(self, file: File):
        # TODO: Do a request with the transfer ID to check the status of the file
        pass
