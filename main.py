from src.Manager import Manager


TARGET_IP = ...
USERNAME = ...
SSH_KEY_FILE = ...
TARGET_DIR = ...
TEMP_DIR = "./temp/"
HERCULES_PATH = "hercules path"


def main():
    manager = Manager(TARGET_IP, USERNAME, SSH_KEY_FILE, TEMP_DIR, HERCULES_PATH)
    manager.start(TARGET_DIR)


if __name__ == "__main__":
    main()
