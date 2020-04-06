from collections import defaultdict
""" Token type """
ILLEGAL ="ILLEGAL"
EOF = "EOF"
IDENT = "IDENT"
INT = "INT"
ASSIGN = "="
PLUS = "+"
COMMA = ","
SEMICOLON = ";"
LPAREN = "("
RPAREN = ")"
LBRACE = "{"
RBRACE = "}"
LBRACKET = "["
RBRACKET = "]"
FUNCTION = "FUNCTION"
LET = "LET"
BANG = "!"
SLASH = "/"
ASTERISK = "*"
MINUS = "-"
LT = "<"
GT = ">"
BANG = "!"
IF = "IF"
TRUE = "TRUE"
FALSE = "FALSE"
RETURN = "RETURN"
ELSE = "ELSE"
EQ = "=="
NOT_EQ = "!="
STRING = "STRING"
COLON = ":"
MACRO = "MACRO"

""" str to token type """
keywords = defaultdict(lambda: None, {
        'fn': FUNCTION,
        'let': LET,
        'true': TRUE,
        'false': FALSE,
        'return': RETURN,
        'if': IF,
        'else': ELSE
})


class Token():
    """ 字句を表すクラス """
    type=None
    literal=None

    def __init__(self, type, literal):
        self.type = type
        self.literal = literal

    def __str__(self):
        return '{ '+f'type: {self.type}, literal: {self.literal}'+' }'


class Lexer():
    input:str = None
    position:int = None # 入力における現在位置
    read_position:int = 0 # 次に読む位置(次)
    ch:str = None

    def __init__(self, input):
        self.input = input
        self.read_ch()

    def read_ch(self):
        if self.read_position >= len(self.input):
            self.ch = None
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def next_token(self):
        self.skip_whitespace()
        if self.ch == '=':
            if self.peek_ch() == '=':
                self.read_ch()
                tok = Token(EQ, '==')
            else:
                tok = Token(ASSIGN, self.ch)
        elif self.ch == ';':
            tok = Token(SEMICOLON, self.ch)
        elif self.ch == '(':
            tok = Token(LPAREN, self.ch)
        elif self.ch == ')':
            tok = Token(RPAREN, self.ch)
        elif self.ch == '{':
            tok = Token(LBRACE, self.ch)
        elif self.ch == '}':
            tok = Token(RBRACE, self.ch)
        elif self.ch == '+':
            tok = Token(PLUS, self.ch)
        elif self.ch == ',':
            tok = Token(COMMA, self.ch)
        elif self.ch == '-':
            tok = Token(MINUS, self.ch)
        elif self.ch == '/':
            tok = Token(SLASH, self.ch)
        elif self.ch == '*':
            tok = Token(ASTERISK, self.ch)
        elif self.ch == '<':
            tok = Token(LT, self.ch)
        elif self.ch == '>':
            tok = Token(GT, self.ch)
        elif self.ch == '[':
            tok = Token(LBRACKET, self.ch)
        elif self.ch == ']':
            tok = Token(RBRACKET, self.ch)
        elif self.ch == ':':
            tok = Token(COLON, self.ch)
        elif self.ch == '!':
            if self.peek_ch() == '=':
                self.read_ch()
                tok = Token(NOT_EQ, '!=')
            else:
                tok = Token(BANG, self.ch)
        elif self.ch is None:
            tok = Token(EOF, "")
        elif self.ch == '"':
            tok = Token(STRING, self.read_string())
        else:
            if self.ch.isalpha() or self.ch == '_':
                return self.read_ident()
            elif self.ch.isdigit():
                tok =  Token(INT, self.read_integer())
                return tok
            else:
                tok = Token(ILLEGAL, self.ch)
        self.read_ch()
        return tok

    def read_ident(self):
        """ 現在読んでいる位置から文字が出なくなるまでの位置までの文字をとる """
        pos = self.position
        while self.ch and (self.ch.isalpha() or self.ch == '_' or self.ch.isdigit()):
            self.read_ch()
        s = self.input[pos:self.position]
        if keywords[s] is not None:
            return Token(keywords[s], s)
        else:
            return Token(IDENT, self.input[pos:self.position])

    def skip_whitespace(self):
        while self.ch == ' ' or self.ch == '\r' or self.ch == '\n' or self. ch == '\t':
            self.read_ch()

    def read_integer(self):
        pos = self.position
        while self.ch and self.ch.isdigit():
            self.read_ch()
        return self.input[pos: self.position]

    def peek_ch(self):
        if self.read_position >= len(self.input):
            return None
        return self.input[self.read_position]

    def read_string(self):
        pos = self.position+1
        while True :
            self.read_ch()
            if self.ch == '"' or self.ch is None:
                break
        return self.input[pos:self.position]



