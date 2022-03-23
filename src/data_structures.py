
from collections import OrderedDict

class Scope:
    def __init__(self,parent=None,isGlobal = False):
        self.typeDefs = OrderedDict()
        self.symbolTable = OrderedDict()
        self.parent = parent
        self.isGlobal = isGlobal

    def lookUp(self, id):
        if id in self.symbolTable.keys() :
            return True
        return False

    def lookUpType(self, type):
        if type in self.typeDefs.keys() :
            return True
        return False

    def addSymbol(self, name, type) :
        self.symbolTable[name] = {'type' : type}
        print(f"Added symbol {name}")

    def addTypeDef(self, name, type) :
        self.typeDefs[name] = type

class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self.type = None
        self.parent = None