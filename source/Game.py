from Grid import Grid
from Player import Player
from Enums import CellType
from Enums import CellWorth
from Enums import OnFencePlacedState

gParamBoundary_dimensions = [1, 30]
gParamBoundary_maxPlayers = [2, 5]
gParamBoundary_resourceAbundance = [0, 100]

"""
Class representing the logic of a single game
"""

import random
import string

class Game:
    def __init__(self, 
        name = None, 
        host_username = None,
        dimX = None, 
        dimY = None,
        maxPlayers = 2, 
        resourceAbundance = None,
        len_id = 10,
    ):
        # Set game state
        self.name = name
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = len_id));

        self.dimX = dimX;
        self.dimY = dimY;
        self.resourceAbundance = resourceAbundance;
        self.grid = Grid(dimX, dimY, resourceAbundance);
        self.landCells = self.grid.getAllLandCells()

        self.host_username = host_username;
        self.maxPlayers = maxPlayers

        # Set player states
        self.players = [];
        self.__current_player_index = 0;
        self.__current_player = None;
        self.__current_player_username = None;

        # cell worth hyperparameters
        self.cellPointWorths = dict()
        self.cellPointWorths[CellWorth.NORMAL] = 1
        self.cellPointWorths[CellWorth.COPPER] = 2
        self.cellPointWorths[CellWorth.SILVER] = 3
        self.cellPointWorths[CellWorth.GOLD] = 5

    def getGrid(self):      
        return self.grid
    
    def getCellAt(self, x, y):
        return self.grid.getCellAt(x, y)
    
    """
    Try to place a fence on the grid
    """
    def tryPlaceFence(self, cell,
        player_id = None, isServer = False
    ):
        if isServer and (player_id is self.__current_player_username):
            return OnFencePlacedState.FAILURE

        if self.grid.tryPlaceFence(cell, player_id):
            if not self.checkAdjacentLandClaims(cell, player_id):
                self.nextTurn()

            if self.checkGameoverCondition():
                return OnFencePlacedState.GAMEOVER

            return OnFencePlacedState.SUCCESS

        return OnFencePlacedState.FAILURE

    def checkAdjacentLandClaims(self, cell, player_id):
        claimedLand = False
        adjacent = self.getAdjacentCells(cell)
        for cellAdj in adjacent:
            if cellAdj.getCellType() == CellType.LAND and (not cellAdj.isClaimed()):
                if self.checkLandClaim(cellAdj, player_id):
                    self.onLandClaimed(cellAdj, player_id);
                    claimedLand = True
        return claimedLand
    
    def checkLandClaim(self, cell, player_id):
        landAjcaent = self.getAdjacentCells(cell)
        for fences in landAjcaent:
            if (fences.getCellType() != CellType.FENCE) or (fences.getPlayerOwner() != player_id):
                return False
        return True

    def onLandClaimed(self, cell, player_id):
        cell.setPlayerOwner(player_id);
        cellWorth = cell.getCellWorth()
        self.getPlayerByID(player_id).active_game_score += self.cellPointWorths[cellWorth]

    def checkGameoverCondition(self):
        # check every land cell
        for land in self.landCells:
            # only check if not claimed
            if not land.isClaimed():                
                # check fence owners. If all have same owner, land can still be claimed
                adjacent = self.getAdjacentCells(land)

                ownerships = []
                for adj in adjacent:
                    ownerships.append(adj.getPlayerOwner())
                
                # check that ownerships are either none or all the same
                ownership = None
                allSameOrNone = True
                for own in ownerships:
                    if ownership == None:
                        ownership = own
                    if ownership != own and ownership != None and own != None:
                        allSameOrNone = False
                
                if allSameOrNone:
                    return False
        return True

    def getAdjacentCells(self, cell):
        adjacent = []
        adj = self.grid.getCellAt(cell.getPosX() + 1, cell.getPosY())
        if adj != None:
            adjacent.append(adj)
        adj = self.grid.getCellAt(cell.getPosX() - 1, cell.getPosY())
        if adj != None:
            adjacent.append(adj)
        adj = self.grid.getCellAt(cell.getPosX(), cell.getPosY() + 1)
        if adj != None:
            adjacent.append(adj)
        adj = self.grid.getCellAt(cell.getPosX(), cell.getPosY() - 1)
        if adj != None:
            adjacent.append(adj)
        
        return adjacent
    
    """
    Get score of all players
    """
    def getScores(self):
        playerDict = dict()
        for player in self.players:
            playerDict[player] = player.active_game_score
        return playerDict
    
    """
    Get the current player
    """
    def getCurrentPlayer(self):
        return self.__current_player

    """
    Change the current player
    """
    def nextTurn(self):
        self.__current_player_index += 1
        if self.__current_player_index >= len(self.players):
            self.__current_player_index = 0

        self.__current_player = self.players[self.__current_player_index];
        self.__current_player_username = self.__current_player.username;
    
    """
    Add a player to the game
    """
    def add_player(self, player):
        if len(self.players) == self.maxPlayers:
            raise Exception("Max players reached");

        if player in self.players:
            raise Exception("Player already in game");
        
        self.players.append(player);

    """
    Remove a player from the game
    """
    def remove_player(self, username):
        target_indices = [i for i, p in enumerate(self.players) if p.username == username];

        if len(target_indices) == 0:
            return
            #raise Exception(f"Player {username} not in game");
        
        target_index = target_indices[0];
        self.players.pop(target_index);

    def getWinner(self):
        winner = None
        highestScore = 0
        scores = self.getScores()
        for player in self.players:
            score = scores[player]
            if score > highestScore:
                highestScore = score
                winner = player
        return winner

    def getPlayerByID(self, username):
        for player in self.players:
            if player.username == username:
                return player