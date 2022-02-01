import ply.lex as lex
import sys
from ply.lex import TOKEN

reserved = {
    'var'      : 'VAR',
    'break'    : 'BREAK',
    'continue' : 'CONTINUE', 
    'return'   : 'RETURN',
    'nil'      : 'NIL',
    'default'  : 'DEFAULT',
    'func'     : 'FUNC',
    'case'     : 'CASE',    
    'go'       : 'GO',    
    'struct'   : 'STRUCT',
    'else'     : 'ELSE',
    'package'  : 'PACKAGE',
    'switch'   : 'SWITCH',
    'const'    : 'CONST',
    'if'       : 'IF',
    'type'     : 'TYPE',
    'for'      : 'FOR',
    'import'   : 'IMPORT',
    'struct'   : 'STRUCT',
    'make' : 'MAKE'
}

dec_digits = r'[0-9]+'
hex_digits = r'[0-9a-fA-F]+'
number_lit = rf'((0[xX]{hex_digits})|{dec_digits})'
float_mantissa = rf'(({dec_digits}(\.){dec_digits})|({dec_digits}(\.))|((\.){dec_digits}))'
float_exp = rf'([Ee][+-]?{dec_digits})' 
float_lit = rf'{float_mantissa}{float_exp}?'

class Lexer:

    tokens = list(reserved.values()) + [
        'PLUS_EQ',
        'MINUS_EQ',
        'STAR_EQ',
        'DIVIDE_EQ',
        'MODULO_EQ',
        'AMP_EQ',
        'OR_EQ',
        'CARET_EQ',
        'EQ',
        'EQ_EQ',
        'NOT',
        'NOT_EQ',
        'LT_EQ',
        'GT_EQ',
        'LT',
        'GT',
        'AMP_AMP',
        'OR_OR',
        'PLUS_PLUS',
        'MINUS_MINUS',
        'LSQUARE',
        'RSQUARE',
        'LROUND',
        'RROUND',
        'LCURLY',
        'RCURLY',
        'COMMA',
        'DOT',
        'SEMICOLON',
        'COLON',
        'SINGLE_QUOTES',
        'DOUBLE_QUOTES',
        'INT_LIT',
        'FLOAT_LIT',
        'STRING_LIT',
        'BOOL_LIT',
        'NEWLINE',
        'IDENTIFIER',
        'DATA_TYPE',
        'PLUS',
        'MINUS',
        'STAR',
        'DIVIDE',
        'MODULO',
        'AMP',
        'OR',
        'CARET',
        'AND_NOT',
        'LSHIFT',   
        'RSHIFT',
        'ASSIGN'   
    ]

    t_PLUS_PLUS = r'(\+\+)'
    t_MINUS_MINUS = r'(--)'
    t_PLUS_EQ = r'(\+=)'
    t_MINUS_EQ = r'(-=)'
    t_STAR_EQ = r'(\*=)'
    t_DIVIDE_EQ = r'/='
    t_MODULO_EQ = r'(%=)'
    t_AMP_EQ = r'(&=)'
    t_OR_EQ = r'(\|=)'
    t_CARET_EQ = r'(\^=)'
    t_AMP_AMP = r'(&&)'
    t_OR_OR = r'(\|\|)'
    t_LSHIFT = r'(<<)'
    t_RSHIFT = r'(>>)'
    t_EQ_EQ = r'(==)'
    t_NOT_EQ = r'(!=)'
    t_ASSIGN = r'(\:=)'
    t_NOT = r'(!)'
    t_LT_EQ = r'(<=)'
    t_GT_EQ = r'(>=)'
    t_LSQUARE = r'(\[)'
    t_RSQUARE = r'(\])'
    t_LROUND = r'(\()'
    t_RROUND = r'(\))'
    t_LCURLY = r'(\{)'
    t_RCURLY = r'(\})'
    t_COMMA = r'(\,)'
    t_DOT = r'(\.)'
    t_SEMICOLON = r'(\;)'
    t_COLON = r'(\:)'
    t_DOUBLE_QUOTES = r'(\")'
    t_SINGLE_QUOTES = r'(\')'
    t_PLUS = r'(\+)'
    t_MINUS = r'(-)'
    t_STAR = r'(\*)'
    t_DIVIDE = r'(\/)'
    t_MODULO = r'(\%)'
    t_LT = r'(<)'
    t_GT = r'(>)'
    t_EQ = r'(=)'
    t_AMP = r'(\&)'
    t_OR = r'\|'
    t_CARET = r'\^'
    t_AND_NOT = r'&^'
    t_ignore = " \t"

    def __init__(self):
        self.last_newline = -1
        self.line_no = 1

    def t_DATA_TYPE(self,t):
        r'((uint8)|(uint16)|(uint32)|(uint64)|(int8)|(int16)|(int32)|(int64)|(float32)|(float64)|(byte)|(rune)|(bool)|(int)|(uint)|(string))'
        return t

    def t_BOOL_LIT(self, t):
        r'((true)|(false))'
        t.value = 1 if t.value == "true" else "false"
        return t
    
    @TOKEN(float_lit)
    def t_FLOAT_LIT(self, t):
        t.value = float(eval(t.value))
        return t

    @TOKEN(number_lit)
    def t_INT_LIT(self, t):
        t.value = int(eval(t.value))
        return t

    def t_STRING_LIT(self, t):
        r'\"[^\"]*\"'
        cnt = t.value.count('\n')
        if cnt != 0 :
            print("[ERROR] String shouldn't span multiple lines.. Line:", self.line_no,"Col:",t.lexpos - self.last_newline)
            self.line_no += cnt
            self.last_newline = t.lexpos + t.value.rfind('\n')
            exit(0)
        else :
            return t

    def t_SINGLE_LINE_COMMENT(self, t):
        r'//[^\n]*\n'
        self.line_no += 1
        self.last_newline = t.lexpos + len(t.value) - 1
        pass

    def t_MULTI_LINE_COMMENT(self, t):
        r'/\*(.|\n)*?\*/'
        cnt = t.value.count('\n')
        if cnt != 0 :
            self.line_no += cnt
            self.last_newline = t.lexpos + t.value.rfind('\n') 

    def t_newline(self, t):
        r'\n'
        self.line_no += 1
        self.last_newline = t.lexpos

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value,'IDENTIFIER')
        return t

    def t_error(self, t):
        print(f"ERROR...{t.lexpos}")
        t.lexer.skip(1)
        pass

    def build(self):
        self.lexer = lex.lex(object=self)

    def input(self, data):
        self.lexer.input(data)
        data = [["Token", "Lexeme", "Line#", "Column#"]]
        while True :
            tok = self.lexer.token()
            if not tok :
                break
            data.append([tok.type, tok.value, self.line_no, tok.lexpos - self.last_newline])  
        for row in data:
            print("{: <15} {: <15} {: <8} {: >8}".format(*row))

if __name__ == "__main__" :
    file = open(sys.argv[1], 'r')
    data = file.read()
    lexer = Lexer()
    lexer.build()
    lexer.input(data)        