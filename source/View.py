from Grid import Grid
from Enums import CellType
from Enums import CellWorth
from Enums import UserState
from UIMenu import UIMenu
from UIElement import UIElement

from Game import gParamBoundary_dimensions
from Game import gParamBoundary_maxPlayers
from Game import gParamBoundary_resourceAbundance

import curses

class View:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.screenWidthHeight = stdscr.getmaxyx()
        
        # land colours
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_CYAN)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_GREEN)
        self.landColours = [curses.color_pair(1), curses.color_pair(2), curses.color_pair(3), curses.color_pair(4), curses.color_pair(5)]
        self.landColoursPlayers = dict()
        
        # unclaimed colour
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        self.colourLandWorth = curses.color_pair(6)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_WHITE)
        self.colourBold = curses.color_pair(7) | curses.A_BOLD
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.colourDefault = curses.color_pair(8)

        # fence colours
        curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(10, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(12, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(13, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.fenceColours = [curses.color_pair(9), curses.color_pair(10), curses.color_pair(11), curses.color_pair(12), curses.color_pair(13)]
        self.fenceColoursPlayers = dict()

        # UI elements
        self.currentMenu = None

        self.menuLogin = UIMenu(self.screenWidthHeight[0] / 2, self.screenWidthHeight[1] / 2)
        self.menuLogin.addElement(UIElement("StaticField1", 1, 23, "WELCOME TO PROSPECTOR", False))
        self.menuLogin.addElement(UIElement("StaticField1", 2, 23, "Produced by 240032297 and 240032316 for assessment 2 of CS5003", False))
        self.menuLogin.addElement(UIElement("StaticField1", 4, 23, "Sign up or Log in", False))
        self.menuLogin.addElement(UIElement("Username", 5, 10, "Username:", False))
        self.menuLogin.addElement(UIElement("UsernameField", 5, 23, "", True))
        self.menuLogin.addElement(UIElement("Password", 7, 10, "Password:", False))
        self.menuLogin.addElement(UIElement("PasswordField", 7, 23, "", True))


        self.menuRooms = UIMenu(self.screenWidthHeight[0], self.screenWidthHeight[1])

        self.menuMakeGame = UIMenu(self.screenWidthHeight[0], self.screenWidthHeight[1])
        self.menuMakeGame.addElement(UIElement("NameGame", 2, 10, "Name:", False))
        self.menuMakeGame.addElement(UIElement("NameGameField", 2, 20, "", True))
        self.menuMakeGame.addElement(UIElement("MapX", 3, 10, "Map Dimension X:", False))
        self.menuMakeGame.addElement(UIElement("MapXField", 3, 28, "", True))
        self.menuMakeGame.addElement(UIElement("MapXInstructions", 3, 50, str(gParamBoundary_dimensions[0]) + " to " + str(gParamBoundary_dimensions[1]), False))
        self.menuMakeGame.addElement(UIElement("MapY", 4, 10, "Map Dimension Y:", False))
        self.menuMakeGame.addElement(UIElement("MapYField", 4, 28, "", True))
        self.menuMakeGame.addElement(UIElement("MapYInstructions", 4, 50, str(gParamBoundary_dimensions[0]) + " to " + str(gParamBoundary_dimensions[1]), False))
        self.menuMakeGame.addElement(UIElement("MaxPlayers", 6, 10, "Max Players:", False))
        self.menuMakeGame.addElement(UIElement("MaxPlayersField", 6, 23, "", True))
        self.menuMakeGame.addElement(UIElement("MaxPlayersInstructions", 6, 50, str(gParamBoundary_maxPlayers[0]) + " to " + str(gParamBoundary_maxPlayers[1]), False))
        self.menuMakeGame.addElement(UIElement("ResourceAbundance", 7, 10, "Resource Abundance (Percentage):", False))
        self.menuMakeGame.addElement(UIElement("ResourceAbundanceField", 7, 43, "", True))
        self.menuMakeGame.addElement(UIElement("ResourceAbundanceInstructions", 7, 50, str(gParamBoundary_resourceAbundance[0]) + " to " + str(gParamBoundary_resourceAbundance[1]), False))

        self.menuGame = UIMenu(self.screenWidthHeight[0], self.screenWidthHeight[1])

        self.menuEndscreen = UIMenu(self.screenWidthHeight[0], self.screenWidthHeight[1])


    def onUserStateChanged(self, userState):
        if userState == UserState.LOGIN:
            self.currentMenu = self.menuLogin
        elif userState == UserState.ROOMSLIST:  
            self.currentMenu = self.menuRooms  
        elif userState == UserState.MAKEGAME:  
            self.currentMenu = self.menuMakeGame           
        elif userState == UserState.GAME:
            self.currentMenu = self.menuGame
        elif userState == UserState.ENDSCREEN:
            self.currentMenu = self.menuEndscreen

    def draw(self, grid, currentUser, playerScores, gamesList, playerWinner, userStatistics):
        if self.currentMenu == self.menuGame:
            self.drawGame(grid, playerScores, currentUser)
        elif self.currentMenu == self.menuRooms:
            self.currentMenu.clearElements()
            index = 1
            for game in gamesList:
                self.currentMenu.addElement(UIElement("Game" + str(index), 2 + index, 10, game, True))
                index += 1
            self.currentMenu.addElement(UIElement("MakeGame", 4 + index, 10, "New Game", True))
            self.drawStatistics(userStatistics, currentUser)
        elif self.currentMenu == self.menuEndscreen:
            self.currentMenu.clearElements()
            if playerWinner == currentUser:
                self.stdscr.addstr(1, 1, "You won the game!", self.colourDefault)
            else:
                self.stdscr.addstr(1, 1, "You lost the game... " + str(playerWinner) + " won the game.", self.colourDefault)
            self.stdscr.addstr(2, 1, "Press any key top continue.", self.colourDefault)

            if currentUser != None:
                self.drawScores(playerScores, currentUser)
        
        self.currentMenu.displayMenu(self.stdscr)

    def drawGame(self, grid, playerScores, currentUser):
        if grid == None:
            return

        dimensionX = grid.getdimensionX()
        dimensionY = grid.getdimensionY()

        # draw grid
        for y in range(dimensionY):
            for x in range(dimensionX):
                cell = grid.getCellAt(x, y)
                self.drawCell(cell, x, y)

        # draw scores
        if currentUser != None:
            self.drawScores(playerScores, currentUser)

    def drawCell(self, cell, x, y):
        cellType = cell.getCellType()
        playerOwner = cell.getPlayerOwner()

        if cellType == CellType.FENCE:
            colour = self.getPlayerColour(playerOwner, True)
            if y % 2 == 0:
                self.stdscr.addstr(y, x, "-", colour)
            else:
                self.stdscr.addstr(y, x, "|", colour)
        elif cellType == CellType.LAND:
            string = "#"
            worth = cell.getCellWorth()
            if worth == CellWorth.COPPER:
                string = "B"
            elif worth == CellWorth.SILVER:
                string = "S"
            elif worth == CellWorth.GOLD:
                string = "G"

            if cell.isClaimed() or worth == CellWorth.NORMAL:
                colour = self.getPlayerColour(playerOwner, False)
            else:
                colour = self.colourLandWorth

            self.stdscr.addstr(y, x, string, colour)
        elif cellType == CellType.BORDER:
            self.stdscr.addstr(y, x, " ")
        elif cellType == CellType.SKIP:
            self.stdscr.addstr(y, x, ".")

    def drawScores(self, playerScores, currentPlayer):
        offsetX = 40
        offsetY = 2
        for player in playerScores:
            currentColour = self.colourDefault
            if player.username == currentPlayer:
                currentColour = self.colourDefault | curses.A_BOLD
            self.stdscr.addstr(offsetY, offsetX, str(player.username), currentColour)
            
            colour = self.getPlayerColour(player.username, True)
            self.stdscr.addstr(offsetY, offsetX + 20, str(playerScores[player]), colour)
            offsetY += 1
    
    def drawStatistics(self, userStatistics, currentPlayer):
        if len(userStatistics) == 0:
            return

        offsetX = 40
        offsetY = 2
        self.stdscr.addstr(1, offsetX + 20, "User Statistics for " + currentPlayer, self.colourDefault | self.colourBold)
        self.stdscr.addstr(offsetY + 2, offsetX + 20, "Wins: ", self.colourDefault)
        self.stdscr.addstr(offsetY + 3, offsetX + 20, str(userStatistics["wins"]), self.colourDefault)
        self.stdscr.addstr(offsetY + 5, offsetX + 20, "Losses: ", self.colourDefault)
        self.stdscr.addstr(offsetY + 6, offsetX + 20, str(userStatistics["losses"]), self.colourDefault)
        self.stdscr.addstr(offsetY + 8, offsetX + 20, "Draws: ", self.colourDefault)
        self.stdscr.addstr(offsetY + 9, offsetX + 20, str(userStatistics["draws"]), self.colourDefault)

    def getPlayerColour(self, playerID, isFence):
        if(not playerID in self.landColoursPlayers):
            return curses.COLOR_WHITE
        if isFence:
            return self.fenceColoursPlayers[playerID]
        else:    
            return self.landColoursPlayers[playerID]
        
    def getElementPosition(self, elementName):
        self.currentMenu.getElementPosition(elementName)

    def setElementString(self, elementName, newString):
        self.currentMenu.getElement(elementName).setDisplayString(newString)
        
    def navigateMenu(self, currentElement, up):
        element = self.currentMenu.navigateMenu(currentElement, up)
        return element

    def onPlayerAdded(self, playerID, num):
        self.landColoursPlayers[playerID] = self.landColours[num]
        self.fenceColoursPlayers[playerID] = self.fenceColours[num]

    def onPlayerRemoved(self, playerID):
        if playerID in self.landColoursPlayers:
            del self.landColoursPlayers[playerID]
        if playerID in self.fenceColoursPlayers:
            del self.fenceColoursPlayers[playerID]

    def displayError(self, message):
        self.stdscr.addstr(10, 1, str(message))