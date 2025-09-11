#!/usr/bin/env python
from Cell import Cell
from Enums import CellType
from Enums import CellWorth

from random import random

class Grid:
    def __init__(self, dimX, dimY, abundance):
        self.dimensionX = (dimX * 2) - 1
        self.dimensionY = (dimY * 2) - 1

        # random parameters
        self.percentGold = float(abundance) * 0.2
        self.percentSilver = float(abundance) * 0.3
        self.percentCopper = float(abundance) * 0.5

        self.initialiseGrid()

    def initialiseGrid(self):
        self.grid = [[None for _ in range(self.dimensionX)] for _ in range(self.dimensionY)]
        for y in range(0,self.dimensionY):
            for x in range(0,self.dimensionX):
                if (x % 2 == 0) and (y % 2 == 0):
                    self.grid[y][x] = Cell(x, y, CellType.SKIP, CellWorth.NORMAL) # skip cells
                elif (x % 2 == 0) or (y % 2 == 0):
                    self.grid[y][x] = Cell(x, y, CellType.BORDER, CellWorth.NORMAL) # selectable border cells for building fences
                else:
                    # determine cell worth
                    cellWorth = CellWorth.NORMAL
                    rand = int(random() * 100)
                    if rand < self.percentGold:
                        cellWorth = CellWorth.GOLD
                    elif rand < self.percentSilver:
                        cellWorth = CellWorth.SILVER
                    elif rand < self.percentCopper:
                        cellWorth = CellWorth.COPPER

                    self.grid[y][x] = Cell(x, y, CellType.LAND, cellWorth) # land cells

    def getCellAt(self, x, y):
        if x < 0 or x >= self.dimensionX:
            return None
        elif y < 0 or y >= self.dimensionY:
            return None
        return self.grid[y][x]
    
    def getdimensionX(self):
        return self.dimensionX
    
    def getdimensionY(self):
        return self.dimensionY
    
    def tryPlaceFence(self, cell, playerID):
        if cell.getCellType() != CellType.BORDER:
            return False
        
        cell.setCellType(CellType.FENCE)
        cell.setPlayerOwner(playerID)
        return True
    
    def getAllLandCells(self):
        landCells = []
        for y in range(0,self.dimensionY):
            for x in range(0,self.dimensionX):
                if self.getCellAt(x, y).getCellType() == CellType.LAND:
                    landCells.append(self.getCellAt(x, y))
        return landCells
