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