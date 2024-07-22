from dataclasses import dataclass
from enum import Enum


class FileStatus(Enum):
    UPDATING = 1
    READY = 2
    COPIED = 3
    SENT = 4
    DELETED = 5


@dataclass
class File:
    name: str
    size: int
    modified_time: int
    local_path: str
    remote_path: str
    status: FileStatus = FileStatus.UPDATING
