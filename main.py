import os
from src.Manager import Manager
from src.Config import Config

TARGET_IP = ...
USERNAME = ...
SSH_KEY_FILE = ...
TARGET_DIR = ...
TEMP_DIR = "./temp/"
HERCULES_PATH = ...
HERCULES_INTERFACE = ...
HERCULES_LOCAL_ADDRESS = ...
HERCULES_DESTINATION_ADDRESS = ...


def main():
    config = Config(
        TARGET_IP,
        USERNAME,
        SSH_KEY_FILE,
        TEMP_DIR,
        HERCULES_PATH,
        TARGET_DIR,
        HERCULES_INTERFACE,
        HERCULES_LOCAL_ADDRESS,
        HERCULES_DESTINATION_ADDRESS,
    )
    if os.path.isfile("config.json"):
        config.load("config.json")
        print(config)
    manager = Manager(config)
    manager.start()


if __name__ == "__main__":
    main()
