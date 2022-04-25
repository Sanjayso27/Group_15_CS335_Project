import sys
from lexer import LexerGo
from lexer import tokens
import ply.yacc as yacc
from helper import print_error, print_warn, print_csv, typestring
from collections import OrderedDict
from data_structures import SymbolTable, Node
import pygraphviz as pgv
# import logging
# log = logging.getLogger('ply')

rootNode = Node('rootNode')

class ParserGo:

    def __init__(self, data, filePath):
        self.filePath = filePath
        self.lexer = LexerGo()
        self.lexer.build()
        self.lexer.input(data)
        self.tokens = tokens
        self.precedence = (
            ('left', 'OR_OR'),
            ('left', 'AMP_AMP'),
            ('left', 'EQ_EQ', 'NOT_EQ', 'LT', 'LE', 'GT', 'GE'),
            ('left', 'PLUS', 'MINUS', 'OR', 'CARET'),
            ('left', 'STAR', 'DIVIDE', 'MODULO', 'LSHIFT', 'RSHIFT', 'AMP')
        )
        # self.curScope = Scope(isGlobal=True)    # contains current scope
        # self.scopeList = [self.curScope]        # contains list of all scopes
        # self.scopePtr = 1                       # next index of scope to insert
        self.scopeStack = []                      # contains all active scopes
        self.offsetStack = [0]                    # contains offsets of all active scopes
        # self.funcList = {}                      # contains all fucntions
        # self.curFunc = ''
        self.compileErrors = 0
        self.scope = 0
        self.symbolTables = []
        self.lastScope = 0
        self.varCount = 0
        self.labelCount = 0
        self.typeCount = 0
        self.type = {}
        self.type['int'] = {'size': 4, 'type': ['int']}
        self.type['bool'] = {'size': 4, 'type': ['bool']}
        self.type['string'] = {'size': 4, 'type': ['string']}
        self.type['float'] = {'size': 4, 'type': ['float']}
        self.newScope()

    def getBaseType(self, type_):
        if isinstance(type_, list):
            return type_
        return self.type[type_]['type']

    # type dictionary structure for :
    # basic types : self.type['int'] = {'size': 4, 'type': ['int']}
    # pointers : {'size': 4, 'type': basetype }
    # struct :  {'size': sz, 'type': types of fields }
    # arrays :  {'size': sz, 'type': base type }
    # this recursive function calculates the size of nD arrays and structures within structures as well due to its recursive nature
    def computeSize(self, type_):
        if isinstance(type_, str):
            return self.type[type_]['size']
        if type_[0] == 'pointer':
            return 4
        elif type_[0] == 'struct':
            sz = 0
            if isinstance(type_[1], str):
                return self.computeSize(type_[1])
            for key in type_[1]:
                sz += self.computeSize(type_[1][key]['type'])
            return sz
        elif type_[0] == 'array' :
            sz = self.computeSize(type_[1]['type'])
            return (type_[1]['len'] * sz)
        else:
            return self.type[type_[0]]['size']

    # creates a type name for unnamed types such as arrays,struct,pointer
    def addType(self, type_):
        typeName = 'type' + str(self.typeCount)
        self.typeCount += 1
        sz = self.computeSize(type_)
        self.type[typeName] = {'size': sz, 'type': type_}
        return typeName

    # we are also adding placeholders in 3AC in symbol table
    # creates a new variables as placeholders in 3AC
    def newVar(self, type_):
        var = 't' + str(self.varCount)
        if isinstance(type_, str):
            size_ = self.type[type_]['size']
        else:
            size_ = self.computeSize(type_)
        self.symbolTables[self.getScope()].add(var, type_)
        self.symbolTables[self.getScope()].update(var, 'size', size_)
        self.symbolTables[self.getScope()].update(var, 'offset', self.getOffset())
        self.updateOffset(size_)

        self.varCount += 1
        return var

    # Creates a new label useful in for,if statements
    def newLabel(self):
        label = "label" + str(self.labelCount)
        self.labelCount +=1
        return label

    def newOffset(self):
        self.offsetStack.append((self.getOffset()))

    def getOffset(self):
        return self.offsetStack[-1]
    
    def popOffset(self):
        return self.offsetStack.pop()

    def updateOffset(self,size):
        self.offsetStack[-1] += size

    def newScope(self,parent =None):
        newTable = SymbolTable(parent)
        # print(newTable.metadata['name'])
        newTable.metadata['scopeNo']=self.scope
        self.symbolTables.append(newTable)
        self.scopeStack.append(self.scope)
        self.newOffset()
        self.scope +=1

    def getScope(self):
        return self.scopeStack[-1]

    def endScope(self):
        scope = self.getNearest("func")
        if(scope != -1):
            self.symbolTables[scope].metadata['total_offset'] += self.getWidth(self.getScope())
        self.lastScope = self.scopeStack.pop()
        self.popOffset()

    def checkId(self,identifier,type_='default'):
        if identifier in self.symbolTables[0].functions.keys():
            return True
        
        if type_ == "global":
            if self.symbolTables[0].lookUp(identifier) is True:
                return True
            return False

        if type_ == "current":
            if self.symbolTables[self.getScope()].lookUp(identifier) is True:
                return True
            return False

        #default case going through scopes in the stack up to check whether it's declared or not
        for scope in self.scopeStack[::-1]:
            if self.symbolTables[scope].lookUp(identifier) is True:
                return True
        return False

    # finding info about a global or local variable or type
    def findInfo(self, identifier, type_='default'):
        if type_ == 'global':
            if self.symbolTables[0].get(identifier) is not None:
                return self.symbolTables[0].get(identifier)

        else:
            for scope in self.scopeStack[::-1]:
                if self.symbolTables[scope].get(identifier) is not None:
                    return self.symbolTables[scope].get(identifier)
                    
        return None
    
    def findScope(self, identifier):
        for scope in self.scopeStack[::-1]:
            if self.symbolTables[scope].get(identifier) is not None:
                return scope
    
    # return nearest parent scope with name in metadata = type_(func, for), -1 if no such scope exist
    def getNearest(self, type_):
        for scope in self.scopeStack[::-1]:
            # print(scope)
            # print(self.symbolTables[scope].metadata)
            if self.symbolTables[scope].metadata['name'] == type_:
                return scope
        return -1

    def compareType(self, tp1, tp2):
        # given 2 types (in compact form), checks whether they denote same type or not
        if isinstance(tp1, str):
            tp1 = self.getBaseType(tp1)
        if isinstance(tp2, str):
            tp2 = self.getBaseType(tp2)
        
        # to handle the case of linked list (pointer to struct)
        try:
            if tp1[0] == 'pointer' and tp1[1][0] == 'struct' and isinstance(tp1[1][1], str):
                tp1 = ['pointer', self.getBaseType(tp1[1][1])]
        except:
            pass
        try:
            if tp2[0] == 'pointer' and tp2[1][0] == 'struct' and isinstance(tp2[1][1], str):
                tp2 = ['pointer', self.getBaseType(tp2[1][1])]
        except:
            pass

        try:
            if tp1[0] == 'struct' and isinstance(tp1[1], str):
                tp1 = self.getBaseType(tp1[1])
        except:
            pass
        
        try:
            if tp2[0] == 'struct' and isinstance(tp2[1], str):
                tp2 = self.getBaseType(tp2[1])
        except:
            pass

        return tp1==tp2

    def checkArguments(self, name, arguments):
        if not (name in self.symbolTables[0].functions.keys()):
            return -1

        funcScope = self.symbolTables[0].functions[name]
        for scp in funcScope:
            funcMeta = self.symbolTables[scp].metadata
            val = 1
            if funcMeta['num_arg'] == len(arguments):
                for i in range(len(arguments)):
                    expectedTp = funcMeta['signature'][i]
                    if not self.compareType(arguments[i], expectedTp):
                        val = 0
                if val:
                    return str(scp)

        return 'arguments do not match any function signature'

    def getWidth(self, scope):
        symTable = self.symbolTables[scope]
        width = 0
        for ident in symTable.symbolTable:
            size_ = self.computeSize(symTable.get(ident)['type'])
            width += size_
        return width

    def getParamWidth(self, scope):
        symTable = self.symbolTables[scope]
        width = 0
        for ident in symTable.symbolTable:
            info = symTable.get(ident)
            if 'is_arg' in info.keys():
                width += self.type[info['type']]['size']
        return width
    
    # def popScope(self):
    #     self.scopeStack.pop()
    #     self.curScope = self.scopeList[self.scopeStack[-1]]

    # def pushScope(self):
    #     self.scopeStack.append(self.scopePtr)
    #     self.curScope = Scope()
    #     self.scopeList.append(self.curScope)
    #     self.scopePtr += 1

    def pos(self, lexpos):
        return (self.lexer.tokenList[lexpos][2], self.lexer.tokenList[lexpos][3])

    def build(self):
        self.parser = yacc.yacc(module=self, start='SourceFile', method='LALR', debug=False)

    def p_error(self, p) :
        if p is not  None :
            self.compileErrors +=1
            msg = f"Found unexpexted token {p.value}"
            print_error(msg, self.lexer.tokenList[p.lexpos][2], self.lexer.tokenList[p.lexpos][3])

    # def p_lcurly(self, p):
    #     '''
    #     lcurly  : LCURLY
    #     '''
    
    # def p_rcurly(self, p):
    #     '''
    #     rcurly  : RCURLY
    #     '''

    def p_Type(self, p):
        '''
        Type    : TypeName
                | TypeLit
        '''
        p[0] = p[1]
        p[0].name = 'Type'

    def p_TypeName(self, p):
        '''
        TypeName	: ID
                    | DATA_TYPE
        '''
        p[0] = Node('TypeName')
        if p[1] in self.type:
            p[0].typeList.append(p[1])
        else:
            self.compileErrors +=1
            message = "Type undefined!"
            print_error(message,*(self.pos(p.lexpos(1))))


    def p_TypeLit(self, p):
        '''
        TypeLit	: ArrayType 
                | StructType 
                | PointerType 
                | SliceType
        '''
        p[0] = p[1]
        p[0].name = "TypeLit"
        
    def p_ArrayType(self, p):
        '''
        ArrayType : LSQUARE ArrayLength RSQUARE ElementType
        '''
        p[0] = Node('ArrayType')
        if p[2].extra['count'] < 0:
            self.compileErrors +=1
            message = "Array size must be +ve"
            print_error(message,*(self.pos(p.lexpos(2))))
            return
        newArr = self.addType(['array',{
            'type': self.getBaseType(p[4].typeList[0]),
            'len': p[2].extra['count']
        }])
        p[0].typeList.append(newArr)

    def p_ArrayLength(self, p):
        '''
        ArrayLength : INT_LIT
        '''
        p[0] = Node('ArrayLength')
        p[0].extra['count'] = int(p[1])
    
    def p_SliceType(self, p):
        '''
        SliceType 	: LSQUARE RSQUARE ElementType
        '''
        p[0] = Node('SliceType')
        newSlice = self.addType(['slice', {
            'type': self.getBaseType(p[4].typeList[0]),
            'len':  0
        }])
        p[0].typeList.append(newSlice)
    
    def p_ElementType(self, p):
        '''
        ElementType : Type
        '''
        p[0] = p[1]
        p[0].name = 'ElementType'
    
    def p_PointerType(self, p):
        '''
        PointerType	: STAR BaseType
        '''
        p[0] = Node("PointerType")
        baseType = self.getBaseType(p[2].typeList[0])
        newPointer = self.addType(["pointer",baseType])
        p[0].typeList.append(newPointer)

    def p_BaseType(self, p):
        '''
        BaseType	: Type
        '''
        p[0] = p[1]
        p[0].name = "BaseType"
    
    # Used to deal with linked list type of structures
    def p_structLcurly(self,p):
        '''
        structLcurly  : LCURLY
        '''
        # print(p[-2])
        self.type[p[-2]] = {
            "type": ["struct",p[-2]],
            "size": 0
        }
    
    def p_structRcurly(self,p):
        '''
        structRcurly  : RCURLY
        '''
        self.type.pop(p[-4])

    def p_StructType(self, p):
        '''
        StructType 	: STRUCT structLcurly FieldDeclList structRcurly
        '''
        for id in range(len(p[3].identList)):
            if(p[3].identList[id] in p[3].identList[:id]):
                self.compileErrors +=1
                message = f"Field {p[3].identList[id]} redeclared"
                print_error(message,*(self.pos(p.lexpos(3))))
                return
        p[0] = p[3]
        dict_ = {}
        offset_ = 0
        for id in range(len(p[3].identList)):
            baseType = self.getBaseType(p[3].typeList[id])
            sz = self.computeSize(baseType)
            dict_[p[3].identList[id]] = {
                "type" : baseType,
                "size" : sz,
                "offset": offset_
            }
            offset_ +=sz
        newStruct = self.addType(["struct",dict_])
        p[0].typeList = [newStruct]
        p[0].name = "StructType"

    def p_FieldDeclList(self, p):
        '''
        FieldDeclList 	: FieldDeclList FieldDecl SEMICOLON 
                        | FieldDecl SEMICOLON
        '''
        p[0] = p[1]
        p[0].name = "FieldDeclList"
        if len(p) == 4:
            p[0].identList += p[2].identList
            p[0].typeList += p[2].typeList

    def p_FieldDecl(self, p):
        '''
        FieldDecl 	: IdentifierList Type
        '''
        p[0] = p[1]
        p[0].name = "FieldDecl"

        p[0].typeList = [p[2].typeList[0] for _ in p[1].identList]
    
    def p_Block(self, p):
        '''
        Block	: LCURLY StatementList RCURLY
                | LCURLY RCURLY
        '''
        if(len(p)==3):
            p[0]= Node("Block")
        else :
            p[0]=p[2]
            p[0].name = "Block"
    
    # def p_pushBlock(self, p):
    #     '''
    #     pushBlock   : 
    #     '''
    #     if self.curFunc != '':
    #         if(self.funcList[self.curFunc] == {}):
    #             self.funcList[self.curFunc]["scopeList"] = []
    #         self.funcList[self.curFunc]['scopeList'].append(self.scopePtr)
    #         # if(not ("scopeList" in self.funcList[self.curFunc].keys)):
    #     self.pushScope()

    # def p_popBlock(self, p):
    #     '''
    #     popBlock   : 
    #     '''
    #     self.popScope()
    
    def p_StatementList(self, p):
        '''
        StatementList 	: StatementList Statement SEMICOLON
                        | Statement SEMICOLON
        '''
        p[0]=p[1]
        p[0].name = "StatementList"
        if(len(p)==4):
            p[0].code +=p[2].code
            p[0].scopeInfo += p[2].scopeInfo
        # print(p[0])


    def p_Declaration(self, p):
        '''
        Declaration	: ConstDecl 
                    | TypeDecl 
                    | VarDecl 
        '''
        p[0]=p[1]
        p[0].name = "Declaration"
    
    def p_TopLevelDecl(self, p):
        '''
        TopLevelDecl	: Declaration 
                        | FunctionDecl 
                        | MethodDecl
        '''
        p[0] = p[1]
        p[0].name = "TopLevelDecl"

    def p_ConstDecl(self, p):
        '''
        ConstDecl	: CONST ConstSpec
        '''
        p[0]=p[2]
        p[0].name = "ConstDecl"
        for id in range(len(p[0].identList)):
            sz = self.type[p[0].typeList[id]]['size']
            # adding in symbol table
            if not self.symbolTables[self.getScope()].add(p[0].identList[id],p[0].typeList[id]) :
                self.compileErrors +=1
                message =  f"Variable {p[0].identList[id]} already declared"
                print_error(message,*(self.pos(p.lexpos(2))))
                pass
            # updating the info about is_const ,offset,size in the symbol table entry corr. to id
            self.symbolTables[self.getScope()].update(p[0].identList[id],'is_const',True)
            self.symbolTables[self.getScope()].update(p[0].identList[id],"offset",self.getOffset())
            self.symbolTables[self.getScope()].update(p[0].identList[id],"size",sz)
            self.updateOffset(sz)

    def p_ConstSpec(self, p):
        '''
        ConstSpec   :	IdentifierList EQ ExpressionList
                    |   IdentifierList Type EQ ExpressionList
        '''
        p[0]=p[1]
        if len(p)==4:
            p[0].code += p[3].code
            p[0].scopeInfo +=p[3].scopeInfo
            if len(p[1].identList) != len(p[3].typeList):
                self.compileErrors +=1
                message = f"{len(p[1].identList)} constants but {len(p[3].typeList)} values"
                print_error(message,*(self.pos(p.lexpos(2))))
            for id in range(len(p[1].identList)):
                p[0].typeList[id] = p[3].typeList[id]
                p[0].code.append(["=",p[1].identList[id],p[3].placeList[id]])
                p[0].scopeInfo.append(["",self.getScope(),self.findScope(p[3].placeList[id])])
            p[0].placeList = p[3].placeList
            p[0].name = "ConstSpec"
        elif len(p)==5:
            p[0].code += p[4].code
            p[0].scopeInfo +=p[4].scopeInfo
            for i in range(len(p[1].identList)):
                p[0].typeList.append(p[2].typeList[0])
            if len(p[1].identList) != len(p[4].typeList):
                self.compileErrors +=1
                message = f"{len(p[1].identList)} constants but {len(p[4].typeList)} values"
                print_error(message,*(self.pos(p.lexpos(2))))
            for type_ in p[4].typeList:
                if not self.compareType(type_,p[2].typeList[0]):
                    self.compileErrors +=1
                    message = f"{type_} assignment to {p[2].typeList[0]}"
                    print_error(message,*(self.pos(p.lexpos(2))))
            for id in range(len(p[1].identList)):
                p[0].code.append(["=",p[1].identList[id],p[4].placeList[id]])
                p[0].scopeInfo.append(["",self.getScope(),self.findScope(p[4].placeList[id])])
            p[0].placeList = p[4].placeList
            p[0].name = "ConstSpec"

    def p_IdentifierList(self, p):
        '''
        IdentifierList	: IdentifierList COMMA ID
                        | ID
        '''
        if len(p)==2:
            p[0] = Node("IdentifierList")
            p[0].identList.append(p[1])
            p[0].placeList.append(p[1])
        else :
            p[0]=p[1]
            p[0].name = 'IdentifierList'

            if self.checkId(p[1],"current") or (p[3] in p[1].identList):
                self.compileErrors +=1
                message = f"{p[3]} already declared"
                print_error(message,*(self.pos(p.lexpos(3))))
            else:
                p[0].identList.append(p[3])
                p[0].placeList.append(p[3])

    def p_ExpressionList(self, p):
        '''
        ExpressionList	: ExpressionList COMMA Expression
                        | Expression
        '''
        p[0]=p[1]
        p[0].name = "ExpressionList"
        if len(p)==4 :
            p[0].code += p[3].code
            p[0].scopeInfo += p[3].scopeInfo
            p[0].placeList += p[3].placeList
            p[0].typeList += p[3].typeList
            p[0].extra['deref'] += p[3].extra['deref']
    
    def p_TypeDecl(self, p):
        '''
        TypeDecl	: TYPE ID Type
        '''
        p[0]=Node("TypeDecl")
        if p[2] in self.type:
            self.compileErrors +=1
            message =  f"Type {p[2]} already declared"
            print_error(message,*(self.pos(p.lexpos(2))))
        else :
            self.type[p[2]] = self.type[p[3].typeList[0]]

    def p_VarDecl(self, p):
        '''
        VarDecl	: VAR VarSpec 
        '''
        p[0]=p[2]
        # print(self.type)
        p[0].name = "VarDecl"
        for id in range(len(p[0].identList)):
            sz = self.type[p[0].typeList[id]]['size']
            # adding in symbol table
            if not self.symbolTables[self.getScope()].add(p[0].identList[id],p[0].typeList[id]) :
                self.compileErrors +=1
                message =  f"Variable {p[0].identList[id]} already declared"
                print_error(message,*(self.pos(p.lexpos(2))))
                pass
            # updating the info about is_const ,offset,size in the symbol table entry corr. to id
            self.symbolTables[self.getScope()].update(p[0].identList[id],"offset",self.getOffset())
            self.symbolTables[self.getScope()].update(p[0].identList[id],"size",sz)
            # print(sz)
            self.updateOffset(sz)

    def p_VarSpec(self, p):
        '''
        VarSpec	: IdentifierList Type 
                | IdentifierList Type EQ ExpressionList
        '''
        p[0]=p[1]
        if len(p)==5:
            p[0].code += p[4].code
            p[0].scopeInfo +=p[4].scopeInfo
            for i in range(len(p[1].identList)):
                p[0].typeList.append(p[2].typeList[0])
            if len(p[1].identList) != len(p[4].typeList):
                self.compileErrors +=1
                message = f"{len(p[1].identList)} variables but {len(p[4].typeList)} values"
                print_error(message,*(self.pos(p.lexpos(2))))
            else :
                for type_ in p[4].typeList:
                    if not self.compareType(type_,p[2].typeList[0]):
                        self.compileErrors +=1
                        message = f"{type_} assignment to {p[2].typeList[0]}"
                        print_error(message,*(self.pos(p.lexpos(2))))
                        return
                for id in range(len(p[4].placeList)):
                    p[0].code.append(["=",p[1].identList[id],p[4].placeList[id]])
                    # why below line needed and what is stored in placelist
                    p[0].scopeInfo.append(["",self.getScope(),self.findScope(p[4].placeList[id])])
                p[0].placeList = p[4].placeList
        else :
            for i in range(len(p[1].identList)):
                # print(p[2].typeList[0])
                p[0].typeList.append(p[2].typeList[0])           
        p[0].name = "VarSpec"

    def p_ShortVarDecl(self, p):
        '''
        ShortVarDecl : IdentifierList ASSIGN ExpressionList
        '''
        p[0] = p[1]
        p[0].name = "ShortVarDecl"
        p[0].code += p[3].code
        p[0].scopeInfo += p[3].scopeInfo
        if len(p[1].identList) != len(p[3].typeList):
            message = f"{len(p[1].identList)} short variables but {len(p[3].typeList)} values"
            self.compileErrors +=1
            print_error(message,*(self.pos(p.lexpos(2))))
        for id in range(len(p[0].identList)):
            sz = self.type[p[3].typeList[id]]['size']
            if not self.symbolTables[self.getScope()].add(p[0].identList[id],p[3].typeList[id]) :
                self.compileErrors +=1
                message =  f"Variable {p[0].identList[id]} already declared"
                print_error(message,*(self.pos(p.lexpos(2))))
                pass
            self.symbolTables[self.getScope()].update(p[0].identList[id],"offset",self.getOffset())
            self.symbolTables[self.getScope()].update(p[0].identList[id],"size",sz)
            self.updateOffset(sz)
            p[0].code.append(["=",p[0].identList[id],p[3].placeList[id]])
            p[0].scopeInfo.append(['',self.getScope(),self.findScope(p[3].placeList[id])])

    # def dfs(self, node, G):
    #     G.add_node(id(node), label=node.name)
    #     node.visited = True
    #     for i, child in enumerate(node.childList) :
    #         if child is not None:
    #             if not child.visited :
    #                 G.add_node(id(child), label=child.name)
    #                 self.dfs(child, G)
    #             G.add_edge(id(node), id(child), label=str(i))
    
    # maybe declare and define later
    def p_FunctionDecl(self, p):
        '''
        FunctionDecl 	: FUNC FunctionName CreateScope Signature FunctionBody EndScope
        '''
        p[0] = p[5]
        p[0].name = "FunctionDecl"
        funcScope = self.symbolTables[0].functions[p[2].extra['name']][-1]
        if "empty" not in p[5].extra:
            # check whether it's already declared but not defined by checking the maybe list
            if p[2].extra["name"] in self.symbolTables[0].maybe:
                newfuncScope = self.symbolTables[0].maybeScope[p[2].extra['name']]
                p[0].code.insert(0,[p[2].extra['name']+str(newfuncScope)+'::'])  
                p[0].scopeInfo.insert(0,[''])
                self.symbolTables[0].functions[p[2].extra['name']+str(newfuncScope)] = funcScope
            # fresh function
            else:
                p[0].code.insert(0,[p[2].extra['name']+str(funcScope)+'::'])
                p[0].scopeInfo.insert(0,[''])
                self.symbolTables[0].functions[p[2].extra['name']+str(funcScope)] = funcScope
        else:
            # just declaring now will define later
            self.symbolTables[0].maybe.append(p[2].extra['name'])    
            self.symbolTables[0].maybeScope[p[2].extra['name']] = funcScope

    def p_FunctionName(self, p):
        '''
        FunctionName	: ID
        '''
        p[0] = Node("FunctionName")
        p[0].extra["name"] = p[1]
        if p[1] not in self.symbolTables[0].functions:
            self.symbolTables[0].functions[p[1]] = [self.scope]
        else:
            self.symbolTables[0].functions[p[1]].append(self.scope)

    def p_Signature(self, p):
        '''
        Signature      	: Parameters
                        | Parameters Result
        '''
        p[0] = Node('Signature')
        # msg = self.updateSignature(p[1].typeList)
        scope = self.getNearest('func')
        fname  = self.symbolTables[scope].metadata['is_function']
        funcScope = self.symbolTables[0].functions[fname]

        sameSig = 0
        for idx in range(len(funcScope)-1):
            if self.symbolTables[funcScope[idx]].metadata['signature'] == p[1].typeList:
                sameSig += 1

        for idx in range(len(funcScope)-1):
            if fname in self.symbolTables[0].maybe:
                sameSig = 0
        if sameSig > 0:
            self.compileErrors +=1
            print_error('function ' + fname + ' redeclared',*(self.pos(p.lexpos(2))))
            return
        self.symbolTables[scope].metadata['signature'] = p[1].typeList
        self.symbolTables[scope].metadata['num_arg'] = len(p[1].typeList)
        if len(p)==3:
            scope_ = self.getNearest('func')
            self.symbolTables[scope_].metadata['retvaltype'] = p[2].typeList
            retValSize = [self.type[x]["size"] for x in p[2].typeList]
            self.symbolTables[scope_].metadata['retvalsize'] = retValSize
        else :
            scope_ = self.getNearest('func')
            self.symbolTables[scope_].metadata['retvaltype'] = []
            self.symbolTables[scope_].metadata['retvalsize'] = []
        
    def p_Parameters(self, p):
        '''
        Parameters 	: LROUND ParameterList RROUND
                    | LROUND RROUND
        '''
        p[0] = Node("Parameters")
        if len(p) == 4:
            p[0]=p[2]
            p[0].name = 'Parameters'
            for index_ in range(len(p[2].typeList)):
                sz = self.type[p[2].typeList[index_]]['size']
                self.symbolTables[self.getScope()].add(p[2].identList[index_], p[2].typeList[index_])
                # updating the info about is_arg ,offset,size in the symbol table entry corr. to id
                self.symbolTables[self.getScope()].update(p[2].identList[index_], 'size', sz)
                self.symbolTables[self.getScope()].update(p[2].identList[index_], 'offset', self.getOffset())
                self.symbolTables[self.getScope()].update(p[2].identList[index_], 'is_arg', True)
                self.updateOffset(sz)

    def p_ParameterList(self, p):
        '''
        ParameterList	: ParameterList COMMA ParameterDecl 
                        | ParameterDecl
        '''
        p[0]=p[1]
        p[0].name = "ParameterList"
        if len(p)==4:
            p[0].placeList += p[3].placeList
            p[0].identList += p[3].identList
            p[0].typeList += p[3].typeList
    
    # not allowing identifier list here
    def p_ParameterDecl(self, p):
        '''
        ParameterDecl	: ID Type
        '''
        p[0] = Node("ParameterDecl")
        p[0].placeList = [p[1]]
        p[0].identList = [p[1]]
        p[0].typeList = p[2].typeList
    
    def p_Result(self, p):
        '''
        Result 	: Type
        '''
        p[0] = p[1]
        p[0].name = "Result"

    def p_CreateScope(self,p):
        '''
        CreateScope :
        '''
        p[0] = Node('CreateScope')
        self.newScope(self.getScope())
        type_ = 'none'
        # for blocks 
        # here p[-1] will be the token for
        if isinstance(p[-1], str):
            type_ = p[-1]
        # for functions
        elif isinstance(p[-1], Node):
            if p[-1].name == 'FunctionName':
                type_ = 'func'
                #  this metadata is used for getting the name of function which is used for checking whether the function is redeclared or not
                self.symbolTables[self.getScope()].metadata['is_function'] = p[-1].extra['name']

        # these labels are useful in for blocks ,if else blocks
        self.symbolTables[self.getScope()].metadata['start'] =  self.newLabel()
        self.symbolTables[self.getScope()].metadata['end'] =  self.newLabel()
        # this name field in metadata is used for finding the nearest scope which is useful in continue statements 
        self.symbolTables[self.getScope()].metadata['name'] = type_
        self.symbolTables[self.getScope()].metadata['update'] = self.newLabel()
        self.symbolTables[self.getScope()].metadata['condition'] = self.newLabel()

    def p_EndScope(self,p):
        '''
        EndScope :
        '''
        p[0] = Node('EndScope')
        self.endScope()

    def p_FunctionBody(self, p):
        '''
        FunctionBody	: Block
                        | 
        '''
        if len(p)==2:
            p[0] = p[1]
            p[0].name = "FunctionBody"
        else :
            p[0]=Node("FunctionBody")
            p[0].extra['empty'] = True
    
    # MethodDecl TODO:
    def p_MethodDecl(self, p):
        '''
        MethodDecl	: FUNC Receiver MethodName Signature
                    | FUNC Receiver MethodName Signature FunctionBody
        '''

    def p_MethodName(self, p):
        '''
        MethodName  : ID
        '''

    def p_Receiver(self, p):
        '''
        Receiver	: LROUND ParameterDecl RROUND
        '''

    def p_Operand(self, p):
        '''
        Operand : Literal 
                | OperandName
                | LROUND Expression RROUND
        '''
        if len(p) == 4 :
            p[0] = p[2]
        else :
            p[0] = p[1]
        p[0].name = "Operand"

    def p_Literal(self, p):
        '''
        Literal	: BasicLit 
                | CompositeLit
        '''
        p[0] = p[1]
        p[0].name = "Literal"
    
    def p_BasicLit(self, p):
        '''
        BasicLit	: IntLit
                    | FloatLit
                    | StrLit
                    | BoolLit
                    | CharLit
                    | NilLit
        '''
        p[0] = p[1]
        p[0].name = "BasicLit"

    # basic literals we are using
    def p_IntLit(self, p):
        '''
        IntLit  : INT_LIT
        '''
        p[0] = Node("IntLit")
        p[0].typeList.append("int")
        newVar = self.newVar('int')
        p[0].code.append(['=', newVar, int(p[1])])
        p[0].scopeInfo.append(['', self.getScope() , 'int_literal'])
        p[0].placeList.append(newVar)

    def p_FloatLit(self, p):
        '''
        FloatLit    : FLOAT_LIT
        '''
        p[0] = Node('FloatLit')
        p[0].typeList.append('float')
        newVar = self.newVar('float')
        p[0].code.append(['=', newVar, float(p[1])])
        p[0].scopeInfo.append(['', self.getScope() , 'literal'])
        p[0].placeList.append(newVar)

    def p_StrLit(self, p):
        '''
        StrLit  : STRING_LIT
        '''
        p[0] = Node('StringLit')
        p[0].typeList.append('string')
        newVar = self.newVar('string')
        p[0].code.append(['=', newVar, p[1]])
        p[0].scopeInfo.append(['', self.getScope() , 'literal'])
        p[0].placeList.append(newVar)
    
    def p_BoolLit(self, p):
        '''
        BoolLit : BOOL_LIT
        '''
        p[0] = Node('BoolLit')
        p[0].typeList.append('bool')
        newVar = self.newVar('bool')
        p[0].code.append(['=', newVar, p[1]])
        p[0].scopeInfo.append(['', self.getScope() , 'literal'])
        p[0].placeList.append(newVar)
    
    # TODO:
    def p_CharLit(self, p):
        '''
        CharLit : CHAR_LIT
        '''
        p[0] = Node('CharLit')
        # p[0].typeList.append('string')
        # newVar = self.newVar('string')
        # p[0].code.append(['=', newVar, p[1]])
        # p[0].scopeInfo.append(['', self.getScope() , 'literal'])
        # p[0].placeList.append(newVar)
    

    #TODO: 
    def p_NilLit(self, p):
        '''
        NilLit  : NIL
        '''
        p[0] = Node("NilLit")
    
    def p_OperandName(self, p):
        '''
        OperandName : ID 
        '''
        p[0] = Node("OperandName")
        # print(p[1])
        if self.checkId(p[1],"default"):
            type_ = self.findInfo(p[1],"default")
            p[0].typeList.append(type_["type"])
            p[0].placeList.append(p[1])
        else :
            msg = f"Using variable before declaration {p[1]}"
            self.compileErrors +=1
            print_error(msg, *(self.pos(p.lexpos(1))))

    #TODO:
    def p_CompositeLit(self, p):
        '''
        CompositeLit	: LiteralType LiteralValue
        '''
    
    def p_LiteralType(self, p):
        '''
        LiteralType	: ArrayType 
                    | SliceType
                    | StructType
        ''' 
        # Reducing power of rule : No defined types will form composite literal
    
    def p_LiteralValue(self, p):
        '''
        LiteralValue 	: LCURLY RCURLY
                        | LCURLY ElementList RCURLY
        '''
    
    def p_ElementList(self, p):
        '''
        ElementList	: Element
                    | ElementList COMMA Element
        '''
    
    def p_Element(self, p):
        '''
        Element : Expression
                | LiteralValue
        '''
    
    # for function changed PrimaryExpr Arguments -> ID Arguments
    def p_PrimaryExpr(self, p):
        '''
        PrimaryExpr	: Operand 
                    | PrimaryExpr Selector 
                    | PrimaryExpr Index 
                    | ID Arguments
                    | MakeExpr
        '''
        if len(p)==2 and p[1].name == "Operand" :
            p[0] = p[1]
            p[0].name = "PrimaryExpr"

        elif p[2].name == 'Arguments' :
            p[0]=p[2]
            msg = self.checkArguments(p[1],p[2].typeList)
            if isinstance(msg,int):
                self.compileErrors +=1
                print_error('Function %s not defined'%p[1],*(self.pos(p.lexpos(1))))
            elif msg[0] == 'a':
                self.compileErrors +=1
                print_error( msg,*(self.pos(p.lexpos(1))))
            else:
                funcScope = int(msg)
                for arg in p[2].placeList:
                    data_ = self.symbolTables[self.findScope(arg)].get(arg)
                    baseType = self.getBaseType(data_['type'])
                    if baseType[0] in ['int', 'bool', 'float', 'string']:
                        p[0].code.append(['param_base', arg])
                    else :
                        p[0].code.append(['param_complex', arg])
                    p[0].scopeInfo.append(['', self.findScope(arg)])
                p[0].code.append(['call', p[1] + str(funcScope), len(p[2].placeList)])
                p[0].scopeInfo.append(['', 'function', 'int'])
                type_ = self.symbolTables[funcScope].metadata['retvaltype']
                size_ = self.symbolTables[funcScope].metadata['retvalsize']
                p[0].typeList = type_
                newVar1 = self.newVar(type_)
                p[0].code.append(['retval', newVar1, 'eax'])
                p[0].scopeInfo.append(['', self.findScope(newVar1), ''])
                p[0].identList = [newVar1]
                p[0].sizeList = size_
                p[0].placeList = p[0].identList
                p[0].name = "PrimaryExpr"


        elif p[2].name == 'Index' :
            p[0] = p[1]
            p[0].code += p[2].code
            p[0].scopeInfo += p[2].scopeInfo
            rawType = self.getBaseType(p[1].typeList[0])
            if not self.compareType(p[2].typeList[0], 'int'):
                return 
            elif rawType[0] != 'array' and rawType[0] != 'pointer':
                self.compileErrors +=1
                print_error('type ' + str(rawType) + ' does not support indexing',*(self.pos(p.lexpos(1))))
            else:
                # this arrayElementp is added to support accesses in multi-D arrays
                arrayElemtp = self.addType(rawType[1]['type'])
                newVar1 = self.newVar('int')
                self.symbolTables[self.getScope()].update(newVar1, 'type', arrayElemtp)
                newVar2 = self.newVar('int')
                arrayElemSz = self.type[arrayElemtp]['size']
                # the array acces 3AC code consists of 2 parts
                # first we calculate the offset of the element accessed in the stack
                # for this calculation we need arrayElementSz and the offset whose placeholder is p[2].placeList[0] and this offset is stored in newVar2
                # now the offset of the base is available from symbolTable and we can access it using p[1].placeList[0] 
                # now using this base and offset we will get the array element
                p[0].code.append(['array*', newVar2, p[2].placeList[0], arrayElemSz])
                p[0].scopeInfo.append(['', self.getScope(), self.findScope(p[2].placeList[0]), 'literal'])
                p[0].code.append(['array+', newVar1, p[1].placeList[0], newVar2])
                p[0].scopeInfo.append(['', self.getScope(), self.findScope(p[1].placeList[0]), self.getScope()])
                p[0].placeList = [newVar1]
                p[0].typeList = [arrayElemtp]
                self.symbolTables[self.getScope()].update(newVar1, 'reference', True)
                p[0].extra['isIndex'] = True

        elif p[2].name == 'Selector':
            p[0] = p[1]
            baseType = self.getBaseType(p[1].typeList[0])
            ident = p[2].extra['ident']
            if isinstance(baseType[1], str):
                baseType[1] = self.getBaseType(baseType[1])[1]
            if baseType[0] != 'struct':
                self.compileErrors +=1
                print_error('With period we must have struct type',*(self.pos(p.lexpos(1))))
            elif ident not in baseType[1]:
                err_ = 'Name ' + str(baseType[1]) + ' has no field, or method called ' + ident
                self.compileErrors +=1
                print_error(err_,*(self.pos(p.lexpos(1))))
            else:
                # for supporting structs within struct we are adding it in the type dictionary
                identType = self.addType(baseType[1][ident]['type'])
                newVar1 = self.newVar('int')
                self.symbolTables[self.getScope()].update(newVar1, 'type', identType)
                # the struct field access 3Ac code consists of first getting the offset of the base structure from the symbolTable
                # then using the offset of the field accessed we can calculate the location of this field element in the stack
                p[0].code.append(['struct+', newVar1, p[1].placeList[0], baseType[1][ident]['offset']])
                p[0].scopeInfo.append(['', self.getScope(), self.findScope(p[1].placeList[0]), 'offset'])
                p[0].placeList = [newVar1]
                p[0].identList = p[0].placeList
                p[0].typeList = [identType]
                self.symbolTables[self.getScope()].update(newVar1, 'reference', True)
        
        # handle MakeExpr
        else :
            p[0] = p[1]
        # if(isinstance(p[0],str)):
        #     print(len(p),p[2].name)
    
    # TODO:
    def p_MakeExpr(self, p):
        '''
        MakeExpr    : MAKE LROUND SliceType COMMA Expression COMMA Expression RROUND
                    | MAKE LROUND SliceType COMMA Expression RROUND
        '''

    def p_Selector(self, p):
        '''
        Selector	: DOT ID
        '''
        p[0]=Node("Selector")
        p[0].extra["ident"]=p[2]
    
    def p_Index(self, p):
        '''
        Index	: LSQUARE Expression RSQUARE
        '''
        p[0]=p[2]
        p[0].name = "Index"
        if not self.compareType(p[2].typeList[0],"int"):
            self.compileErrors +=1
            print_error("Index type should be integer",*(self.pos(p.lexpos(2))))
    
    def p_Arguments(self, p):
        '''
        Arguments	: LROUND ExpressionList RROUND
                    | LROUND RROUND
        '''
        if len(p)==3:
            p[0]=Node("Arguments")
        else :
            p[0]=p[2]
            p[0].name = "Arguments"

    def p_Expression(self, p):
        '''
        Expression 	: UnaryExpr 
                    | Expression OR_OR Expression
                    | Expression AMP_AMP Expression
                    | Expression EQ_EQ Expression
                    | Expression NOT_EQ Expression
                    | Expression LT Expression
                    | Expression GT Expression
                    | Expression LE Expression
                    | Expression GE Expression
                    | Expression PLUS Expression
                    | Expression MINUS Expression
                    | Expression STAR Expression
                    | Expression AMP Expression
                    | Expression OR Expression
                    | Expression CARET Expression
                    | Expression DIVIDE Expression
                    | Expression MODULO Expression
                    | Expression LSHIFT Expression
                    | Expression RSHIFT Expression
        '''
        p[0]=Node("Expression")
        if len(p) == 2 :
            p[0].typeList = p[1].typeList
            p[0].placeList = p[1].placeList
            p[0].code = p[1].code
            p[0].scopeInfo = p[1].scopeInfo
            p[0].extra['deref'] = p[1].extra['deref']
            # used to know the scope info in if_expr 
            p[0].extra['scope'] = self.getScope()
        else :
            p[0].extra['deref'] = ['no']
            temp = Node("temp")
            if p[2] in ["||","&&"]:
                temp.extra['opcode'] = p[2]
                temp.extra['bool'] = True
                temp.typeList.append('bool')
            elif p[2] in ["==",'!=', '<', '<=', '>', '>=']:
                temp.extra['opcode'] = p[2]
                if p[1] in ['==', '!=']:
                    temp.extra['bool'] = True
                    temp.extra['int'] = True
                    temp.extra['string'] = True
                    temp.extra['float'] = True
                else:
                    temp.extra['int'] = True
                    temp.extra['float'] = True
                temp.typeList.append('bool')
            else :
                if p[2] in ["|",'^', '/', '%', '>>', '<<']:
                    temp.extra['opcode'] = p[2]
                    temp.extra['int'] = True
                    if p[2] == '/':
                        temp.extra['float'] = True
                else :
                    temp.extra['int'] = True
                    temp.extra['float'] = True
                    if p[2] == '+':
                        temp.extra['string'] = True
                    temp.extra['opcode'] = p[2]
            tp = self.getBaseType(p[1].typeList[0])
            # print(p[1].typeList,p[3].typeList)
            if not self.compareType(p[1].typeList[0], p[3].typeList[0]):
                self.compileErrors +=1
                print_error('Type should be same across binary operator',*(self.pos(p.lexpos(2))))
            elif tp[0] not in temp.extra:
                self.compileErrors +=1
                print_error('Invalid type for binary expression',*(self.pos(p.lexpos(2))))
            else:
                if len(temp.typeList) > 0:
                    # for boolean
                    p[0].typeList = temp.typeList
                else:
                    p[0].typeList = p[1].typeList
                newVar = self.newVar(p[0].typeList[0])
                p[0].code = p[1].code
                p[0].scopeInfo = p[1].scopeInfo
                p[0].code += p[3].code
                p[0].scopeInfo += p[3].scopeInfo
                # len(temp.extra)==2 for OR_OR and AND_AND <,<=,>,>= 
                # len(temp.extra)==1 for ^ | << >> MODULO
                # 3 for +, - ,*,&,/
                # len(temp.extra)==4 for == and !=
                # print(temp.extra)
                if len(temp.extra) < 3:
                    p[0].code.append([temp.extra['opcode'], newVar, p[1].placeList[0], p[3].placeList[0]])
                    p[0].scopeInfo.append(['', self.getScope(), self.findScope(p[1].placeList[0]), self.findScope(p[3].placeList[0])])
                else:
                    baseType = self.getBaseType(p[1].typeList[0])
                    p[0].code.append([temp.extra['opcode'] + baseType[0], newVar, p[1].placeList[0], p[3].placeList[0]])
                    p[0].scopeInfo.append(['', self.getScope(), self.findScope(p[1].placeList[0]), self.findScope(p[3].placeList[0])])
                p[0].placeList.append(newVar)
                p[0].extra['scope'] = self.getScope() #this is extra information is useful in if else

    def p_UnaryExpr(self, p):
        '''
        UnaryExpr  	: PrimaryExpr 
                    | PLUS UnaryExpr
                    | MINUS UnaryExpr
                    | STAR UnaryExpr
                    | AMP UnaryExpr
                    | NOT UnaryExpr
        '''
        p[0] = Node('UnaryExpr')
        p[0].extra['deref'] = ['no']
        if len(p) == 2:
            # if isinstance(p[1],str):
            # print(p[1].typeList)
            p[0].typeList = p[1].typeList
            p[0].placeList = p[1].placeList
            p[0].code = p[1].code
            p[0].scopeInfo = p[1].scopeInfo
            # print(p[0].typeList)

        elif p[1] == '!':
            tp = self.getBaseType(p[2].typeList[0])
            if tp != ['bool']:
                self.compileErrors +=1
                print_error('Type should be boolean with !',*(self.pos(p.lexpos(2))))
            else:
                p[0].typeList = p[2].typeList
                p[0].placeList = p[2].placeList
                p[0].code = p[2].code
                # first add code for the unary expr
                p[0].scopeInfo = p[2].scopeInfo
                newVar = self.newVar(p[0].typeList[0])
                # then add code for the not of this unary expr
                p[0].code.append(['!', newVar, p[2].placeList[0]])
                p[0].scopeInfo.append(['', self.getScope(), self.findScope(p[2].placeList[0])])
        
        else:
            temp = Node("temp")
            temp.extra['int'] = True
            temp.extra['float'] = True
            if p[1] == '+':
                temp.extra['string'] = True
            temp.extra['opcode'] = p[1]
            update = True
            ck = False
            if temp.extra['opcode'] == '*':
                ck = True
                rawType = self.getBaseType(p[2].typeList[0])
                if rawType[0] != 'pointer':
                    self.compileErrors +=1
                    print_error('Expected pointer type',*(self.pos(p.lexpos(1))))
                else:
                    # TODO:
                    newType = self.addType(rawType[1])
                    p[0].typeList = [newType]
                    update = False
            if temp.extra['opcode'] == '&':
                ck = True
                rawType = self.getBaseType(p[2].typeList[0])
                newType = self.addType(['pointer', rawType])
                p[0].typeList = [newType]
                update = False
            rawType = self.getBaseType(p[2].typeList[0])
            if rawType[0] not in temp.extra and not ck:
                self.compileErrors +=1
                print_error('Invalid type for unary expression',*(self.pos(p.lexpos(1))))
            else:
                # only do this id
                if update:
                    p[0].typeList = p[2].typeList
                    p[0].extra['deref'] = ['no']
                else:
                    p[0].extra['deref'] = [temp.extra['opcode'] + p[2].placeList[0]]
                newVar = self.newVar(p[0].typeList[0])
                p[0].placeList = [newVar]
                p[0].identList = [newVar]
                p[0].code = p[2].code
                p[0].scopeInfo = p[2].scopeInfo
                # codes can be of the form [*pointer,t1,t2] or [+int,t1,t2] ...
                p[0].code.append([temp.extra['opcode'] + self.getBaseType(p[2].typeList[0])[0], newVar, p[2].placeList[0]])
                p[0].scopeInfo.append(['',self.getScope(),self.findScope(p[2].placeList[0])])

    def p_Statement(self, p):
        '''
        Statement 	: Declaration 
                    | LabeledStmt  
                    | ReturnStmt 
                    | JumpStmt 
                    | GotoStmt
                    | CreateScope Block EndScope 
                    | IfStmt 
                    | ForStmt
                    | SimpleStmt
                    | PrintStmt
                    | ScanStmt
        '''
        if len(p)==2:
            p[0] = p[1]
            # if(isinstance(p[1],str)):
            #     print(p[1])
        else :
            p[0] = p[2]
            # print(p[2].name)
        p[0].name = "Statement"
    
    def p_PrintStmt(self,p):
        "PrintStmt : PRINT ExpressionList"
        p[0] = p[2]
        p[0].name = 'PrintStmt'
        for idx, var in enumerate(p[2].placeList):
            if str(self.getBaseType(p[2].typeList[idx])[0]) not in ["int","float"]:
                self.compileErrors +=1
                print_error('Type not supported for printing',*(self.pos(p.lexpos(1))))
            p[0].code.append(['print_' + str(self.getBaseType(p[2].typeList[idx])[0]), var])
            p[0].scopeInfo.append(['', self.findScope(var)])
    
    def p_ScanStmt(self,p):
        "ScanStmt : SCAN ExpressionList"
        p[0] = p[2]
        p[0].name = 'ScanStmt'
        for idx, var in enumerate(p[2].placeList):
            if str(self.getBaseType(p[2].typeList[idx])[0]) not in ["int"]:
                self.compileErrors +=1
                print_error('Type not supported for scanning',*(self.pos(p.lexpos(1))))
            p[0].code.append(['scan_' + str(self.getBaseType(p[2].typeList[idx])[0]), var])
            p[0].scopeInfo.append(['', self.findScope(var)])

    def p_SimpleStmt(self, p):
        '''
        SimpleStmt	: ExpressionStmt
                    | IncDecStmt 
                    | Assignment 
                    | ShortVarDecl
        '''
        p[0] = p[1]
        # print(p[1].name)
        p[0].name = "SimpleStmt"
        
    def p_ExpressionStmt(self, p):
        '''
   
        ExpressionStmt 	: Expression
        '''
        p[0] = p[1]
        p[0].name = "ExpressionStmt"

    # TODO:
    def p_LabeledStmt(self, p):
        '''         
        LabeledStmt	: Label COLON Statement
        '''
        if p[1] in self.checkId(p[1],"default"):
            msg = "Redeclaring identfier as label"
            self.compileErrors +=1
            print_error(msg, *(self.pos(p.lexpos(1))))
        else :
            newVar = self.newVar(p[1].typelist[0])
            self.symbolTables[self.getScope()].add(newVar,p[1].typelist[0])
            p[0] = p[3]

    def p_Label(self, p):
        '''
        Label   : ID
        '''
        p[0] = p[1]
    
    def p_IncDecStmt(self, p):
        '''
        IncDecStmt 	: Expression PLUS_PLUS
                    | Expression MINUS_MINUS
                    | PLUS_PLUS Expression
                    | MINUS_MINUS Expression
        '''
        if p[1] == '++' or p[1] == '--' :
            msg = "Prefix increment not allowed in go"
            self.compileErrors +=1
            print_error(msg, *(self.pos(p.lexpos(1))))
            return
        p[0]=p[1]
        p[0].name = "IncDecStmt"
        rawType = self.getBaseType(p[1].typeList[0])
        if  rawType[0] != 'int':
            err_ = str(p[1].typeList[0]) + 'cannot be incremented or decremented'
            self.compileErrors +=1
            print_error( err_,*(self.pos(p.lexpos(1))))
        p[0].code.append([p[2], p[1].placeList[0], p[1].placeList[0]])
        p[0].scopeInfo.append(['', self.findScope(p[1].placeList[0]), self.findScope(p[1].placeList[0])])
    
    def p_Assignment(self, p):
        '''
        Assignment	: ExpressionList PLUS_EQ ExpressionList
                    | ExpressionList MINUS_EQ ExpressionList
                    | ExpressionList STAR_EQ ExpressionList
                    | ExpressionList DIVIDE_EQ ExpressionList
                    | ExpressionList MODULO_EQ ExpressionList
                    | ExpressionList AMP_EQ ExpressionList
                    | ExpressionList OR_EQ ExpressionList
                    | ExpressionList CARET_EQ ExpressionList
                    | ExpressionList EQ ExpressionList
        '''
        p[0]=p[1]
        temp = Node("temp")
        temp.extra['opcode'] = p[2]
        if p[1] != "=" :
            temp.extra['int'] = True
        else :
            temp.extra['int'] = True
            temp.extra['bool'] = True
            temp.extra['float'] = True
            temp.extra['string'] = True
        if len(p[1].typeList) != len(p[3].typeList):
            err_ = str(len(p[1].typeList)) + ' identifier but ' + str(len(p[3].placeList)) + ' expressions'
            self.compileErrors +=1
            print_error(err_,*(self.pos(p.lexpos(2))))
        else:
            for idx in range(len(p[3].typeList)):
                rawTp1 = self.getBaseType(p[1].typeList[idx])
                rawTp2 = self.getBaseType(p[3].typeList[idx])
                if not self.compareType(rawTp1, rawTp2):
                    err_ = str(rawTp1) + ' assigned to ' + str(rawTp2)
                    self.compileErrors +=1
                    print_error(err_,*(self.pos(p.lexpos(2))))
                info = self.findInfo(p[1].placeList[idx])  
                if info is None:
                    info = []
                if 'is_const' in info:
                    self.compileErrors +=1
                    print_error('Constant cannot be reassigned',*(self.pos(p.lexpos(2))))
                if  rawTp1[0] not in temp.extra and temp.extra['opcode'] != '=':
                    self.compileErrors +=1
                    # print(rawTp1)
                    # print(p[2].extra)
                    print_error('Invalid Type for operator %s'%p[2].extra['opcode'],*(self.pos(p.lexpos(2))))
        p[0].name = "Assignment"
        p[0].code += p[3].code
        p[0].scopeInfo += p[3].scopeInfo
        for idx_ in range(len(p[3].typeList)):
            # if it's not pointer type we are adding only opcode info in the code
            if p[1].extra['deref'][idx_] == 'no':
                p[0].code.append([temp.extra['opcode'], p[1].placeList[idx_], p[3].placeList[idx_]])
            # here we are also adding the opcode and the pointer info coming from p[1].extra['deref']
            # p[1].extra['deref'] contains values in the form *t where t is a placeholder
            else:
                p[0].code.append([temp.extra['opcode'], p[1].extra['deref'][idx_], p[3].placeList[idx_]])
            p[0].scopeInfo.append(['', self.findScope(p[1].placeList[idx_]), self.findScope(p[3].placeList[idx_])])
    
    # the labels are placed in such a way that for each case after body of loop ends it go to update then to condition then to body again or out of loop
    def p_ForStmt(self, p):
        '''
        ForStmt : FOR CreateScope Condition Block EndScope
                | FOR CreateScope ForLoop Block EndScope
        '''
        start = self.symbolTables[self.lastScope].metadata['start']
        update = self.symbolTables[self.lastScope].metadata['update']
        end = self.symbolTables[self.lastScope].metadata['end']  
        condition = self.symbolTables[self.lastScope].metadata['condition']  
        
        p[0]=p[3]
        if p[3].name == "Condition":
            p[0].code.insert(0, [condition])
            p[0].scopeInfo.insert(0, [''])
        p[0].code += [[start]]
        p[0].scopeInfo.append([''])
        p[0].code += p[4].code
        p[0].scopeInfo += p[4].scopeInfo
        if p[3].name == "Condition":
            p[0].code += [['goto', condition]]
        else :
            p[0].code += [['goto', update]]
        p[0].scopeInfo.append(['', ''])
        p[0].code += [[end]]
        p[0].scopeInfo.append([''])
        p[0].name = 'ForStmt'

    def p_Condition(self,p):
        '''
        Condition : Expression
        '''
        p[0] = p[1]
        end = self.symbolTables[self.getScope()].metadata['end']
        p[0].code.append(['if', p[1].placeList[0],'False', end])
        p[0].scopeInfo.append(['', self.findScope(p[1].placeList[0]), '', ''])
        rawType = self.getBaseType(p[1].typeList[0])
        if rawType[0] != 'bool':
            print_error('Expression type should be bool',*(self.pos(p.lexpos(1))))
        p[0].name = 'Condition'


    def p_ForLoop(self, p):
        '''
        ForLoop	: InitStmtOpt SEMICOLON ConditionOpt SEMICOLON UpdateOpt
        '''
        p[0] = p[1]
        condition = self.symbolTables[self.getScope()].metadata['condition']
        update = self.symbolTables[self.getScope()].metadata['update']
        start = self.symbolTables[self.getScope()].metadata['start']
        # this how the code for this for loop will look like
        # [condition]
        # [code for conditionopt] and this might contain code like 'goto end' if condition is not satisfied
        # ['goto' start] we are going to body of the for loop if condition is satisfied
        # [update] since body of the for loop contains 'goto update' it will come to this label after the body of loop is done
        # [code for Updateopt] 
        # ['goto condition'] after updating is done we go to condition
        # and this goes on till the condition is false
        p[0].code += [[condition]]
        p[0].scopeInfo.append([''])
        p[0].code += p[3].code
        p[0].scopeInfo += p[3].scopeInfo
        p[0].code += [['goto', start]]
        p[0].scopeInfo.append(['', ''])
        p[0].code += [[update]]
        p[0].scopeInfo.append([''])
        p[0].code += p[5].code
        p[0].scopeInfo += p[5].scopeInfo
        p[0].code += [['goto', condition]]
        p[0].scopeInfo.append(['',''])
        p[0].name = 'ForLoop'

        p[0].extra = p[3].extra
    
    # def p_WhileLoop(self, p):
    #     '''
    #     WhileLoop	: FOR ConditionOpt
    #     '''
    #     node = Node(name = 'while', kind = 'Stmt')
    #     node.childList += [p[2]]
    #     p[0] = node
    
    def p_InitStmt(self, p):
        '''
        InitStmtOpt	: SimpleStmt
                    |
        '''
        if len(p)==2:
            p[0]=p[1]
            p[0].name = "InitStmt"
        else :
            p[0]=Node("InitStmtOpt")
    
    def p_UdpateOpt(self, p):
        '''
        UpdateOpt	: SimpleStmt
                    |
        '''
        if len(p)==2:
            p[0]=p[1]
            p[0].name = "UdpateOpt"
        else :
            p[0]=Node("UpdateOpt")
    
    def p_ConditionOpt(self, p):
        '''
        ConditionOpt 	: Condition
                        |
        '''
        if len(p) == 2 :
            p[0] = p[1]
            p[0].name = "ConditionOpt"
        else :
            p[0] = Node("ConditionOpt")

    def p_ReturnStmt(self, p):
        '''
        ReturnStmt	: RETURN Expression
                    | RETURN 
        '''
        p[0] = Node("ReturnStmt")
        scope_ = self.getNearest('func')
        if scope_ == -1:
            print_error('return should be in a function',)
            return
        if len(p)==2:
            if len(typeList) != 0:
                error_ = 'Expected  '+str(len(typeList)) + ' arguments got 0' 
                print_error(f'Type Mismatch {error_}',*(self.pos(p.lexpos(1))))
                self.compileErrors +=1
            p[0].code = [['return']]
            p[0].scopeInfo =  [['']]
        else :
            typeList = self.symbolTables[scope_].metadata['retvaltype']
            if len(typeList) != len(p[2].typeList):
                error_ = 'Expected ' + str(len(typeList)) + ' arguments got ' + str(len(p[2].typeList))
                print_error(f'Type Mismatch {error_}',*(self.pos(p.lexpos(1))))
                self.compileErrors +=1
            elif not self.compareType(p[2].typeList[0], typeList[0]):
                print_error('return type does not match',*(self.pos(p.lexpos(1))))
                self.compileErrors +=1
            self.symbolTables[scope_].metadata['retval'] = p[2].placeList[0]
            p[0].code = p[2].code + [['return', p[2].placeList[0]]]
            p[0].scopeInfo = p[2].scopeInfo + [['', self.findScope(p[2].placeList[0])]]

    def p_JumpStmt(self, p):
        '''
        JumpStmt	: BREAK 
                    | CONTINUE
        '''
        p[0] = Node('JumpStmt')
        scope_ = self.getNearest('for')
        if scope_ == -1:
            self.compileErrors +=1
            print_error(f'{p[1]} is not in a loop',*(self.pos(p.lexpos(1))))
            return
        symTab = self.symbolTables[scope_]
        if(p[1]=="break"):
            p[0].code = [['break_goto', symTab.metadata['end']]]
        else :
            p[0].code = [['continue_goto', symTab.metadata['update']]]
        p[0].scopeInfo = [['', '']]
    
    # TODO
    def p_GotoStmt(self, p):
        '''
        GotoStmt	: GOTO Label 
        '''
        p[0] = Node(name='goto', kind = 'Stmt')
        # save scopestack and node to which label points
        # we will check for errors after parsing
        

    # labels are placed such that if condition is true it will go inside the if block or the corresponding else block if it's not empty
    def p_IfStmt(self, p):
        '''
        IfStmt 	: IF CreateScope Expression Block ElseOpt EndScope
        '''
        p[0] = p[3]
        # print(p[3].name)
        rawType = self.getBaseType(p[3].typeList[0])
        if rawType[0] != 'bool':
            self.compileErrors +=1
            print_error('Non-bool expression (%s) used as if condition'%p[3].typeList[0],*(self.pos(p.lexpos(3))))
        
        newLabel1 = self.newLabel()
        p[0].code.append(['if',p[3].placeList[0],'False',newLabel1])
        # Use extra information to get scope of expr because Last scope has been popped
        p[0].scopeInfo.append(['', p[3].extra['scope'], '', ''])
        p[0].code += p[4].code
        p[0].scopeInfo += p[4].scopeInfo
        newLabel2 = self.newLabel()
        p[0].code.append(['goto', newLabel2])
        p[0].scopeInfo.append(['',''])
        p[0].code.append([f"{newLabel1}:"])
        p[0].scopeInfo.append([''])
        p[0].code += p[5].code
        p[0].scopeInfo += p[5].scopeInfo
        p[0].code.append([f"{newLabel2}:"])
        p[0].scopeInfo.append([''])

    def p_ElseOpt(self, p):
        '''
        ElseOpt	: ELSE CreateScope IfStmt EndScope
                | ELSE CreateScope Block EndScope
                | 
        '''
        if len(p)==5:
            p[0]=p[3]
        else :
            p[0]=Node("ElseOpt")
            p[0].extra["isEmpty"] = True
        p[0].name = "ElseOpt"
        

    def p_SourceFile(self, p):
        '''
        SourceFile	: PackageClause ImportDeclList TopLevelDeclList
                    | PackageClause ImportDeclList
                    | PackageClause TopLevelDeclList
                    | PackageClause
        '''
        if len(p)==4:
            p[0] = p[4]
            p[0].name = "SourceFile"
        elif len(p)==3 and p[2].name=="TopLevelDeclList":
            p[0]=p[2]
            p[0].name = "SourceFile"
        else :
            p[0]=Node("SourceFile")
        global rootNode
        rootNode.code += p[0].code
        rootNode.scopeInfo += p[0].scopeInfo

    def p_PackageClause(self, p):
        '''
        PackageClause   : PACKAGE ID SEMICOLON
        '''
        p[0]=Node("PackageClause")
        p[0].identList.append(p[1])

    def p_ImportDeclList(self, p):
        '''
        ImportDeclList	: ImportDeclList ImportDecl SEMICOLON
                        | ImportDecl SEMICOLON
        '''
        p[0] = Node("ImportDeclList")

    def p_ImportDecl(self, p):
        '''
        ImportDecl 	: IMPORT ImportPath
        '''
        p[0] = Node("ImportDecl")
    
    def p_ImportPath(self, p):
        '''
        ImportPath	: STRING_LIT
        '''
        p[0] = Node("ImportPath")

    def p_TopLevelDeclList(self, p):
        '''
        TopLevelDeclList	: TopLevelDeclList TopLevelDecl SEMICOLON
                            | TopLevelDecl SEMICOLON
        '''
        p[0]=p[1]
        p[0].name = "TopLevelDeclList"
        if len(p)==4 :
            p[0].code += p[2].code
            p[0].scopeInfo += p[2].scopeInfo

from codeGen import CodeGenerator

if __name__ == "__main__" :
    try :
        file = open(sys.argv[1], 'r')
    except :
        print(f"File {sys.argv[1]} not found")
        exit(0)
    data = file.read()
    parser = ParserGo(data, sys.argv[1])
    parser.build()
    result = parser.parser.parse(data, lexer=parser.lexer.lexer, tracking=True)
    if parser.compileErrors > 0:
        sys.exit()
    # print("===== 3AC ====")
    # for idx in range(len(rootNode.code)):
    #     print("-------------------------")
    #     print(rootNode.code[idx])
    #     print(rootNode.scopeInfo[idx])
    codeGen = CodeGenerator(rootNode,parser)

    outfile = open('assembly.asm', 'w')
    x86Code = codeGen.getCode()

    for code_ in x86Code:
        if code_.split(' ')[0] in ['global', 'section', 'extern']:
            outfile.write(code_ + '\n')
        elif code_[-1:] == ':' and 'main' in code_:
            outfile.write('main:\n')
        elif code_[-1:] == ':':
            outfile.write(code_ + '\n')
        else:
            outfile.write('    '+code_+'\n')
    outfile.close()
