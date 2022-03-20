import sys
from lexer import LexerGo
from lexer import tokens
import ply.yacc as yacc
from helper import print_error, print_warn
# import logging
# log = logging.getLogger('ply')

class ParserGo:
    tokens = tokens
    precedence = (
        ('left', 'OR_OR'),
        ('left', 'AMP_AMP'),
        ('left', 'EQ_EQ', 'NOT_EQ', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'PLUS', 'MINUS', 'OR', 'CARET'),
        ('left', 'STAR', 'DIVIDE', 'MODULO', 'LSHIFT', 'RSHIFT', 'AMP')
    )

    def __init__(self, data):
        self.lexer = LexerGo()
        self.lexer.build()
        self.lexer.input(data)

    def build(self):
        self.parser = yacc.yacc(module=self, start='SourceFile', method='LALR', debug=True)

    def p_error(self, p):
        if p is not  None :
            msg = f"Unexpexted {p.value} found"

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

    def p_TypeName(self, p):
        '''
        TypeName	: ID
                    | DATA_TYPE
        '''

    def p_TypeLit(self, p):
        '''
        TypeLit	: ArrayType 
                | StructType 
                | PointerType 
                | SliceType
        '''
    def p_ArrayType(self, p):
        '''
        ArrayType : LSQUARE ArrayLength RSQUARE ElementType
        '''

    def p_ArrayLength(self, p):
        '''
        ArrayLength : Expression
        '''
    
    def p_SliceType(self, p):
        '''
        SliceType 	: LSQUARE RSQUARE ElementType
        '''
    
    def p_ElementType(self, p):
        '''
        ElementType : Type
        '''
    
    def p_PointerType(self, p):
        '''
        PointerType	: STAR BaseType
        '''
    
    def p_BaseType(self, p):
        '''
        BaseType	: Type
        '''
    
    def p_StructType(self, p):
        '''
        StructType 	: STRUCT lcurly FieldDeclList rcurly
        '''
    
    def p_FieldDeclList(self, p):
        '''
        FieldDeclList 	: FieldDeclList FieldDecl SEMICOLON 
                        | FieldDecl SEMICOLON
        '''
    
    def p_FieldDecl(self, p):
        '''
        FieldDecl 	: IdentifierList Type
        '''
    
    def p_Block(self, p):
        '''
        Block	: lcurly StatementList rcurly
                | lcurly rcurly
        '''
    
    def p_StatementList(self, p):
        '''
        StatementList 	: StatementList Statement
                        | Statement
        '''

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
        ConstDecl	:	CONST ConstSpec SEMICOLON
        '''

    def p_ConstSpec(self, p):
        '''
        ConstSpec   :	IdentifierList EQ ExpressionList
        '''

    def p_IdentifierList(self, p):
        '''
        IdentifierList	: IdentifierList COMMA ID
                        | ID
        '''

    def p_ExpressionList(self, p):
        '''
        ExpressionList	: ExpressionList COMMA Expression
                        | Expression
        '''
    
    def p_TypeDecl(self, p):
        '''
        TypeDecl	: TYPE ID Type SEMICOLON
        '''

    def p_VarDecl(self, p):
        '''
        VarDecl	: VAR VarSpec SEMICOLON
        '''
    
    def p_VarSpec(self, p):
        '''
        VarSpec	: IdentifierList Type 
                | IdentifierList Type EQ ExpressionList
        '''
    
    def p_ShortVarDecl(self, p):
        '''
        ShortVarDecl : IdentifierList ASSIGN ExpressionList
        '''
    
    def p_FunctionDecl(self, p):
        '''
        FunctionDecl 	: FUNC FunctionName Signature FunctionBody
                        | FUNC FunctionName Signature SEMICOLON
        '''
    
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

    def p_Literal(self, p):
        '''
        Literal	: BasicLit 
                | CompositeLit
        '''
    
    def p_BasicLit(self, p):
        '''
        BasicLit	: INT_LIT
                    | FLOAT_LIT
                    | STRING_LIT
                    | BOOL_LIT
                    | CHAR_LIT
                    | NIL
        '''
    
    def p_OperandName(self, p):
        '''
        OperandName : ID 
        '''

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
        #             
        # '''
        # Incase of ID check if typedef
    
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

    def p_UnaryExpr(self, p):
        '''
        UnaryExpr  	: PrimaryExpr 
                    | unary_op UnaryExpr
        '''
    
    # def p_binary_op(self, p):
    #     '''
    #     binary_op   :  
    #                 |  
    #                 |  
    #                 |
    #     '''
    
    def p_rel_op(self, p):
        '''
        rel_op	: EQ_EQ 
                | NOT_EQ 
                | LT 
                | LE 
                | GT 
                | GE
        '''

    def p_add_op(self, p):
        '''
        add_op	: PLUS 
                | MINUS
                | OR 
                | CARET
        '''
    
    def p_mul_op(self, p):
        '''
        mul_op	: STAR 
                | DIVIDE
                | MODULO
                | LSHIFT
                | RSHIFT
                | AMP
        '''
    
    def p_unary_op(self, p):
        '''
        unary_op 	: PLUS
                    | MINUS
                    | NOT
                    | CARET 
                    | STAR
                    | AMP
        '''
    
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
        
    def p_ExpressionStmt(self, p):
        '''
        ExpressionStmt 	: Expression
        '''

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
        '''
    
    def p_Assignment(self, p):
        '''
        Assignment	: ExpressionList assign_op ExpressionList
        '''
    
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
        WhileLoop	: FOR Condition Block
                    | FOR Block 
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
                | IF SimpleStmt SEMICOLON Expression ElseStmt
                | IF Expression ElseStmt
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