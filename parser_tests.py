import unittest
import b1u3token
import b1u3parser
import b1u3ast


class ParserTest(unittest.TestCase):
    def test_let_statements(self):
        tests = [
                ["let x = 5;", "x", 5],
                ["let y = true;", "y", True],
                ["let foobar = y;", "foobar", "y"]
        ]
        for i, tt in enumerate(tests):
            lexer = b1u3token.Lexer(tt[0])
            parser = b1u3parser.Parser(lexer)
            program = parser.parse_program()
            self.check_parser_errors(parser)
            self.assertEqual(len(program.statements), 1, f"Program doesn't contain 1 statements. got={len(program.statements)}")
            stmt = program.statements[0]
            self.assertTrue(isinstance(stmt, b1u3ast.LetStatement), f'stmt is not LetStatement instance, got={type(stmt)}')
            self.help_let_statement_test(stmt, tt[1])
            val = stmt.value
            self.help_test_literal_expression(val, tt[2])


    def help_let_statement_test(self, stmt, name):
        self.assertEqual(stmt.token_literal(), 'let', f'stmt.token_literal() is not "let", got={stmt.token_literal()}')

        self.assertTrue(isinstance(stmt, b1u3ast.LetStatement), 'stmt is not LetStatement')
        self.assertEqual(stmt.name.value, name, f'stmt is not {name}, got={stmt.name}')
        self.assertEqual(stmt.name.token_literal(), name, f'stmt is not {name}, got={stmt.name.token_literal()}')
        # print(stmt)


    def check_parser_errors(self, parser):
        errors = parser.errors
        if len(errors) == 0:
            return
        errmsgs = []
        import sys
        errmsgs.append(f'\nparser has {len(errors)} errors')
        for e in errors:
            errmsgs.append(f'parser error: {e}')
        self.fail('\n'.join(errmsgs))


    def test_return_statement(self):
        input = """
            return 5;
            return 10;
            return 993322;
        """
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        # print(dir(program))
        self.check_parser_errors(p)

        self.assertEqual(len(program.statements), 3, f'p.statements does not contain 3 statements. got={len(program.statements)}')
        for s in program.statements:
            self.assertTrue(isinstance(s, b1u3ast.ReturnStatement), 's is not ReturnStatement')
            self.assertEqual(s.token_literal(), 'return', f"s is not 'return', got={s.token_literal()}")

    def test_identifier_expression(self):
        input = 'foobar;'
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
        stmt = program.statements[0]
        exp = stmt.expression
        self.assertEqual(exp.value, 'foobar', f'exp.value is not foobar, got={exp.value}')
        self.assertEqual(exp.token_literal(), 'foobar', f'exp.token_literal() is not foobar, got={exp.token_literal()}')

    def test_integer_literal_expression(self):
        input = '5;'
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
        stmt = program.statements[0]
        literal = stmt.expression
        self.assertTrue(isinstance(literal, b1u3ast.IntegerLiteral))
        self.assertEqual(literal.value, 5, f'literal.value is not 5, got={literal.value}')
        self.assertEqual(literal.token_literal(), '5', f'literal.token_literal() is not "5", got={literal.token_literal()}')


    def test_parse_prefix_expression(self):
        prefix_tests = [['!5;', '!', 5], ['-15;', '-', 15], ['!true;', '!', True], ['!false;', '!', False]]
        for tt in prefix_tests:
            l = b1u3token.Lexer(tt[0])
            p = b1u3parser.Parser(l)
            program = p.parse_program()
            self.check_parser_errors(p)
            self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
            stmt = program.statements[0]
            self.assertTrue(isinstance(stmt, b1u3ast.ExpressionStatement))
            exp = stmt.expression
            self.assertTrue(isinstance(exp, b1u3ast.PrefixExpression))
            self.assertEqual(exp.operator, tt[1], f'exp.operator is not {tt[1]}, got={exp.operator}')
            self.help_test_literal_expression(exp.right, tt[2])
            # self.help_test_integer_literal(exp.right, tt[2])

    def help_test_integer_literal(self, il, value):
        self.assertTrue(isinstance(il, b1u3ast.IntegerLiteral))
        integ = il
        self.assertEqual(integ.value, value, f'integ.value is not {value}, got={integ.value}')
        self.assertEqual(integ.token_literal(), str(value), f'integ.value is not {str(value)}, got={integ.token_literal()}')

    def test_parse_infix_expressions(self):
        infix_tests = [
                ['5+5;', 5, '+', 5],
                ['5-5;', 5, '-', 5],
                ['5*5;', 5, '*', 5],
                ['5/5;', 5, '/', 5],
                ['5>5;', 5, '>', 5],
                ['5<5;', 5, '<', 5],
                ['5 == 5;', 5, '==', 5],
                ['5 != 5;', 5, '!=', 5],
                ['true == true', True, '==', True],
                ['true != false', True, '!=', False],
                ['false == false', False, '==', False]
        ]

        for tt in infix_tests:
            l = b1u3token.Lexer(tt[0])
            p = b1u3parser.Parser(l)
            program = p.parse_program()
            self.check_parser_errors(p)
            self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
            stmt = program.statements[0]
            self.assertTrue(isinstance(stmt, b1u3ast.ExpressionStatement))
            exp = stmt.expression
            self.help_test_infix_expression(exp, tt[1], tt[2], tt[3])
            """
            self.assertTrue(isinstance(exp, b1u3ast.InfixExpression))
            self.help_test_integer_literal(exp.left, tt[1])
            self.assertEqual(exp.operator, tt[2], f'exp.operator is not {tt[2]}, got={exp.operator}')
            self.help_test_integer_literal(exp.right, tt[3])
            """


    def help_test_identifier(self, exp, value):
        self.assertTrue(isinstance(exp, b1u3ast.Identifier))
        self.assertEqual(exp.value, value, f'exp.value is not {value}, got={exp.value}')
        self.assertEqual(exp.token_literal(), value, f'exp.token_literal() is not {value}, got={exp.token_literal()}')

    def help_test_literal_expression(self, exp, expected):
        if type(expected) == int:
            self.help_test_integer_literal(exp, expected)
        elif type(expected) == str:
            self.help_test_identifier(exp, expected)
        elif type(expected) == bool:
            self.help_test_boolean_literal(exp, expected)
        else:
            self.fail(f'type of exp not handled.got={type(exp)}')

    def help_test_infix_expression(self, exp, left, operator, right):
        self.assertTrue(isinstance(exp, b1u3ast.InfixExpression), f'exp is not instance of InfixExpression, got={type(exp)}')
        self.help_test_literal_expression(exp.left, left)
        self.assertEqual(exp.operator, operator, f'exp.operator is not {operator}, got={exp.operator}')
        self.help_test_literal_expression(exp.right, right)


    def test_boolean_expression(self):
        input = 'true;false;'
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 2, f'p.statements does not contain 2 statements. got={len(program.statements)}')
        stmt = program.statements[0]
        literal = stmt.expression
        self.assertTrue(isinstance(literal, b1u3ast.Boolean))
        # print(literal.value)
        self.assertTrue(literal.value, f'literal.value is not 5, got={literal.value}')
        stmt = program.statements[1]
        literal = stmt.expression
        self.assertTrue(isinstance(literal, b1u3ast.Boolean))
        self.assertTrue(not literal.value, f'literal.value is not False, got={not literal.value}')

    def test_operator_precedence_parsing(self):
        tests = [
                [
                    'true',
                    'true',
                ],
                [
                    'false',
                    'false'
                ],
                [
                    '3 > 5 == false',
                    '((3 > 5) == false)'
                ],
                [
                    '3 < 5 == true',
                    '((3 < 5) == true)'
                ],
                [
                    '1 + (2 + 3) + 4',
                    '((1 + (2 + 3)) + 4)'
                ],
                [
                    '(5 + 5) + 2',
                    '((5 + 5) + 2)'
                ],
                [
                    '2 / (5 + 5)',
                    '(2 / (5 + 5))'
                ],
                [
                    '-(5 + 5)',
                    '(-(5 + 5))'
                ],
                [
                    '!(true == true)',
                    '(!(true == true))'
                ],
                [
                    'a + add(b * c) + d',
                    '((a + add((b * c))) + d)'
                ],
                [
                    'add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))',
                    'add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))'
                ],
                [
                    'add(a + b + c * d / f + g)',
                    'add((((a + b) + ((c * d) / f)) + g))'
                ],
                [
                    'a * [1, 2, 3, 4][b * c] * d',
                    '((a * ([ 1, 2, 3, 4 ][(b * c)])) * d)'
                ],
                [
                    'add(a * b[2], b[1], 2 * [1, 2][1])',
                    'add((a * (b[2])), (b[1]), (2 * ([ 1, 2 ][1])))'
                ]
            ]
        for tt in tests:
            l = b1u3token.Lexer(tt[0])
            p = b1u3parser.Parser(l)
            program = p.parse_program()
            self.check_parser_errors(p)
            actual = repr(program)
            self.assertEqual(actual, tt[1], f'expected={tt[1]}, got={actual}')

    def help_test_boolean_literal(self, exp, value):
        self.assertTrue(isinstance(exp, b1u3ast.Boolean), f'exp is not b1u3ast.Boolean. got={type(exp)}')
        self.assertEqual(exp.value, value, f'exp is not {value}, got={type(exp)}')
        self.assertEqual(exp.token_literal(), str(value).lower(), f'exp.token_literal() is not {str(value).title()}, got={exp.token_literal()}')

    def test_if_expression(self):
        input = 'if (x < y) { x }'
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
        stmt = program.statements[0]
        self.assertTrue(isinstance(stmt, b1u3ast.ExpressionStatement), f'stmt.Expression is not ast.ExpressionStatement. got={type(stmt)}')
        exp = stmt.expression
        self.assertTrue(isinstance(exp, b1u3ast.IfExpression), f'stmt.Expression is not ast.IfExpression. got={type(stmt)}')
        self.help_test_infix_expression(exp.condition, 'x', '<', 'y')
        self.assertEqual(len(exp.consequence.statements), 1, f'consequence is not 1 statements. got={len(exp.consequence.statements)}')
        self.assertTrue(isinstance(exp.consequence.statements[0], b1u3ast.ExpressionStatement), f'exp.consequence.statements[0] is not ast.ExpressionStatement. got={type(exp.consequence.statements[0])}')
        consequence = exp.consequence.statements[0]
        self.help_test_identifier(consequence.expression, 'x')
        if exp.alternative:
            self.fail('consequence.alternative is not None')


    def test_if_else_expression(self):
        input = 'if (x < y) { x } else { z }'
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
        stmt = program.statements[0]
        self.assertTrue(isinstance(stmt, b1u3ast.ExpressionStatement), f'stmt.Expression is not ast.ExpressionStatement. got={type(stmt)}')
        exp = stmt.expression
        self.assertTrue(isinstance(exp, b1u3ast.IfExpression), f'stmt.Expression is not ast.IfExpression. got={type(stmt)}')
        self.help_test_infix_expression(exp.condition, 'x', '<', 'y')
        self.assertEqual(len(exp.consequence.statements), 1, f'consequence is not 1 statements. got={len(exp.consequence.statements)}')
        self.assertTrue(isinstance(exp.consequence.statements[0], b1u3ast.ExpressionStatement), f'exp.consequence.statements[0] is not ast.ExpressionStatement. got={type(exp.consequence.statements[0])}')
        consequence = exp.consequence.statements[0]
        self.help_test_identifier(consequence.expression, 'x')
        if exp.alternative:
            self.assertTrue(isinstance(exp.alternative, b1u3ast.BlockStatement))
            self.assertEqual(len(exp.alternative.statements), 1, f'exp.alternative.statements does not have 1 statement, got={len(exp.alternative.statements)}')


    def test_function_literal_parsing(self):
        input = "fn(x, y) { x+y }"
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
        stmt = program.statements[0].expression
        self.assertTrue(isinstance(stmt, b1u3ast.FunctionLiteral), f'stmt.Expression is not ast.ExpressionStatement. got={type(stmt)}')
        self.assertEqual(len(stmt.parameters), 2, f'len(stmt.parameters) is not 2, got={len(stmt.parameters)}')
        self.help_test_literal_expression(stmt.parameters[0], 'x')
        self.help_test_literal_expression(stmt.parameters[1], 'y')
        self.assertEqual(len(stmt.body.statements), 1, f'len(stmt.body.statements) is not 1, got={len(stmt.body.statements)}')
        self.assertTrue(isinstance(stmt.body.statements[0], b1u3ast.ExpressionStatement), f'stmt.body.statements[0] is not ExpressionStatement instance, got={type(stmt.body.statements[0])}')
        self.help_test_infix_expression(stmt.body.statements[0].expression, 'x', '+', 'y')

    def test_function_parameter_parsing(self):
        tests = [
            ['fn() {};', []],
            ['fn(x) {};', ['x']],
            ['fn(x, y, z) {};', ['x', 'y', 'z']]
        ]
        for t in tests:
            l = b1u3token.Lexer(t[0])
            p = b1u3parser.Parser(l)
            program = p.parse_program()
            self.check_parser_errors(p)
            self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
            stmt = program.statements[0]
            self.assertTrue(isinstance(stmt, b1u3ast.ExpressionStatement), f'stmt is not ExpressionStatement')
            function = stmt.expression
            self.assertTrue(isinstance(function, b1u3ast.FunctionLiteral))
            self.assertEqual(len(function.parameters), len(t[1]), f'length parameter wrong, want {len(t[1])}, got={len(function.parameters)}')
            for i, tt in enumerate(t[1]):
                self.help_test_literal_expression(function.parameters[i], tt)

    def test_call_expression_parsing(self):
        input = "add(1, 2+3, 4*5);"
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
        stmt = program.statements[0].expression
        self.assertTrue(isinstance(stmt, b1u3ast.CallExpression), f'stmt.Expression is not ast.CallExpression. got={type(stmt)}')
        exp = stmt
        self.help_test_identifier(exp.function, 'add')
        self.assertEqual(len(exp.arguments), 3, f'wrong length of arguments. want=3, got={len(exp.arguments)}')
        self.help_test_literal_expression(exp.arguments[0], 1)
        self.help_test_infix_expression(exp.arguments[1], 2, '+', 3)
        self.help_test_infix_expression(exp.arguments[2], 4, '*', 5)

    def test_string_literal_expression(self):
        input = '"hello world";'
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
        stmt = program.statements[0].expression
        self.assertTrue(isinstance(stmt, b1u3ast.StringLiteral))
        self.assertEqual(stmt.value, "hello world")

    def test_parsing_array_literals(self):
        input = "[1, 2*2, 3 + 3]"
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
        stmt = program.statements[0]
        self.assertTrue(isinstance(stmt, b1u3ast.ExpressionStatement))
        exp = stmt.expression
        self.assertTrue(isinstance(exp, b1u3ast.ArrayLiteral), 'exp is not ArrayLiteral')
        self.assertEqual(len(exp.elements), 3, f"exp doesn't have 3 elements, got={len(exp.elements)}")
        self.help_test_integer_literal(exp.elements[0], 1)
        self.help_test_infix_expression(exp.elements[1], 2, '*', 2)
        self.help_test_infix_expression(exp.elements[2], 3, '+', 3)

    def test_parsing_index_expression(self):
        input = "myArray[1+1]"
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
        indexExp = program.statements[0].expression
        self.assertTrue(isinstance(indexExp, b1u3ast.IndexExpression))
        self.help_test_identifier(indexExp.left, "myArray")
        self.help_test_infix_expression(indexExp.index, 1, "+", 1)

    def test_parsing_hash_liteals(self):
        input = '{"one": 1, "two": 2, "three": 3}'
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')
        hashobj = program.statements[0].expression
        self.assertTrue(isinstance(hashobj, b1u3ast.HashLiteral))
        self.assertEqual(len(hashobj.pairs), 3, f'hashobj.pairs is not 3, got={len(hashobj.pairs)}')
        expected = {'one': 1, 'two': 2, 'three': 3}
        for k in hashobj.pairs:
            isinstance(k, b1u3ast.StringLiteral)
            expected_value = expected[repr(k)]
            self.help_test_integer_literal(hashobj.pairs[k], expected_value)

    def test_parsing_empty_hash_literal(self):
        input = '{}'
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements[0].expression.pairs), 0)
        self.assertEqual(len(program.statements), 1, f'p.statements does not contain 1 statements. got={len(program.statements)}')

    def test_parsing_hash_literals_with_expression(self):
        input = '{"one": 0 + 1, "two": 10 - 8, "three": 15/5}'
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1)
        hashobj = program.statements[0].expression
        tests = {
            "one": lambda x: self.help_test_infix_expression(x, 0, '+', 1),
            "two": lambda x: self.help_test_infix_expression(x, 10, '-', 8),
            "three": lambda x: self.help_test_infix_expression(x, 15, '/', 5)
        }
        for k in hashobj.pairs:
            tests[repr(k)](hashobj.pairs[k])

    def test_macro_literal_parsing(self):
        input = 'macro(x, y) { x + y; }'
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        self.check_parser_errors(p)
        self.assertEqual(len(program.statements), 1)
        exp = program.statements[0].expression
        self.assertTrue(isinstance(exp, b1u3ast.MacroLiteral))
        self.assertEqual(len(exp.parameters), 2, 'length of exp.parameters is not 2')
        self.help_test_literal_expression(exp.arguments[0], 'x')
        self.help_test_literal_expression(exp.arguments[0], 'y')
        self.assertEqual(len(macro.body.statements), 1)
        body_stmt = exp.body.statements[0]
        self.assertTrue(isinstance(body_stmt, b1u3ast.ExpressionStatement))
        self.help_test_infix_expression(body_stmt.expression, 'x' + 'y')
