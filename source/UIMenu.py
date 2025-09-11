#!/usr/bin/env python
from UIElement import UIElement

class UIMenu(UIElement):
    def __init__(self, offsetY, offsetX):
        self.offset = [int(offsetY), int(offsetX)]
        self.elements = []

    def addElement(self, element):
        self.elements.append(element)

    def getElement(self, name):
        for element in self.elements:
            if element.getName() == name:
                return element
        return None
    
    def GetElementPosition(self, name):
        return self.getElement(name).getPosition()

    def displayMenu(self, stdscr):
        for element in self.elements:
            element.display(stdscr)

    def navigateMenu(self, currentElement, up):
        if currentElement == None:
            for i in self.elements:
                if i.isSelectable():
                    return i

        if len(self.elements) < 2:
            return currentElement

        index = 0
        for i in range(len(self.elements)):
            if self.elements[i].getName() == currentElement.getName():
                index = i
                break
        
        maxTries = len(self.elements)
        while(maxTries > 0):
            if up:
                index -= 1
            else:
                index += 1

            if index < 0:
                index = 0
            elif index >= len(self.elements):
                index = len(self.elements) - 1
            
            if self.elements[index].isSelectable():
                return self.elements[index]
            maxTries -= 1
        
        return currentElement
    
    def clearElements(self):
        self.elements = []