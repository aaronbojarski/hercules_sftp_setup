import requests
from src.File import File, FileStatus
from src.Config import Config


class Hercules:
    def __init__(self, config: Config):
        self.hercules_monitor_address = config.hercules_monitor_address
        self.destination_address = config.rth_address
        self.destination_dir = config.rth_target_dir

    def transfer(self, file: File):
        infile = file.local_path
        outfile = self.destination_dir + "/" + file.name
        resp = requests.get(
            f"http://{self.hercules_monitor_address}/submit?file={infile}&destfile={outfile}&dest={self.destination_address}"
        ).text
        file.hercules_file_id = [int(s) for s in resp.split() if s.isdigit()][0]
        print(
            f"HERCULES: SENDING file {file.name} ({file.local_path}) to {self.destination_dir} with file id {file.hercules_file_id}"
        )

    def status(self, file: File):
        if file.hercules_file_id == -1:
            FileStatus.ERROR
        resp = requests.get(f"http://{self.hercules_monitor_address}/status?id={file.hercules_file_id}").text
        status = [int(s) for s in resp.split() if s.isdigit()][0]
        if status == 3:
            print(f"Hercules transfer for {file.name} done.")
            return FileStatus.SENT
        return FileStatus.SENDING
