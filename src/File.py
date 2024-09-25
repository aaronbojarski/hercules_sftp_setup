from dataclasses import dataclass
from enum import Enum


class FileStatus(Enum):
    UPDATING = 1
    READY = 2
    COPIED = 3
    SENDING = 4
    SENT = 5
    DELETED = 6
    ERROR = 7


@dataclass
class File:
    name: str
    size: int
    modified_time: int
    local_path: str
    status: FileStatus = FileStatus.UPDATING
    hercules_file_id: int = -1
