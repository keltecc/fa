#!/usr/bin/env python3

import enum
import datetime
import dataclasses


@dataclasses.dataclass
class User:
    username: str
    hashed_password: str


class TaskStatus(enum.Enum):
    Unknown = 'Unknown'
    Waiting = 'Waiting'
    InProgress = 'InProgress'
    Done = 'Done'


@dataclasses.dataclass
class Task:
    id: str
    owner: str
    title: str
    description: str
    status: TaskStatus
    priority: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
