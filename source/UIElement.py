#!/usr/bin/env python
import curses

class UIElement:
    def __init__(self, name, posY, posX, defaultString, selectable):
        self.name = name
        self.position = [posY, posX]
        self.displayString = defaultString
        self.selectable = selectable
    
    def display(self, stdscr, highlight = False):
        colour = curses.color_pair(8) # default colour
        if highlight:
            colour = curses.color_pair(7) # selected

        offsettedY = self.position[0]
        offsettedX = self.position[1]
        stdscr.addstr(offsettedY, offsettedX, self.displayString, colour)

    def getPosition(self):
        return self.position
    
    def setDisplayString(self, string):
        self.displayString = str(string)

    def getDisplayString(self):
        return self.displayString

    def isSelectable(self):
        return self.selectable
    
    def getName(self):
        return self.name