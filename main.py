import os
import argparse
from src.Manager import Manager
from src.Config import Config

CONFIG_FILE_PATH = "config.json"


def main():
    config = Config()
    if os.path.isfile(CONFIG_FILE_PATH):
        config.load(CONFIG_FILE_PATH)
        print("Loading config file: % s" % os.path.abspath(CONFIG_FILE_PATH))
    else:
        print("Config not found.")
        exit()
    print(config)
    manager = Manager(config)
    manager.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--Config", help="Config File Path")
    args = parser.parse_args()

    if args.Config:
        CONFIG_FILE_PATH = args.Config
    main()
