from time import sleep


class Hercules:
    def __init__(self, binary):
        self.binary = binary

    def transfer(self, destination, file):
        print(f"HERCULES: SENDING file {file} to {destination}")
        sleep(3)
        print("HERCULES: Transfer complete")
