import b1u3ast, unittest




class TestModify(unittest.TestCase):
    def tmp(self, node):
        self.assertTrue(isinstance(node, b1u3object.IntegerLiteral))


    def test_m1(self):
        one = lambda: b1u3ast.IntegerLiteral(value=1)
        two = lambda: b1u3ast.IntegerLiteral(value=2)
        turn_one_into_two = lambda node:




