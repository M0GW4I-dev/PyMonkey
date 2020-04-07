import b1u3token, b1u3parser, b1u3object, b1u3evaluator, unittest

class EvaluatorTest(unittest.TestCase):
    def test_eval_integer_expression(self):
        tests = [
                ['5', 5],
                ['10', 10]
        ]
        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            self.help_test_integer_object(evaluated, tt[1])


    def help_test_eval(self, input:str):
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        e = b1u3object.Environment()
        program = p.parse_program()
        return b1u3evaluator.b1u3eval(program, e)


    def help_test_integer_object(self, obj, expected):
        self.assertTrue(isinstance(obj, b1u3object.Integer), f'object is not Integer. got={type(obj)}')
        self.assertEqual(obj.value, expected, f'obj.value is not {expected}, got={obj.value}')

    def test_eval_boolean_expression(self):
        tests = [
            ['true', True],
            ['false', False],
            ['1 < 2', True],
            ['3 > 5', False],
            ['1 == 1', True],
            ['1 != 1', False],
            ['1 == 2', False],
            ['1 != 2', True],
            ['true == true', True],
            ['true == false', False],
            ['false == true', False],
            ['false == false', True],
            ['true != true', False],
            ['true != false', True],
            ['false != true', True],
            ['false != false', False],
            ['(1 < 2) == true', True],
            ['(1 < 2) == false', False],
            ['(1 > 2) == true', False],
            ['(1 > 2) == false', True]
        ]

        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            self.help_test_boolean_object(evaluated, tt[1])

    def help_test_boolean_object(self, obj, expected):
        self.assertTrue(isinstance(obj, b1u3object.Boolean), f'object is not Boolean. got={type(obj)}')
        self.assertEqual(obj.value, expected, f'object has wrong value. got={obj.value}, want={expected}')

    def test_bang_operator(self):
        tests = [
            ['!true', False],
            ['!false', True],
            ['!5', False],
            ['!!true', True],
            ['!!false', False],
            ['!!5', True]
        ]

        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            self.help_test_boolean_object(evaluated, tt[1])

    def test_minus_operator(self):
        tests = [
            ['-5', -5],
            ['--5', 5],
            ['999', 999],
            ['-999', -999],
            ['5 + 5 + 5 + 5 -10', 10],
            ['2 * 2 * 2', 8],
            ['-50 + 100 - 50', 0],
            ['50 / 2 * 3', 75],
            ['2 * (5 + 10)', 30]
        ]

        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            self.help_test_integer_object(evaluated, tt[1])

    def test_if_else_expressions(self):
        tests = [
            ['if (true) { 10 }', 10],
            ['if (1) { 10 }', 10],
            ['if (1 < 2) { 100 }', 100],
            ['if (1 > 2) { 100 }', None],
            ['if (1 < 2) { 10 } else { 20 }', 10],
            ['if (1 > 2) { 10 } else { 20 }', 20]
        ]

        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            if tt[1] is None:
                self.help_test_null_object(evaluated)
            else:
                self.help_test_integer_object(evaluated, tt[1])

    def help_test_null_object(self, obj):
        self.assertEqual(b1u3evaluator.NULL, obj, f'obj is not NULL, got={type(obj)}')

    def test_return_statements(self):
        tests = [
            ['return 10;', 10],
            ['return 10; 9;', 10],
            ['return 2 * 5; 9;', 10],
            ['if (10 > 1) { if (10 > 1) { return 10; } } return 1;', 10]
        ]

        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            self.help_test_integer_object(evaluated, tt[1])

    def test_error_handling(self):
        tests = [
            ['5 + true;', 'type mismatch: INTEGER + BOOLEAN'],
            ['5 + true; 5;', 'type mismatch: INTEGER + BOOLEAN'],
            ['-true', 'unknown operator: -BOOLEAN'],
            ['true + false;', 'unknown operator: BOOLEAN + BOOLEAN'],
            ['5; true + false; 4;','unknown operator: BOOLEAN + BOOLEAN'],
            ['if (10 > 1) { true + false; }', 'unknown operator: BOOLEAN + BOOLEAN'],
            ["foobar", "identifier not found: foobar"],
            ['{"name": "Monkey"}[fn(x) { x }];', "unusable as hash key: FUNCTION"],
        ]

        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            self.assertTrue(isinstance(evaluated, b1u3object.Error), f'evaluated is not b1u3object.Error')
            self.assertEqual(evaluated.msg, tt[1], f'evaluated.msg is not {tt[1]}, got={evaluated.msg}')

    def test_let_statements(self):
        tests = [
            ["let a = 5; a;", 5],
            ["let a = 5 * 5; a;", 25],
            ["let a = 5; let b = a; b;", 5],
            ["let a = 5; let b = a; let c = a + b + 5; c;", 15]
        ]

        for tt in tests:
            self.help_test_integer_object(self.help_test_eval(tt[0]), tt[1])

    def test_function_object(self):
        input = "fn(x) { x + 2; }"
        evaluated = self.help_test_eval(input)
        self.assertTrue(isinstance(evaluated, b1u3object.Function))
        self.assertEqual(len(evaluated.parameters), 1)
        self.assertEqual(repr(evaluated.parameters[0]), "x", "parameter is not x, got={repr(evaluated.parameters[0])}")
        expected_body = "{ (x + 2) }"
        self.assertEqual(repr(evaluated.body), expected_body, f"evaluated.body is not {expected_body}, got={repr(evaluated.body)}")

    def test_function_application(self):
        tests = [
            ['let identity=fn(x) {x;};identity(10);', 10],
            ['let identity=fn(x) {return x;};identity(10);', 10],
            ['let double=fn(x) {return x*2;};double(5);', 10],
            ['let add=fn(x, y) {return x+y;};add(5,5);', 10],
            ['fn(x){x;}(5);5;', 5]
        ]

        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            self.help_test_integer_object(evaluated, tt[1])

    def test_string_literal(self):
        input = '"Hello World";'
        evaluated = self.help_test_eval(input)
        self.assertTrue(isinstance(evaluated, b1u3object.String))
        self.assertEqual(evaluated.value, "Hello World")

    def test_string_concatenate(self):
        input = '"Hello" + " " + "World!";'
        evaluated = self.help_test_eval(input)
        self.assertTrue(isinstance(evaluated, b1u3object.String))
        self.assertEqual(evaluated.value, "Hello World!")

    def test_builtin_function(self):
        tests = [
            ['len("");', 0],
            ['len("four");', 4],
            ['len("hello world")', 11],
            ['len(1)', "argument to `len` not supported, got INTEGER"],
            ['len("one", "two")', "wrong number of arguments. got=2, want=1"]
        ]
        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            if isinstance(tt[1], int):
                self.help_test_integer_object(evaluated, tt[1])
            elif isinstance(tt[1], str):
                self.assertTrue(isinstance(evaluated, b1u3object.Error), "evaluated is not Error object")
                self.assertEqual(evaluated.msg, tt[1], f'evaluated.msg is not {tt[1]}, got={evaluated.msg}')
            else:
                self.fail(f"type of evaluated is {type(evaluated)}")

    def test_array_literals(self):
        input = '[1, 2 * 2, 3 + 3]'
        evaluated = self.help_test_eval(input)
        self.assertTrue(isinstance(evaluated, b1u3object.Array))
        self.assertEqual(len(evaluated.elements), 3, f'evaluated.elements is not 3, got={len(evaluated.elements)}')
        self.help_test_integer_object(evaluated.elements[0], 1)
        self.help_test_integer_object(evaluated.elements[1], 4)
        self.help_test_integer_object(evaluated.elements[2], 6)

    def test_array_index_expressions(self):
        tests = [
            ["[1, 2, 3][0]", 1],
            ["[1, 2, 3][1]", 2],
            ["[1, 2, 3][2]", 3],
            ["let i = 0; [1][i];", 1],
            ["[1, 2, 3][1 + 1];", 3]
        ]
        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            self.help_test_integer_object(evaluated, tt[1])

    def test_hash_index_expressions(self):
        tests = [
            ['{"foo": 5}["foo"];', 5],
            ['{"foo": 5}["bar"];', None],
            ['let key = "foo"; {"foo": 5}[key]', 5]
        ]
        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            if tt[1]:
                self.help_test_integer_object(evaluated, tt[1])
            else:
                self.help_test_null_object(evaluated)

    def test_hash_literals(self):
        input = """
        let two = "two";
        {
                "one": 10 -9,
                two: 1 + 1,
                "thr"+ "ee": 6 / 2,
                4: 4,
                true: 5,
                false: 6
        }"""
        evaluated = self.help_test_eval(input)
        self.assertTrue(isinstance(evaluated, b1u3object.Hash), f"Eval didn't return Hash. got={type(evaluated)}")
        expected = {
                b1u3object.String(value="one").hash_key(): 1,
                b1u3object.String(value="two").hash_key(): 2,
                b1u3object.String(value="three").hash_key(): 3,
                b1u3object.Integer(value=4).hash_key(): 4,
                b1u3evaluator.TRUE.hash_key(): 5,
                b1u3evaluator.FALSE.hash_key(): 6
        }
        self.assertEqual(len(evaluated.pairs), len(expected), f"Hash has wrong num of pairs. got={len(evaluated.pairs)}")
        for expectedKey, expectedValue in expected.items():
            p = evaluated.pairs[expectedKey]
            self.help_test_integer_object(p.value, expectedValue)

    def test_defines_macro(self):
        input = """
        let number = 1;
        let function = fn(x, y) { x + y };
        let mymacro = macro(x, y) { x + y };
        """
        env = b1u3object.Environment()
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        program = p.parse_program()
        b1u3evaluator.define_macros(program, env)

        self.assertEqual(len(program.statements), 3, f'len(program.statements) is not 3, got={len(program.statements)}')
        env["number"]
        env["function"]
        obj = env["mymacro"]
        self.assertTrue(isinstance(obj, b1u3object.Macro))
        self.assertEqual(len(obj.parameters), 2)
        self.assertEqual(repr(obj.parameters[0]), 'x')
        self.assertEqual(repr(obj.parameters[1]), 'y')
        self.assertEqual(repr(obj.body), '(x + y)')


