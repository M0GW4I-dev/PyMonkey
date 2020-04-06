import b1u3ast
import b1u3token
from collections import defaultdict

# Precedence rank, greater is high priority
LOWEST = 1
EQUALS = 2
LESSGREATER = 3
SUM = 4
PRODUCT = 5
PREFIX = 6
CALL = 7
INDEX = 8

# 優先順位テーブル
precedences = {
    b1u3token.EQ: EQUALS,
    b1u3token.NOT_EQ: EQUALS,
    b1u3token.LT: LESSGREATER,
    b1u3token.GT: LESSGREATER,
    b1u3token.PLUS: SUM,
    b1u3token.MINUS: SUM,
    b1u3token.SLASH: PRODUCT,
    b1u3token.ASTERISK: PRODUCT,
    b1u3token.LPAREN: CALL,
    b1u3token.LBRACKET: INDEX
}


class Parser():
    l: b1u3token.Lexer=None
    cur_token = None
    peek_token = None
    errors:[str] = None
    prefix_parse_fns=None # 前置の演算子が呼ばれた時の関数
    infix_parse_fns=None # 中置の演算子が呼ばれた時の関数

    def __init__(self, lexer):
        self.l = lexer
        self.errors = []
        self.next_token()
        self.next_token()
        self.prefix_parse_fns = defaultdict(lambda: None)
        self.register_prefix(b1u3token.IDENT, self.parse_identifier)
        self.register_prefix(b1u3token.INT, self.parse_integer_literal)
        self.register_prefix(b1u3token.BANG, self.parse_prefix_expression)
        self.register_prefix(b1u3token.MINUS, self.parse_prefix_expression)
        self.register_prefix(b1u3token.TRUE, self.parse_boolean)
        self.register_prefix(b1u3token.FALSE, self.parse_boolean)
        self.register_prefix(b1u3token.LPAREN, self.parse_grouped_expression)
        self.register_prefix(b1u3token.IF, self.parse_if_expression)
        self.register_prefix(b1u3token.FUNCTION, self.parse_function_literal)
        self.register_prefix(b1u3token.STRING, self.parse_string_literal)
        self.register_prefix(b1u3token.LBRACKET, self.parse_array_literal)
        self.register_prefix(b1u3token.LBRACE, self.parse_hash_literal)
        self.register_prefix(b1u3token.MACRO, self.parse_macro_literal)
        self.infix_parse_fns = defaultdict(lambda: None)
        self.register_infix(b1u3token.PLUS, self.parse_infix_expression)
        self.register_infix(b1u3token.MINUS, self.parse_infix_expression)
        self.register_infix(b1u3token.SLASH, self.parse_infix_expression)
        self.register_infix(b1u3token.ASTERISK, self.parse_infix_expression)
        self.register_infix(b1u3token.EQ, self.parse_infix_expression)
        self.register_infix(b1u3token.NOT_EQ, self.parse_infix_expression)
        self.register_infix(b1u3token.LT, self.parse_infix_expression)
        self.register_infix(b1u3token.GT, self.parse_infix_expression)
        self.register_infix(b1u3token.LPAREN, self.parse_call_expression)
        self.register_infix(b1u3token.LBRACKET, self.parse_index_expression)

    def next_token(self):
        """ Lexer の next_token と紛らわしいな """
        self.cur_token = self.peek_token
        self.peek_token = self.l.next_token()

    def parse_program(self):
        program = b1u3ast.Program() # ast のルートノードを作成
        program.statements = []
        while self.cur_token.type != b1u3token.EOF:
            stmt = self.parse_statement()
            if stmt != None:
                program.statements.append(stmt)
            self.next_token()
        return program

    def parse_statement(self):
        if self.cur_token.type == b1u3token.LET:
            stmt = self.parse_let_statement()
            return stmt
        elif self.cur_token.type == b1u3token.RETURN:
            stmt = self.parse_return_statement()
            return stmt
        else:
            return self.parse_expression_statement()

    def parse_let_statement(self):
        stmt = b1u3ast.LetStatement(token=self.cur_token)

        if not self.expect_peek(b1u3token.IDENT):
            return None
        # value には、識別子の文字列自身を渡している
        stmt.name = b1u3ast.Identifier(token=self.cur_token, value=self.cur_token.literal)
        if not self.expect_peek(b1u3token.ASSIGN):
            return None
        self.next_token()
        stmt.value = self.parse_expression(LOWEST)
        if self.peek_token_is(b1u3token.SEMICOLON):
            self.next_token()
        return stmt

    def parse_return_statement(self):
        stmt = b1u3ast.ReturnStatement(token=self.cur_token)
        # skip return token
        self.next_token()
        stmt.return_value = self.parse_expression(LOWEST)

        stmt.value = self.parse_expression(LOWEST)
        if self.peek_token_is(b1u3token.SEMICOLON):
            self.next_token()
        return stmt

    def cur_token_is(self, t=None):
        return self.cur_token.type == t

    def peek_token_is(self, t=None):
        return self.peek_token.type == t

    def expect_peek(self, t=None):
        if self.peek_token_is(t):
            self.next_token()
            return True
        else:
            self.peek_error(t)
            return False

    def errors(self):
        return self.errors

    def peek_error(self, t):
        msg = f'expected next token to be {t}, got {self.peek_token.type}'
        self.errors.append(msg)


    def register_prefix(self, token_type, fn):
        self.prefix_parse_fns[token_type] = fn


    def register_infix(self, token_type, fn):
        self.infix_parse_fns[token_type] = fn

    def parse_expression_statement(self):
        stmt = b1u3ast.ExpressionStatement(token=self.cur_token)
        stmt.expression = self.parse_expression(LOWEST)
        if self.peek_token_is(b1u3token.SEMICOLON):
            self.next_token()
        return stmt

    def parse_expression(self, precedence):
        prefix = self.prefix_parse_fns[self.cur_token.type]
        if prefix is None:
            self.no_prefix_parse_fn_error(self.cur_token.type)
            return None
        left_exp = prefix()
        # maybe error
        while not self.peek_token_is(b1u3token.SEMICOLON) and precedence < self.peek_precedence():
            infix = self.infix_parse_fns[self.peek_token.type]
            if infix is None:
                return left_exp
            self.next_token()
            left_exp = infix(left_exp)
        return left_exp

    def parse_identifier(self):
        return b1u3ast.Identifier(token=self.cur_token, value=self.cur_token.literal)

    def parse_integer_literal(self):
        lit = b1u3ast.IntegerLiteral(token=self.cur_token)
        try:
            value = int(self.cur_token.literal)
            lit.value = value
        except _:
            self.errors.append(f'could not parse {self.cur_token.literal} as integer')
            return None
        return lit

    def no_prefix_parse_fn_error(self, t):
        msg = f'no prefix parse function for {t} found'
        self.errors.append(msg)

    def parse_prefix_expression(self):
        expression = b1u3ast.PrefixExpression(token=self.cur_token, operator=self.cur_token.literal)
        self.next_token()
        expression.right = self.parse_expression(PREFIX)
        return expression

    def peek_precedence(self):
        try:
            return precedences[self.peek_token.type]
        except KeyError:
            return LOWEST

    def cur_precedence(self):
        try:
            return precedences[self.cur_token.type]
        except KeyError:
            return LOWEST

    def parse_infix_expression(self, left):
        expression = b1u3ast.InfixExpression(token=self.cur_token, operator=self.cur_token.literal, left=left)
        precedence = self.cur_precedence()
        self.next_token()
        expression.right = self.parse_expression(precedence)
        return expression

    def parse_grouped_expression(self):
        self.next_token()
        exp = self.parse_expression(LOWEST)
        if not self.expect_peek(b1u3token.RPAREN):
            return None
        return exp

    def parse_boolean(self):
        return b1u3ast.Boolean(token=self.cur_token, value=self.cur_token_is(b1u3token.TRUE))

    def parse_if_expression(self):
        expression = b1u3ast.IfExpression(token=self.cur_token)
        if not self.expect_peek(b1u3token.LPAREN):
            return None

        self.next_token()
        expression.condition = self.parse_expression(LOWEST)
        if not self.expect_peek(b1u3token.RPAREN):
            return None
        if not self.expect_peek(b1u3token.LBRACE):
            return None
        expression.consequence = self.parse_block_statement()
        if self.peek_token_is(b1u3token.ELSE):
            self.next_token()
            if not self.expect_peek(b1u3token.LBRACE):
                return None
            expression.alternative = self.parse_block_statement()

        return expression

    def parse_block_statement(self):
        block = b1u3ast.BlockStatement(token=self.cur_token)
        block.statements = []
        self.next_token()
        while not self.cur_token_is(b1u3token.RBRACE) and not self.cur_token_is(b1u3token.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                block.statements.append(stmt)
            self.next_token()
        return block

    def parse_function_literal(self):
        lit = b1u3ast.FunctionLiteral(token=self.cur_token)
        if not self.expect_peek(b1u3token.LPAREN):
            return None
        lit.parameters = self.parse_function_parameters()
        if not self.expect_peek(b1u3token.LBRACE):
            return None
        lit.body = self.parse_block_statement()
        return lit

    def parse_function_parameters(self):
        identifiers = []
        if self.peek_token_is(b1u3token.RPAREN):
            self.next_token()
            return identifiers
        self.next_token()
        ident = b1u3ast.Identifier(token=self.cur_token, value=self.cur_token.literal)
        identifiers.append(ident)

        while self.peek_token_is(b1u3token.COMMA):
            self.next_token()
            self.next_token()
            ident = b1u3ast.Identifier(token=self.cur_token, value=self.cur_token.literal)
            identifiers.append(ident)

        if not self.expect_peek(b1u3token.RPAREN):
            return None
        return identifiers


    def parse_call_expression(self, function):
        exp = b1u3ast.CallExpression(token=self.cur_token, function=function)
        exp.arguments = self.parse_call_arguments()
        return exp

    def parse_call_arguments(self):
        args = []
        if self.peek_token_is(b1u3token.RPAREN):
            self.next_token()
            return args

        self.next_token()
        args.append(self.parse_expression(LOWEST))
        while self.peek_token_is(b1u3token.COMMA):
            self.next_token()
            self.next_token()
            args.append(self.parse_expression(LOWEST))

        if not self.expect_peek(b1u3token.RPAREN):
            return None
        return args

    def parse_string_literal(self):
        return b1u3ast.StringLiteral(token=self.cur_token, value=self.cur_token.literal)

    def parse_array_literal(self):
        array = b1u3ast.ArrayLiteral(token=self.cur_token)
        array.elements = self.parse_expression_list(b1u3token.RBRACKET)
        return array

    def parse_expression_list(self, end):
        ret = []
        if self.peek_token_is(end):
            self.next_token()
            return ret
        self.next_token()
        ret.append(self.parse_expression(LOWEST))
        while self.peek_token_is(b1u3token.COMMA):
            self.next_token()
            self.next_token()
            ret.append(self.parse_expression(LOWEST))

        if not self.expect_peek(end):
            return None
        return ret

    def parse_index_expression(self, left):
        exp = b1u3ast.IndexExpression(token=self.cur_token, left=left)
        self.next_token()
        exp.index = self.parse_expression(LOWEST)
        if not self.expect_peek(b1u3token.RBRACKET):
            return None
        return exp

    def parse_hash_literal(self):
        h = b1u3ast.HashLiteral(token=self.cur_token)
        h.pairs = {}
        while not self.peek_token_is(b1u3token.RBRACE):
            self.next_token()
            key = self.parse_expression(LOWEST)
            if not self.expect_peek(b1u3token.COLON):
                return None
            self.next_token()
            value = self.parse_expression(LOWEST)
            h.pairs[key] = value
            if not self.peek_token_is(b1u3token.RBRACE) and not self.expect_peek(b1u3token.COMMA):
                return None
        if not self.expect_peek(b1u3token.RBRACE):
            return None
        return h

    def parse_macro_literal(self):
        lit = b1u3ast.MacroLiteral(token=self.cur_token)
        if not self.expect_peek(b1u3token.LPAREN):
            return None
        lit.parameters = self.parse_function_parameters()
        if not self.expect_peek(b1u3token.LBRACE):
            return None
        lit.body = self.parse_block_statement()
        return lit

