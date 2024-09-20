import requests
from src.File import File
from src.Config import Config


class Hercules:
    def __init__(self, config: Config):
        self.hercules_monitor_address = config.hercules_monitor_address
        self.destination_address = config.rth_address
        self.destination_dir = config.rth_target_dir

    def transfer(self, file: File):
        print(f"HERCULES: SENDING file {file.name} ({file.local_path}) to {self.destination_dir}")
        infile = file.local_path
        outfile = self.destination_dir + "/" + file.name
        resp = requests.get(
            f"{self.hercules_monitor_address}/submit?file={infile}&destfile={outfile}&dest={self.destination_address}"
        )
        print("Hercules Response:", resp)
        # TODO: Set the transfer ID in the file to later be able to check

    def status(self, file: File):
        # TODO: Do a request with the transfer ID to check the status of the file
        pass
