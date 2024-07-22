import jsonpickle
import os
from src.File import File, FileStatus
from typing import List


class Filemanager:
    def __init__(self, temp_dir: str) -> None:
        self.files: List[File] = []
        self.temp_dir = os.path.abspath(temp_dir)

    def load_state(self, filename: str) -> None:
        if not os.path.isfile(filename):
            return
        with open(filename, "r") as f:
            self.files = jsonpickle.decode(f.read())

    def save_state(self, filename: str) -> None:
        with open(filename, "w") as f:
            f.write(jsonpickle.encode(self.files))

    def cleanup_state(self, current_filenames: List[str]):
        files = []
        for file in self.files:
            if file.name in current_filenames or not file.status == FileStatus.DELETED:
                files.append(file)
        self.files = files

    def add(self, name: str, size: int, mtime: int):
        file = File(name, size, mtime, self.temp_dir + "/" + name, "'Remote Path Placeholder'")
        self.files.append(file)

    def update(self, name: str, size: int, mtime: int):
        exists = False
        for file in self.files:
            if file.name == name:
                if file.size != size or file.modified_time != mtime:
                    file.size = size
                    file.modified_time = mtime
                    file.status = FileStatus.UPDATING
                elif (
                    file.status == FileStatus.UPDATING
                ):  # File content has not changed during last iteration. Therefore it is likely complete.
                    file.status = FileStatus.READY
                exists = True
                break
        if not exists:
            self.add(name, size, mtime)
