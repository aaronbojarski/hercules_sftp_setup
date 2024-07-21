import json
import os
from File import File, FileStatus
from typing import List


class Filemanager:
    def __init__(self, temp_dir) -> None:
        self.files: List[File] = []
        self.temp_dir = os.path.abspath(temp_dir)

    def load_state(self, filename: str) -> None:
        with open(filename, "r") as f:
            self.files = json.load(f)

    def save_state(self, filename: str) -> None:
        with open(filename, "w") as f:
            json.dump(self.files, f)

    def cleanup_state(self, current_filenames):
        files = []
        for file in self.files:
            if file.name in current_filenames or not file.removed:
                files.append(file)
        self.files = files

    def add(self, name, size, mtime):
        file = File(name, size, mtime, self.temp_dir + "/" + name, "'Remote Path Placeholder'")
        self.files.append(file)

    def update(self, name, size, mtime):
        exists = False
        for file in self.files:
            if file.name == name:
                if file.size != size or file.modified_time != mtime:
                    file.size = size
                    file.modified_time = mtime
                    file.status = FileStatus.UPDATING
                elif file.status == FileStatus.UPDATING:  # File content has not changed during last iteration. Therefore it is likely complete.
                    file.status = FileStatus.READY
                exists = True
                break
        if not exists:
            self.add(name, size, mtime)
