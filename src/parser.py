import sys
from lexer import LexerGo
from lexer import tokens
import ply.yacc as yacc
from helper import print_error, print_warn
from collections import OrderedDict
from data_structures import Scope, Node
# import logging
# log = logging.getLogger('ply')

class ParserGo:

    def __init__(self, data):
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
        self.curScope = Scope(isGlobal=True)    # contains current scope
        self.scopeList = [self.curScope]        # contains list of all scopes
        self.scopePtr = 1                       # next index of scope to insert
        self.scopeStack = [0]                   # contains all active scopes
        
    
    def popScope(self):
        self.scopeStack.pop()
        self.curScope = self.scopeList[self.scopeStack[-1]]

    def pushScope(self):
        self.scopeStack.append(self.scopePtr)
        self.curScope = Scope()
        self.scopeList.append(self.curScope)
        self.scopePtr += 1

    def pos(self, lexpos):
        return (self.lexer.tokenList[lexpos][2], self.lexer.tokenList[lexpos][3])

    def build(self):
        self.parser = yacc.yacc(module=self, start='SourceFile', method='LALR', debug=False)

    def p_error(self, p):
        if p is not  None :
            msg = f"Found unexpexted token {p.value}"
            print_error(msg, self.lexer.tokenList[p.lexpos][2], self.lexer.tokenList[p.lexpos][3])

    def p_lcurly(self, p):
        '''
        lcurly  : LCURLY
        '''
    
    def p_rcurly(self, p):
        '''
        rcurly  : RCURLY
        '''

    def p_Type(self, p):
        '''
        Type    : TypeName
                | TypeLit
        '''
        p[0] = p[1]

    def p_TypeName(self, p):
        '''
        TypeName	: ID
                    | DATA_TYPE
        '''
        p[0] = p[1]

    def p_TypeLit(self, p):
        '''
        TypeLit	: ArrayType 
                | StructType 
                | PointerType 
                | SliceType
        '''
        p[0] = p[1]
        
    def p_ArrayType(self, p):
        '''
        ArrayType : LSQUARE ArrayLength RSQUARE ElementType
        '''
        p[0] = ['ARR', p[2], p[4]]

    def p_ArrayLength(self, p):
        '''
        ArrayLength : Expression
        '''
    
    def p_SliceType(self, p):
        '''
        SliceType 	: LSQUARE RSQUARE ElementType
        '''
        p[0] = ['SLC', p[3]]
    
    def p_ElementType(self, p):
        '''
        ElementType : Type
        '''
        p[0] = p[1]
    
    def p_PointerType(self, p):
        '''
        PointerType	: STAR BaseType
        '''
        p[0] = ['PTR', p[1]]

    def p_BaseType(self, p):
        '''
        BaseType	: Type
        '''
        p[0] = p[1]
    
    def p_StructType(self, p):
        '''
        StructType 	: STRUCT lcurly FieldDeclList rcurly
        '''
        dict = OrderedDict()
        for (id, type) in zip(p[3][0], p[3][1]):
            if id in dict.keys() :
                msg = "Field of struct redeclared"
                print_error(msg, 0, 0)
            else :
                dict[id] = type
        p[0] = ['STRUCT', dict]

    def p_FieldDeclList(self, p):
        '''
        FieldDeclList 	: FieldDeclList FieldDecl SEMICOLON 
                        | FieldDecl SEMICOLON
        '''
        if len(p) == 3:
            p[0] = [p[1][0], p[1][1]]
        else :
            p[1][0] += p[2][0]
            p[1][1] += p[2][1]
            p[0] = [p[1][0], p[1][1]]
        
    def p_FieldDecl(self, p):
        '''
        FieldDecl 	: IdentifierList Type
        '''
        p[0] = [p[1], [p[2] for i in p[1]]]
    
    def p_Block(self, p):
        '''
        Block	: lcurly pushBlock StatementList popBlock rcurly
                | lcurly rcurly
        '''
        p[0] = ['BLOCK',p[3]]
    
    def p_pushBlock(self, p):
        '''
        pushBlock   : 
        '''
        self.pushScope()

    def p_popBlock(self, p):
        '''
        popBlock   : 
        '''
        print(self.curScope.symbolTable)
        self.popScope()
    
    def p_StatementList(self, p):
        '''
        StatementList 	: StatementList Statement
                        | Statement
        '''
        if(len(p)==2):
            p[0] = [p[1]]
        if(len(p)==3):
            p[1].append(p[2])
            p[0] = p[1]


    def p_Declaration(self, p):
        '''
        Declaration	: ConstDecl 
                    | TypeDecl 
                    | VarDecl 
        '''
    
    def p_TopLevelDecl(self, p):
        '''
        TopLevelDecl	: Declaration 
                        | FunctionDecl 
                        | MethodDecl
        '''

    def p_ConstDecl(self, p):
        '''
        ConstDecl	: CONST ConstSpec SEMICOLON
        '''
        p[0] = Node(name='ConstDecl', kind='Stmt')
        if len(p[2]['idList']) != len(p[2]['expList']) :
            msg = "Unequal number of identifiers and expressions"
            print_error(msg, *(self.pos(p.lexpos(1))))
        else :
            for id, exp in zip(p[2]['idList'], p[2]['expList']):
                if self.curScope.lookUp(id) :
                    msg = "Redeclaring variable"
                    print_error(msg, *(self.pos(p.lexpos(1))))
                else :
                    # if type is untyped infer type from expression
                    type = p[2]['type']
                    eq = Node(name = '=', kind = 'EXP', type = type)
                    var = Node(name = id, kind = 'VAR', type = type)
                    eq.childList += [var, exp]
                    p[0].childList.append(eq)
                    self.curScope.addSymbol(name = id, type = type, node = var)
        print(p[0].childList)

    def p_ConstSpec(self, p):
        '''
        ConstSpec   :	IdentifierList EQ ExpressionList
                    |   IdentifierList Type EQ ExpressionList
        '''
        if len(p) == 4 :
            p[0] = {'idList' : p[1], 'expList' : p[3],  'type' : 'untyped'}
        else :
            p[0] = {'idList' : p[1], 'expList' : p[4],  'type' : p[2]}

    def p_IdentifierList(self, p):
        '''
        IdentifierList	: IdentifierList COMMA ID
                        | ID
        '''
        if len(p) == 2 :
            p[0] = [p[1]]
        else :
            p[1].append(p[3])
            p[0] = p[1]

    def p_ExpressionList(self, p):
        '''
        ExpressionList	: ExpressionList COMMA Expression
                        | Expression
        '''
        if len(p) == 2 :
            p[0] = [p[1]]
        else :
            p[1].append(p[3])
            p[0] = p[1]
        
    
    def p_TypeDecl(self, p):
        '''
        TypeDecl	: TYPE ID Type SEMICOLON
        '''

    def p_VarDecl(self, p):
        '''
        VarDecl	: VAR VarSpec SEMICOLON
        '''

        p[0] = Node(name = 'VarDecl', kind = 'Stmt')
        
        if p[2]['initialized'] :
            if len(p[2]['idList']) != len(p[2]['expList']) :
                msg = "Unequal number of identifiers and expressions"
                print_error(msg, *(self.pos(p.lexpos(1))))
            else :
                for id, exp in zip(p[2]['idList'], p[2]['expList']):
                    if self.curScope.lookUp(id) :
                        msg = "Redeclaring variable"
                        print_error(msg, *(self.pos(p.lexpos(1))))
                    else :
                        # initializing to exp
                        type = p[2]['type']
                        eq = Node(name = '=', kind = 'EXP', type = type)
                        var = Node(name = id, kind = 'VAR', type = type)
                        eq.childList += [var, exp]
                        self.curScope.addSymbol(name = id, type = type, node = var)
                        p[0].childList.append(eq)
        else :
            # initialize to default value 
            # infer from type
            for id in p[2]['idList'] :
                if self.scopeList[self.scopeStack[-1]].lookUp(id) :
                    msg = "Redeclaring variable"
                    print_error(msg, *(self.pos(p.lexpos(1))))
                else :
                    type = p[2]['type']
                    eq = Node(name = '=', kind = 'EXP', type = type)
                    var = Node(name = id, kind = 'VAR', type = type)
                    exp = Node(name = 'default', kind = 'EXP', type = type)
                    eq.childList += [var, exp]
                    self.curScope.addSymbol(name = id, type = type, node = var)
                    p[0].childList.append(eq)

        print(p[0].childList)
    
    def p_VarSpec(self, p):
        '''
        VarSpec	: IdentifierList Type 
                | IdentifierList Type EQ ExpressionList
        '''
        if len(p) == 3 :
            p[0] = {'idList' : p[1], 'expList' : [],  'type' : p[2], 'initialized' : False}
        else :
            p[0] = {'idList' : p[1], 'expList' : p[4],  'type' : p[2], 'initialized' : True}
    
    def p_ShortVarDecl(self, p):
        '''
        ShortVarDecl : IdentifierList ASSIGN ExpressionList
        '''
        p[0] = Node(name = 'VarDecl', kind = 'Stmt')
        if len(p[1]) != len(p[3]) :
            msg = "Unequal number of identifiers and expressions"
            print_error(msg, *(self.pos(p.lexpos(1))))
        else :
            for id, exp in zip(p[1], p[3]) :
                if self.curScope.lookUp(id) :
                    msg = "Redeclaring variable"
                    print_error(msg, *(self.pos(p.lexpos(1))))
                else :
                    # type should be infered from expression
                    type = None
                    eq = Node(name = '=', kind = 'EXP', type = type)
                    var = Node(name = id, kind = 'VAR', type = type)
                    eq.childList += [var, exp]
                    self.curScope.addSymbol(name = id, type = type, node = var)
                    p[0].childList.append(eq)
        print(p[0].childList)            

    
    def p_FunctionDecl(self, p):
        '''
        FunctionDecl 	: FUNC FunctionName Signature FunctionBody
                        | FUNC FunctionName Signature SEMICOLON
        '''
        print(p.lexpos(2))
    
    def p_FunctionName(self, p):
        '''
        FunctionName	: ID
        '''
    
    def p_Signature(self, p):
        '''
        Signature      	: Parameters
                        | Parameters Result
        '''
    
    def p_Parameters(self, p):
        '''
        Parameters 	: LROUND ParameterList RROUND
                    | LROUND RROUND
        '''
    
    def p_ParameterList(self, p):
        '''
        ParameterList	: ParameterList COMMA ParameterDecl 
                        | ParameterDecl
        '''
    
    def p_ParameterDecl(self, p):
        '''
        ParameterDecl	: IdentifierList Type
        '''
    
    def p_Result(self, p):
        '''
        Result 	: Type
        '''

    def p_FunctionBody(self, p):
        '''
        FunctionBody	: Block
        '''
    
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
        if len(p) == 2 :
            p[0] = p[1]
        else :
            p[0] = p[2]

    def p_Literal(self, p):
        '''
        Literal	: BasicLit 
                | CompositeLit
        '''
        p[0] = p[1]
    
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
        print(self.pos(p.lexpos(1)))

    def p_IntLit(self, p):
        '''
        IntLit  : INT_LIT
        '''
        p[0] = Node(name='Lit', kind = 'EXP', type = 'int', value = int(p[1]))

    def p_FloatLit(self, p):
        '''
        FloatLit    : FLOAT_LIT
        '''
        p[0] = Node(name='Lit', kind = 'EXP', type = 'float', value = float(p[1]))

    def p_StrLit(self, p):
        '''
        StrLit  : STRING_LIT
        '''
        p[0] = Node(name='Lit', kind = 'EXP', type = 'string', value = p[1])
    
    def p_CharLit(self, p):
        '''
        CharLit : CHAR_LIT
        '''
        p[0] = Node(name='Lit', kind = 'EXP', type = 'char', value = ord(p[1]))
    
    def p_BoolLit(self, p):
        '''
        BoolLit : BOOL_LIT
        '''
        value = True if p[1]=='true' else False
        p[0] = Node(name='Lit', kind = 'EXP', type = 'bool', value = value)

    def p_NilLit(self, p):
        '''
        NilLit  : NIL
        '''
        p[0] = Node(name = 'Lit', kind = 'EXP', type = 'PTR', value = 0)
    
    def p_OperandName(self, p):
        '''
        OperandName : ID 
        '''
        # try finding in stacked scopes
        for scopeid in self.scopeStack[::-1] :
            if self.scopeList[scopeid].lookUp(p[1]) :
                p[0] = self.scopeList[scopeid].symbolTable[p[1]]['node']
                return
        
        msg = f"Using variable before declaration {p[1]}"
        print_error(msg, *(self.pos(p.lexpos(1))))

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
        LiteralValue 	: lcurly rcurly
                        | lcurly ElementList rcurly
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
    
    def p_PrimaryExpr(self, p):
        '''
        PrimaryExpr	: Operand 
                    | PrimaryExpr Selector 
                    | PrimaryExpr Index 
                    | PrimaryExpr Arguments
                    | MakeExpr
        '''
    
    def p_MakeExpr(self, p):
        '''
        MakeExpr    : MAKE LROUND SliceType COMMA Expression COMMA Expression RROUND
                    | MAKE LROUND SliceType COMMA Expression RROUND

        '''

        # | Conversion 
    
    def p_Selector(self, p):
        '''
        Selector	: DOT ID
        '''
    
    # def p_Conversion(self, p):
    #     '''
    #     Conversion	: Type LROUND Expression RROUND
    #     '''
    
    def p_Index(self, p):
        '''
        Index	: LSQUARE Expression RSQUARE
        '''
    
    def p_Arguments(self, p):
        '''
        Arguments	: LROUND ExpressionList RROUND
                    | LROUND RROUND
        '''

    def p_Expression(self, p):
        '''
        Expression 	: UnaryExpr 
                    | Expression OR_OR Expression
                    | Expression AMP_AMP Expression
                    | Expression EQ_EQ Expression
                    | Expression NOT_EQ Expression
                    | Expression LT Expression
                    | Expression LE Expression
                    | Expression GT Expression
                    | Expression GE Expression
                    | Expression PLUS Expression
                    | Expression MINUS Expression
                    | Expression OR Expression
                    | Expression CARET Expression
                    | Expression STAR Expression
                    | Expression DIVIDE Expression
                    | Expression MODULO Expression
                    | Expression LSHIFT Expression
                    | Expression RSHIFT Expression
                    | Expression AMP Expression
        '''
        if len(p) == 2 :
            p[0] = p[1]
        else :
            op = Node(name = p[2], kind = 'EXP')
            op.childList += [p[1], p[3]]

    def p_UnaryExpr(self, p):
        '''
        UnaryExpr  	: PrimaryExpr 
                    | unary_op UnaryExpr
        '''
        if len(p) == 2 :
            p[0] = p[1]
        else :
            # infer type from expression
            op = Node(name = p[1], kind = 'EXP')
            op.childList.append(p[2])
        
    def p_unary_op(self, p):
        '''
        unary_op 	: PLUS
                    | MINUS
                    | NOT
                    | CARET 
                    | STAR
                    | AMP
        '''
        p[0] = p[1]
    
    def p_Statement(self, p):
        '''
        Statement 	: Declaration 
                    | LabeledStmt  
                    | ReturnStmt 
                    | BreakStmt 
                    | ContinueStmt 
                    | GotoStmt
                    | Block 
                    | IfStmt 
                    | ForStmt
                    | SimpleStmt SEMICOLON
                    | SEMICOLON
        '''
    
    def p_SimpleStmt(self, p):
        '''
        SimpleStmt	: ExpressionStmt
                    | IncDecStmt 
                    | Assignment 
                    | ShortVarDecl
        '''
        p[0] = p[1]
        
    def p_ExpressionStmt(self, p):
        '''
        ExpressionStmt 	: Expression
        '''
        p[0] = p[1]

    def p_LabeledStmt(self, p):
        '''         
        LabeledStmt	: Label COLON Statement
        '''

    def p_Label(self, p):
        '''
        Label   : ID
        '''
    
    def p_IncDecStmt(self, p):
        '''
        IncDecStmt 	: Expression PLUS_PLUS
                    | Expression MINUS_MINUS
                    | PLUS_PLUS Expression
                    | MINUS_MINUS Expression
        '''
        if p[1] == '++' or p[1] == '--' :
            msg = "Prefix increment not allowed in go"
            print_error(msg, *(self.pos(p.lexpos(1))))
            return
        op = Node(name = p[2], kind = 'EXP')
        op.childList.append(p[1])
    
    def p_Assignment(self, p):
        '''
        Assignment	: Expression assign_op Expression
        '''
        # reducing power of rule ExpresssionList assign_op ExpressionList
    
    def p_assign_op(self, p):
        '''
        assign_op	: PLUS_EQ
                    | MINUS_EQ
                    | STAR_EQ
                    | DIVIDE_EQ
                    | MODULO_EQ
                    | AMP_EQ
                    | OR_EQ
                    | CARET_EQ
                    | EQ
        '''
    
    def p_ForStmt(self, p):
        '''
        ForStmt : ForLoop Block
                | WhileLoop Block
        '''
    
    def p_ForLoop(self, p):
        '''
        ForLoop	: FOR InitStmt SEMICOLON Condition SEMICOLON PostStmt
                | FOR InitStmt SEMICOLON Condition SEMICOLON
                | FOR InitStmt SEMICOLON SEMICOLON PostStmt
                | FOR InitStmt SEMICOLON SEMICOLON
                | FOR SEMICOLON Condition SEMICOLON PostStmt
                | FOR SEMICOLON Condition SEMICOLON
                | FOR SEMICOLON SEMICOLON PostStmt
                | FOR SEMICOLON SEMICOLON 
        '''
    
    def p_WhileLoop(self, p):
        '''
        WhileLoop	: FOR Condition
                    | FOR
        '''
    
    def p_InitStmt(self, p):
        '''
        InitStmt	: SimpleStmt
        '''
    
    def p_PostStmt(self, p):
        '''
        PostStmt	: SimpleStmt
        '''
    
    def p_Condition(self, p):
        '''
        Condition 	: Expression
        '''
    
    def p_ReturnStmt(self, p):
        '''
        ReturnStmt	: RETURN SEMICOLON
                    | RETURN ExpressionList SEMICOLON
        '''
    
    def p_BreakStmt(self, p):
        '''
        BreakStmt	: BREAK SEMICOLON
                    | BREAK Label SEMICOLON
        '''
    
    def p_ContinueStmt(self, p):
        '''
        ContinueStmt 	: CONTINUE SEMICOLON
                        | CONTINUE Label SEMICOLON
        '''
    
    def p_GotoStmt(self, p):
        '''
        GotoStmt	: GOTO Label SEMICOLON
        '''
    
    def p_IfStmt(self, p):
        '''
        IfStmt 	: IF SimpleStmt SEMICOLON Expression Block
                | IF Expression Block
                | IF SimpleStmt SEMICOLON Expression Block ElseStmt
                | IF Expression Block ElseStmt
        '''
    def p_ElseStmt(self, p):
        '''
        ElseStmt	: ELSE IfStmt
                    | ELSE Block
        '''

    def p_SourceFile(self, p):
        '''
        SourceFile	: PackageClause ImportDeclList TopLevelDeclList
                    | PackageClause ImportDeclList
                    | PackageClause TopLevelDeclList
                    | PackageClause
        '''
    
    def p_PackageClause(self, p):
        '''
        PackageClause   : PACKAGE ID
        '''

    def p_ImportDeclList(self, p):
        '''
        ImportDeclList	: ImportDeclList ImportDecl SEMICOLON
                        | ImportDecl SEMICOLON
        '''

    def p_ImportDecl(self, p):
        '''
        ImportDecl 	: IMPORT ImportPath
        '''
    
    def p_ImportPath(self, p):
        '''
        ImportPath	: STRING_LIT
        '''
    
    def p_TopLevelDeclList(self, p):
        '''
        TopLevelDeclList	: TopLevelDeclList TopLevelDecl
                            | TopLevelDecl
        '''

if __name__ == "__main__" :
    file = open(sys.argv[1], 'r')
    data = file.read()
    parser = ParserGo(data)
    parser.build()
    result = parser.parser.parse(data, lexer=parser.lexer.lexer, tracking=True)
    print(result)