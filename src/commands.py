from enum import Enum


class CommandKind(Enum):
    StatusGet = 0
    IsBanned = 1
    CurrentHeight = 2
    GetBlock = 3
