# from collections import OrderedDict

class SymbolTable:
    def __init__(self,parent=None):
        # identifiers in symbol table has fields like type
        self.symbolTable = {}
        self.parent = parent
        self.functions = {}
        self.metadata = {}
        self.metadata['name'] = 'global'
        self.metadata['total_offset'] = 0
        # Used when function is declared first and then defined later
        self.maybe = []
        self.maybeScope = {}

    def lookUp(self, id):
        if id in self.symbolTable.keys() :
            return True
        return False

    def add(self, id,type_) :
        if (not self.lookUp(id)):
            self.symbolTable[id] = {'type' : type_}

    def get(self,id):
        if(self.lookUp(id)):
            return (self.symbolTable)[id]
        return None

    def update(self,id,key,value):
        try:
            (self.symbolTable)[id][key] = value
            return True
        except KeyError:
            return False

class Node:
    def __init__(self, name):
        self.name = name    # name of Node
        # self.type = type    # type of Node
        # self.childList = [] # childrens of Node
        # self.kind = kind    # Kind of Node
        # self.value = value
        # self.visited = False
        self.code = []
        self.typeList = []
        self.placeList = []
        self.identList = []
        self.sizeList = []
        self.extra = {}
        self.scopeInfo = []

    
    def __str__(self):
        return f"name : {self.name} \ntype{self.typeList}\n"