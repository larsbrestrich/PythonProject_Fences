#!/usr/bin/env python
from Enums import CellType
from Enums import CellWorth

class Cell:
    def __init__(self, x, y, type, worth):
        self.x = x
        self.y = y
        self.cellType = type
        self.cellWorth = worth
        self.playerOwnerID = None

    def getCellType(self):
        return self.cellType
    
    def getCellWorth(self):
        return self.cellWorth
    
    def getPlayerOwner(self):
        return self.playerOwnerID
    
    def getPosX(self):
        return self.x
    
    def getPosY(self):
        return self.y
    
    def setCellType(self, type):
        self.cellType = type

    def setPlayerOwner(self, player):
        self.playerOwnerID = player

    def isClaimed(self):
        return self.playerOwnerID != None