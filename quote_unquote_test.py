import unittest
import b1u3token, b1u3parser, b1u3object, b1u3evaluator, unittest


class QuoteTest(unittest.TestCase):
    def test_quote(self):
        tests = [
            ["quote(5)", "5"],
            ["quote(8 + 3)", "(8 + 3)"],
            ["quote(foobar)", "foobar"],
            ["quote(foobar + hogehoge)", "(foobar + hogehoge)"]
        ]
        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            self.assertTrue(isinstance(evaluated, b1u3object.Quote))
            self.assertNotEqual(evaluated.node, None)
            self.assertEqual(repr(evaluated.node), tt[1])


    def help_test_eval(self, input:str):
        l = b1u3token.Lexer(input)
        p = b1u3parser.Parser(l)
        e = b1u3object.Environment()
        program = p.parse_program()
        return b1u3evaluator.b1u3eval(program, e)

    def test_quote_unquote(self):
        tests = [
            ["quote(unquote(4))", "4"],
            ["quote(unquote(4 + 4))", "8"],
            ["quote(8 + unquote(3 + 4))", "(8 + 7)"],
            ["quote(unquote(3 + 4) + 8)", "(7 + 8)"],
            ["quote(unquote(true))", "true"],
            ["quote(unquote(true == false))", "false"],
            ["quote(unquote(quote(4 + 5)))", "(4 + 5)"],
            ["let hoge = quote(4 + 4); quote(unquote(4 + 4) + unquote(hoge))", "(8 + (4 + 4))"]
        ]
        for tt in tests:
            evaluated = self.help_test_eval(tt[0])
            self.assertTrue(isinstance(evaluated, b1u3object.Quote))
            self.assertTrue(evaluated is not None)
            self.assertEqual(repr(evaluated.node), tt[1])

