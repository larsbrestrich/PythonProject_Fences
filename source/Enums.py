#!/usr/bin/env python
from enum import Enum

class UserState(Enum):
    NONE = 0
    LOGIN = 1
    ROOMSLIST = 2
    MAKEGAME = 3
    GAME = 4
    ENDSCREEN = 5

class CellType(Enum):
    SKIP = -1
    BORDER = 0
    LAND = 1
    FENCE = 2

class CellWorth(Enum):
    NORMAL = 0
    COPPER = 1
    SILVER = 2
    GOLD = 3

class OnFencePlacedState(Enum):
    SUCCESS = 1
    FAILURE = 2
    GAMEOVER = 3

class Helpers:
    def convertString(b):
        if isinstance(b, bytes):
            return b.decode('utf-8')
        return ""

    def convertChar(ch):
        try:
            return chr(ch)
        except (ValueError, TypeError):
            return ''
    
    def convertStringToNumber(b):
        if isinstance(b, bytes):
            b = b.decode('utf-8')
        else:
            b = ""

        s = b.strip()
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return None