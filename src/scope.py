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

    def addTypeDef(self, name, type) :
        self.typeDefs[name] = type