import jsonpickle
import os
from src.File import File, ItemStatus, Directory
from typing import List


class Filemanager:
    def __init__(self, temp_dir: str) -> None:
        self.files: List[File] = []
        self.dirs: List[Directory] = []
        self.temp_dir = os.path.abspath(temp_dir)

    def load_state(self, filename: str) -> None:
        if not os.path.isfile(filename):
            return
        with open(filename, "r") as f:
            self.files = jsonpickle.decode(f.read())
        # restart hercules transfer if file was in transfer in loaded state
        for file in self.files:
            if file.status == ItemStatus.SENDING:
                file.status = ItemStatus.COPIED

    def save_state(self, filename: str) -> None:
        with open(filename, "w") as f:
            f.write(jsonpickle.encode(self.files, indent=4))

    def cleanup_state(self, current_filenames: List[str]):
        files = []
        for file in self.files:
            if file.name in current_filenames or file.status != ItemStatus.DELETED:
                files.append(file)
        self.files = files

    def add(self, name: str, size: int, mtime: int):
        file = File(name, size, mtime, self.temp_dir + "/" + name)
        self.files.append(file)

    def update(self, name: str, size: int, mtime: int):
        exists = False
        for file in self.files:
            if file.name == name:
                if file.size != size or file.modified_time != mtime:
                    file.size = size
                    file.modified_time = mtime
                    file.status = ItemStatus.UPDATING
                elif (
                    file.status == ItemStatus.UPDATING
                ):  # File content has not changed during last iteration. Therefore it is likely complete.
                    file.status = ItemStatus.READY
                exists = True
                break
        if not exists:
            self.add(name, size, mtime)

    def update_dir(self, name, size, mtime):
        exists = False
        for directory in self.dirs:
            if directory.name == name:
                if directory.size != size or directory.modified_time != mtime:
                    directory.size = size
                    directory.modified_time = mtime
                    directory.status = ItemStatus.UPDATING
                elif (
                    directory.status == ItemStatus.UPDATING
                ):  # File content has not changed during last iteration. Therefore it is likely complete.
                    directory.status = ItemStatus.READY
                exists = True
                break
        if not exists:
            directory = Directory(name, size, mtime, self.temp_dir + "/" + name)
            self.dirs.append(directory)