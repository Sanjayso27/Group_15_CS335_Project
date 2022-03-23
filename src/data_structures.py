
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

    def addTypeDef(self, name, type) :
        self.typeDefs[name] = type
    
    

class Node:
    def __init__(self, name):
        self.name = name
        self.code = []
        self. typeList = []
        self.placeList = []
        self.code = []
