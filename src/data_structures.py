
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

    def addSymbol(self, name, type, node = 'None') :
        self.symbolTable[name] = {'type' : type, 'node' : node}
        print(f"Added symbol {name}")

    def addTypeDef(self, name, type) :
        self.typeDefs[name] = type

class Node:
    def __init__(self, name, kind, type=None, value = 0):
        self.name = name    # name of Node
        self.type = type    # type of Node
        self.childList = [] # childrens of Node
        self.kind = kind    # Kind of Node
        self.value = value
        self.visited = False

    def __str__(self):
        return f"name : {self.name} \nkind : {self.kind} \ntype{self.type}\n"