import unittest
import b1u3token
import b1u3parser
import b1u3ast


class LexerTest(unittest.TestCase):
    def test_next_token1(self):
        input = '=+(){},;'
        tests = [
            (b1u3token.ASSIGN, '='),
            (b1u3token.PLUS, '+'),
            (b1u3token.LPAREN, '('),
            (b1u3token.RPAREN, ')'),
            (b1u3token.LBRACE, '{'),
            (b1u3token.RBRACE, '}'),
            (b1u3token.COMMA, ','),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.EOF, '')
        ]
        lexer = b1u3token.Lexer(input)
        for i, t in enumerate(tests):
            token = lexer.next_token()
            self.assertEqual(t[0], token.type, f'tests[{i}]: token type wrong expected {t[0]}, got {token.type}')
            self.assertEqual(t[1], token.literal, f'tests[{i}]: literal wrong expected "{t[1]}", got "{token.literal}"')

    def test_next_token2(self):
        input = """let five = 5;
        let ten = 10;
        let add = fn (x, y) {
            x + y;
        };
        let result = add(five, ten);"""
        tests = [
            (b1u3token.LET, 'let'),
            (b1u3token.IDENT, 'five'),
            (b1u3token.ASSIGN, '='),
            (b1u3token.INT, '5'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.LET, 'let'),
            (b1u3token.IDENT, 'ten'),
            (b1u3token.ASSIGN, '='),
            (b1u3token.INT, '10'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.LET, 'let'),
            (b1u3token.IDENT, 'add'),
            (b1u3token.ASSIGN, '='),
            (b1u3token.FUNCTION, 'fn'),
            (b1u3token.LPAREN, '('),
            (b1u3token.IDENT, 'x'),
            (b1u3token.COMMA, ','),
            (b1u3token.IDENT, 'y'),
            (b1u3token.RPAREN, ')'),
            (b1u3token.LBRACE, '{'),
            (b1u3token.IDENT, 'x'),
            (b1u3token.PLUS, '+'),
            (b1u3token.IDENT, 'y'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.RBRACE, '}'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.LET, 'let'),
            (b1u3token.IDENT, 'result'),
            (b1u3token.ASSIGN, '='),
            (b1u3token.IDENT, 'add'),
            (b1u3token.LPAREN, '('),
            (b1u3token.IDENT, 'five'),
            (b1u3token.COMMA, ','),
            (b1u3token.IDENT, 'ten'),
            (b1u3token.RPAREN, ')'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.EOF, '')
        ]
        lexer = b1u3token.Lexer(input)
        for i, t in enumerate(tests):
            token = lexer.next_token()
            self.assertEqual(t[0], token.type, f'tests[{i}]: token type wrong expected {t[0]}, got {token.type}')
            self.assertEqual(t[1], token.literal, f'tests[{i}]: literal wrong expected "{t[1]}", got "{token.literal}"')

    def test_next_token3(self):
        input = '!-/3*;5 < 100 > 6;'
        tests = [
            (b1u3token.BANG, '!'),
            (b1u3token.MINUS, '-'),
            (b1u3token.SLASH, '/'),
            (b1u3token.INT, '3'),
            (b1u3token.ASTERISK, '*'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.INT, '5'),
            (b1u3token.LT, '<'),
            (b1u3token.INT, '100'),
            (b1u3token.GT, '>'),
            (b1u3token.INT, '6'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.EOF, '')
        ]
        lexer = b1u3token.Lexer(input)
        for i, t in enumerate(tests):
            token = lexer.next_token()
            self.assertEqual(t[0], token.type, f'tests[{i}]: token type wrong expected {t[0]}, got {token.type}')
            self.assertEqual(t[1], token.literal, f'tests[{i}]: literal wrong expected "{t[1]}", got "{token.literal}"')

    def test_next_token4(self):
        input = 'if return true false else'
        tests = [
            (b1u3token.IF, 'if'),
            (b1u3token.RETURN, 'return'),
            (b1u3token.TRUE, 'true'),
            (b1u3token.FALSE, 'false'),
            (b1u3token.ELSE, 'else'),
            (b1u3token.EOF, '')
        ]
        lexer = b1u3token.Lexer(input)
        for i, t in enumerate(tests):
            token = lexer.next_token()
            self.assertEqual(t[0], token.type, f'tests[{i}]: token type wrong expected {t[0]}, got {token.type}')
            self.assertEqual(t[1], token.literal, f'tests[{i}]: literal wrong expected "{t[1]}", got "{token.literal}"')

    def test_next_token5(self):
        input = '10 == 5; 3 != 8; [1, 2]; macro(x, y) { x + y };'
        tests = [
            (b1u3token.INT, '10'),
            (b1u3token.EQ, '=='),
            (b1u3token.INT, '5'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.INT, '3'),
            (b1u3token.NOT_EQ, '!='),
            (b1u3token.INT, '8'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.LBRACKET, '['),
            (b1u3token.INT, '1'),
            (b1u3token.COMMA, ','),
            (b1u3token.INT, '2'),
            (b1u3token.RBRACKET, ']'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.MACRO, 'macro'),
            (b1u3token.LPAREN, ')'),
            (b1u3token.IDENT, 'x'),
            (b1u3token.COMMA, ','),
            (b1u3token.IDENT, 'y'),
            (b1u3token.LBRACE, '{'),
            (b1u3token.IDENT, 'x'),
            (b1u3token.PLUS, '+'),
            (b1u3token.IDENT, 'y'),
            (b1u3token.RBRACE, '}'),
            (b1u3token.SEMICOLON, ';'),
            (b1u3token.EOF, '')
        ]
        lexer = b1u3token.Lexer(input)
        for i, t in enumerate(tests):
            token = lexer.next_token()
            self.assertEqual(t[0], token.type, f'tests[{i}]: token type wrong expected {t[0]}, got {token.type}')
            self.assertEqual(t[1], token.literal, f'tests[{i}]: literal wrong expected "{t[1]}", got "{token.literal}"')

    def test_next_token6(self):
        input = '"foobar" "foo bar" {"A": "B"}'
        tests = [
            (b1u3token.STRING, "foobar"),
            (b1u3token.STRING, "foo bar"),
            (b1u3token.LBRACE, "{"),
            (b1u3token.STRING, "A"),
            (b1u3token.COLON, ":"),
            (b1u3token.STRING, "B"),
            (b1u3token.RBRACE, "}"),
            (b1u3token.EOF, '')
        ]
        lexer = b1u3token.Lexer(input)
        for i, t in enumerate(tests):
            token = lexer.next_token()
            self.assertEqual(t[0], token.type, f'tests[{i}]: token type wrong expected {t[0]}, got {token.type}')
            self.assertEqual(t[1], token.literal, f'tests[{i}]: literal wrong expected "{t[1]}", got "{token.literal}"')



