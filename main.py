from Hercules import Hercules
import pysftp
from time import sleep
from alive_progress import alive_bar


SSH_KEY_FILE = ...
TARGET_IP = ...

hercules = Hercules("hercules_path")
with pysftp.Connection(TARGET_IP, username="moltres", private_key=SSH_KEY_FILE) as sftp:
    print("CONNECTED")
    files = []
    while True:
        with sftp.cd("/home/moltres/aaron/test"):
            current_files = sftp.listdir()
            for f in current_files:
                if f not in files:
                    print(f"Found new file: {f}")
                    files.append(f)
                    filesize = sftp.stat(f).st_size
                    with alive_bar(filesize, manual=True) as bar:
                        sftp.get(f, callback=(lambda a, b: bar(a / b)))
                    hercules.transfer("CERN", f)
                    print()
        sleep(1)
