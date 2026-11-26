from enum import StrEnum


class TaskStatus(StrEnum):
    open = "open"
    in_progress = "in_progress"
    done = "done"
