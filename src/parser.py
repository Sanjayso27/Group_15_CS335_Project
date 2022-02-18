import sys
from lexer import Lexer
from lexer import tokens_for_parser as tokens
import ply.yacc as yacc

class Parser:

    tokens = tokens    
    
    def __init__(self, data):
        lexer = Lexer()
        lexer.build()
        self.tokmap = lexer.get_map(data)

    def build(self):
        self.parser = yacc.yacc(module=self, start='start', method='LALR', debug=True)

    def p_error(self, p):
        if not p:
            print("End of File!")
            return
        # Read ahead looking for a closing '}'
        print(f"Found error at L : {self.tokmap[p.lexpos][0]}, C : {self.tokmap[p.lexpos][1]}")
        while True:
            tok = self.parser.token()             # Get the next token
            if not tok or tok.type == 'RBRACE':
                break
        self.parser.restart()

    # top level source file
    def p_start(self, p):
        '''start : pkg_stmt top_lvl_stmt_list
        '''
        p[0] = [p[1], p[2]]

    def p_pkg_stmt(self, p):
        '''pkg_stmt : PACKAGE IDENTIFIER'''
        p[0] = [p[1], p[2]]

    def p_top_lvl_stmt_list(self, p):
        '''top_lvl_stmt_list    : top_lvl_stmt
                                | top_lvl_stmt top_lvl_stmt_list   
        '''
        p[0] = [p[1]]
        if len(p)==3 :
            p[0] = p[0] + p[2]

    def p_top_lvl_stmt(self, p):
        '''top_lvl_stmt : imp_stmt
                        | struct_decl
                        | var_decl
                        | func_decl
                        | method_decl
        '''                
        p[0] = p[1]

    # IMPORT HANDLING #
    def p_imp_list(self, p):
        '''imp_list : STRING_LIT imp_list
                    | STRING_LIT
        '''
        p[0] = [p[1]]
        if len(p)==3 :
            p[0] = p[0] + p[2]

    def p_imp_stmt(self, p):
        '''imp_stmt : IMPORT STRING_LIT
                    | IMPORT LROUND imp_list RROUND
        '''
        p[0] = [p[1]]
        if len(p) == 5 :
            p[0] = p[0] + [p[3]]
        else :
            p[0] = p[0] + [p[2]]


    # TYPE HANDLING #
    def p_arr_type(self, p):
        '''arr_type : LSQUARE INT_LIT RSQUARE arr_type
                    | LSQUARE INT_LIT RSQUARE DATA_TYPE
        '''

    def p_slc_type(self, p):
        '''slc_type : LSQUARE RSQUARE slc_type
                    | LSQUARE RSQUARE DATA_TYPE
        '''

    def p_ptr_type(self, p):
        '''ptr_type : STAR ptr_type
                    | STAR DATA_TYPE
        '''

    def p_type(self, p):
        '''type : DATA_TYPE
                | arr_type
                | slc_type
                | ptr_type
        '''

    # VAR and CONST DECLARATIONS #
    def p_var_decl(self, p):
        '''var_decl : VAR IDENTIFIER type
                    | VAR IDENTIFIER type EQ expression
                    | VAR IDENTIFIER ASSIGN expression
                    | CONST IDENTIFIER type EQ expression
                    | CONST IDENTIFIER ASSIGN expression
        '''

    # STRUCT DECLARATIONS
    def p_struct_decl(self, p):
        '''struct_decl  : TYPE IDENTIFIER STRUCT LCURLY var_decl_list RCURLY
        '''
        p[0] = [p[1], p[2], p[3], p[5]]
    
    def p_var_decl_list(self, p):
        '''var_decl_list    : IDENTIFIER type var_decl_list
                            | IDENTIFIER type
        '''
        p[0] = [[p[1], p[2]]]
        if len(p) == 4 :
            p[0] = p[0] + p[3]

    # BLOCK         
    def p_block(self, p):
        '''block : LCURLY stmt_list RCURLY
        '''

    def p_stmt_list(self, p):
        '''stmt_list    : stmt stmt_list
                        | stmt
        '''

    def p_stmt(self, p):
        '''stmt : var_decl
                | return_stmt
                | block
                | selection_stmt
                | iteration_stmt
                | jump_stmt
                | label_stmt
                | expression_stmt
                | expression'''

    def p_return_stmt(self, p):
        '''return_stmt : RETURN argument_expression_list
        '''

    def p_expression_stmt(self, p):
        ''' expression_stmt : SEMICOLON
                            | expression SEMICOLON
        '''

    def p_selection_stmt(self, p):
        ''' selection_stmt  : IF expression  block
                            | IF expression  block ELSE block
                            | IF expression  block ELSE selection_stmt
        '''

    def p_iteration_stmt(self, p):
        ''' iteration_stmt  : FOR block
                            | FOR expression  block
                            | FOR expression_stmt expression_stmt expression  block
        '''

    def p_jump_stmt(self, p):
        '''jump_stmt    : CONTINUE
                        | BREAK
                        | GOTO IDENTIFIER
        '''

    def p_label_stmt(self, p):
        '''label_stmt   : IDENTIFIER COLON stmt
        '''

    # FUNCTIONS
    def p_func_decl(self, p):
        '''func_decl    : FUNC IDENTIFIER signature block
                        | FUNC IDENTIFIER signature'''

    def p_signature(self, p):
        '''signature    : params result
                        | params '''
    
    def p_params(self, p):
        '''params   : LROUND param_list RROUND
                    | LROUND RROUND'''

    def p_param_list(self, p):
        '''param_list   : type
                        | identifier_list type
                        | param_list COMMA identifier_list type 
        '''
    
    def p_identifier_list(self, p):
        '''identifier_list  : IDENTIFIER
                            | identifier_list COMMA IDENTIFIER'''
    
    def p_result(self, p):
        '''result : type'''     # TODO add typelist

    # METHOD
    def p_method(self, p):
        '''method_decl  : FUNC LROUND IDENTIFIER type RROUND IDENTIFIER signature
                        | FUNC LROUND IDENTIFIER type RROUND IDENTIFIER signature block
        '''

    def p_primary_expression(self, p):
        '''primary_expression   : IDENTIFIER
                                | lit_operand
                                | LROUND expression RROUND'''

    def p_postfix_expression(self, p):
        '''postfix_expression   : primary_expression
                                | postfix_expression LSQUARE expression RSQUARE
                                | postfix_expression LROUND RROUND
                                | postfix_expression LROUND argument_expression_list RROUND
                                | postfix_expression DOT IDENTIFIER 
                                | postfix_expression DOT IDENTIFIER LROUND RROUND
                                | postfix_expression DOT IDENTIFIER LROUND argument_expression_list RROUND
                                | postfix_expression PLUS_PLUS
                                | postfix_expression MINUS_MINUS'''                          

    def p_argument_expression_list(self, p):
        '''argument_expression_list : assignment_expression
                                    | argument_expression_list COMMA assignment_expression'''
	
    def p_unary_expression(self, p):
        '''unary_expression : postfix_expression
                            | PLUS_PLUS postfix_expression
                            | MINUS_MINUS postfix_expression
                            | unary_operator postfix_expression'''

    def p_unary_operator(self, p):
        '''unary_operator   : AMP
                            | STAR
                            | PLUS
                            | MINUS
                            | NOT'''

    def p_multiplicative_expression(self, p):
        '''multiplicative_expression    : unary_expression
                                        | multiplicative_expression STAR unary_expression
                                        | multiplicative_expression DIVIDE unary_expression
                                        | multiplicative_expression MODULO unary_expression'''

    def p_additive_expression(self, p):
        '''additive_expression  : multiplicative_expression
                                | additive_expression PLUS multiplicative_expression
                                | additive_expression MINUS multiplicative_expression'''

    def p_shift_expression(self, p):
        '''shift_expression : additive_expression
                            | shift_expression LSHIFT additive_expression
                            | shift_expression RSHIFT additive_expression'''

    def p_relational_expression(self, p):
        '''relational_expression    : shift_expression
                                    | relational_expression LT shift_expression
                                    | relational_expression GT shift_expression
                                    | relational_expression LT_EQ shift_expression
                                    | relational_expression GT_EQ shift_expression'''

    def p_equality_expression(self, p):
        '''equality_expression  : relational_expression
                                | equality_expression EQ_EQ relational_expression
                                | equality_expression NOT_EQ relational_expression'''

    def p_and_expression(self, p):
	    '''and_expression   : equality_expression
                            | and_expression AMP equality_expression'''

    def p_exclusive_or_expression(self, p):
        '''exclusive_or_expression  : and_expression
                                    | exclusive_or_expression CARET and_expression'''

    def p_inclusive_or_expression(self, p):
        '''inclusive_or_expression  : exclusive_or_expression
                                    | inclusive_or_expression OR exclusive_or_expression'''


    def p_logical_and_expression(self, p):
        '''logical_and_expression   : inclusive_or_expression
                                    | logical_and_expression AMP_AMP inclusive_or_expression'''


    def p_logical_or_expression(self, p):
        '''logical_or_expression    : logical_and_expression
                                    | logical_or_expression OR_OR logical_and_expression'''

    def p_assignment_expression(self, p):
        '''assignment_expression    : logical_or_expression
                                    | unary_expression assignment_operator assignment_expression'''

    def p_assignment_operator(self, p):
        '''assignment_operator  : PLUS_EQ
                                | MINUS_EQ
                                | STAR_EQ
                                | DIVIDE_EQ
                                | MODULO_EQ
                                | AMP_EQ
                                | OR_EQ
                                | CARET_EQ
                                | EQ
                                | ASSIGN'''

    def p_expression(self, p):
        '''expression   : assignment_expression'''

    def p_lit_operand(self, p):
        '''lit_operand  : INT_LIT
                        | FLOAT_LIT
                        | STRING_LIT
                        | BOOL_LIT'''

if __name__ == "__main__" :
    file = open(sys.argv[1], 'r')
    data = file.read()
    lexer_cls = Lexer()
    lexer_cls.build()
    lexer_cls.lexer.input(data)
    parser_cls = Parser(data)
    parser_cls.build()
    result = parser_cls.parser.parse(data, lexer=lexer_cls.lexer, tracking=True)