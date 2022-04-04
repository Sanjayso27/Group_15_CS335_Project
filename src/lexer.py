# TODO : modify to put ; after each }, ), ++, --, ID, DATA_TYPE, Literals, BREAK, CONTINUE, RETURN when followed by newline 
import ply.lex as lex
import sys
from ply.lex import TOKEN
from helper import print_warn, print_error, print_table

escaped_char = {
    "n": "\n",
    "b": "\b",
    "t": "\t",
    "\\": "\\",
    '\"': '\"',
    '\'': '\'',
    "0": "\0",
}

reserved = {
    "var": "VAR",
    "break": "BREAK",
    "continue": "CONTINUE",
    "return": "RETURN",
    "nil": "NIL",
    #"default": "DEFAULT",
    "func": "FUNC",
    #"case": "CASE",
    "goto": "GOTO",
    "struct": "STRUCT",
    "else": "ELSE",
    "package": "PACKAGE",
    #"switch": "SWITCH",
    "const": "CONST",
    "if": "IF",
    "type": "TYPE",
    "for": "FOR",
    "import": "IMPORT",
    "struct": "STRUCT",
    "make": "MAKE",
}

tokens = list(reserved.values()) + [
    "PLUS_EQ",
    "MINUS_EQ",
    "STAR_EQ",
    "DIVIDE_EQ",
    "MODULO_EQ",
    "AMP_EQ",
    "OR_EQ",
    "CARET_EQ",
    "EQ",
    "EQ_EQ",
    "NOT",
    "NOT_EQ",
    "LE",
    "GE",
    "LT",
    "GT",
    "AMP_AMP",
    "OR_OR",
    "PLUS_PLUS",
    "MINUS_MINUS",
    "LSQUARE",
    "RSQUARE",
    "LROUND",
    "RROUND",
    "LCURLY",
    "RCURLY",
    "COMMA",
    "DOT",
    "SEMICOLON",
    "COLON",
    #"SINGLE_QUOTES",
    #"DOUBLE_QUOTES",
    "INT_LIT",
    "FLOAT_LIT",
    "STRING_LIT",
    "BOOL_LIT",
    "CHAR_LIT",
    #"BR",
    "ID",
    "DATA_TYPE",
    "PLUS",
    "MINUS",
    "STAR",
    "DIVIDE",
    "MODULO",
    "AMP",
    "OR",
    "CARET",
    #"AND_NOT",
    "LSHIFT",
    "RSHIFT",
    "ASSIGN",
]

dec_digits = r"[0-9]+"
hex_digits = r"[0-9a-fA-F]+"
number_lit = rf"((0[xX]{hex_digits})|{dec_digits})"
float_mantissa = (
    rf"(({dec_digits}(\.){dec_digits})|({dec_digits}(\.))|((\.){dec_digits}))"
)
float_exp = rf"([Ee][+-]?{dec_digits})"
float_lit = rf"{float_mantissa}{float_exp}?"
char_lit = r"'.*'"


class LexerGo:

    t_PLUS_PLUS = r"(\+\+)"
    t_MINUS_MINUS = r"(--)"
    t_PLUS_EQ = r"(\+=)"
    t_MINUS_EQ = r"(-=)"
    t_STAR_EQ = r"(\*=)"
    t_DIVIDE_EQ = r"/="
    t_MODULO_EQ = r"(%=)"
    t_AMP_EQ = r"(&=)"
    t_OR_EQ = r"(\|=)"
    t_CARET_EQ = r"(\^=)"
    t_AMP_AMP = r"(&&)"
    t_OR_OR = r"(\|\|)"
    t_LSHIFT = r"(<<)"
    t_RSHIFT = r"(>>)"
    t_EQ_EQ = r"(==)"
    t_NOT_EQ = r"(!=)"
    t_ASSIGN = r"(\:=)"
    t_NOT = r"(!)"
    t_LE = r"(<=)"
    t_GE = r"(>=)"
    t_LSQUARE = r"(\[)"
    t_RSQUARE = r"(\])"
    t_LROUND = r"(\()"
    t_RROUND = r"(\))"
    t_LCURLY = r"(\{)"
    t_RCURLY = r"(\})"
    t_COMMA = r"(\,)"
    t_DOT = r"(\.)"
    t_SEMICOLON = r"(\;)"
    t_COLON = r"(\:)"
    #t_DOUBLE_QUOTES = r"(\")"
    #t_SINGLE_QUOTES = r"(\')"
    t_PLUS = r"(\+)"
    t_MINUS = r"(-)"
    t_STAR = r"(\*)"
    t_DIVIDE = r"(\/)"
    t_MODULO = r"(\%)"
    t_LT = r"(<)"
    t_GT = r"(>)"
    t_EQ = r"(=)"
    t_AMP = r"(\&)"
    t_OR = r"\|"
    t_CARET = r"\^"
    #t_AND_NOT = r"&^"
    t_ignore = " \t"

    def __init__(self):
        self.last_newline = -1
        self.line_no = 1
        self.isError = False
        self.isTerminalError = False
        self.tokens = tokens
        self.tokenList = {}

    def t_DATA_TYPE(self, t):
        r"((uint8)|(uint16)|(uint32)|(uint64)|(int8)|(int16)|(int32)|(int64)|(float32)|(float64)|(byte)|(rune)|(bool)|(int)|(uint)|(string))"
        return t

    def t_BOOL_LIT(self, t):
        r"((true)|(false))"
        return t

    @TOKEN(float_lit)
    def t_FLOAT_LIT(self, t):
        t.value = float(eval(t.value))
        return t

    @TOKEN(number_lit)
    def t_INT_LIT(self, t):
        t.value = int(eval(t.value))
        return t

    @TOKEN(char_lit)
    def t_CHAR_LIT(self, t):
        if len(t.value) == 3:
            t.value = ord(t.value[1])
        elif len(t.value) > 4:
            self.isError = True
            msg = "Invalid char literal"
            print_error(msg, self.line_no, t.lexpos - self.last_newline)
            return
        else:
            if t.value[1] == "\\" and t.value[2] in escaped_char.keys():
                t.value = ord(escaped_char[t.value[2]])
            else:
                msg = "Invalid char literal"
                print_error(msg, self.line_no, t.lexpos - self.last_newline)
                return
        return t

    def t_STRING_LIT(self, t):
        r"\"[^\"]*\" "
        cnt = t.value.count("\n")
        if cnt != 0:
            msg = "String shouldn't span multiple lines"
            print_error(msg, self.line_no, t.lexpos - self.last_newline)
            self.isError = True
            self.line_no += cnt
            self.last_newline = t.lexpos + t.value.rfind("\n")
        else:
            return t

    def t_SINGLE_LINE_COMMENT(self, t):
        r"//[^\n]*(\n|$)"
        self.line_no += 1
        self.last_newline = t.lexpos + len(t.value) - 1
        pass

    def t_MULTI_LINE_COMMENT(self, t):
        r"/\*(.|\n)*?\*/"
        cnt = t.value.count("\n")
        if cnt != 0:
            self.line_no += cnt
            self.last_newline = t.lexpos + t.value.rfind("\n")

    def t_UNENDING_MULTI_LINE_COMMENT(self, t):
        r"/\*(.|\n)*$"
        msg = "Found unending multiline comment"
        self.isError = True
        print_error(msg, self.line_no, t.lexpos - self.last_newline)

    def t_BR(self, t):
        r"\n"
        self.line_no += 1
        self.last_newline = t.lexpos
        t.value = 'BR'
        return
        
    def t_IDENTIFIER(self, t):
        r"[a-zA-Z_][a-zA-Z_0-9]*"
        t.type = reserved.get(t.value, "ID")
        return t

    def t_error(self, t):
        msg = "Found invalid character"
        print_error(msg, self.line_no, t.lexpos - self.last_newline)
        self.isError = True
        t.lexer.skip(1)
        pass

    def build(self):
        self.lexer = lex.lex(object=self)

    def input(self, data, show_lexer_output=False):
        self.lexer.input(data)

        while True:
            tok = self.lexer.token()
            if not tok:
                break
            self.tokenList[tok.lexpos] = [
                tok.type,
                tok.value,
                self.line_no,
                tok.lexpos - self.last_newline,
            ]

        if show_lexer_output:
            print_table(
                ["Token", "Value", "Line", "Column"], list(self.tokenList.values())
            )


if __name__ == "__main__":
    file = open(sys.argv[1], "r")
    data = file.read()
    lexer = LexerGo()
    lexer.build()
    lexer.input(data, show_lexer_output=True)
