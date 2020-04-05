import b1u3ast, unittest



class ModifyTest(unittest.TestCase):
    def turn_one_into_two(self, node):
        if not isinstance(node, b1u3ast.IntegerLiteral):
            return node

        if node.value != 1:
            return node

        node.value = 2
        return node



    def test_m1(self):
        one = lambda: b1u3ast.IntegerLiteral(value=1)
        two = lambda: b1u3ast.IntegerLiteral(value=2)
        tests = [
                [one(), two()],
                [
                    b1u3ast.Program(statements=[
                        b1u3ast.ExpressionStatement(expression=one())
                    ]),
                    b1u3ast.Program(statements=[
                        b1u3ast.ExpressionStatement(expression=two())
                    ])
                ]
                ]
        for tt in tests:
            modified = b1u3ast.modify(tt[0], self.turn_one_into_two)
            if isinstance(tt[1], b1u3ast.Program):
                self.assertEqual(modified.statements[0].expression.value, tt[1].statements[0].expression.value)
            else:
                self.assertEqual(modified.value, tt[1].value)

    def test_m2(self):
        one = lambda: b1u3ast.IntegerLiteral(value=1)
        two = lambda: b1u3ast.IntegerLiteral(value=2)
        tests = [
                    [b1u3ast.InfixExpression(left=one(), right=two()), b1u3ast.InfixExpression(left=two(), right=two())],
                    [b1u3ast.PrefixExpression(operator='-', right=one()), b1u3ast.PrefixExpression(operator='-', right=two())],
                    [b1u3ast.IndexExpression(left=one(), index=one()), b1u3ast.IndexExpression(left=two(), index=two())],
                    [
                        b1u3ast.IfExpression(
                            condition=one(),
                            consequence=b1u3ast.BlockStatement(statements=[b1u3ast.ExpressionStatement(expression=one())]),
                            alternative=b1u3ast.BlockStatement(statements=[b1u3ast.ExpressionStatement(expression=one())])),
                        b1u3ast.IfExpression(
                            condition=two(),
                            consequence=b1u3ast.BlockStatement(statements=[b1u3ast.ExpressionStatement(expression=two())]),
                            alternative=b1u3ast.BlockStatement(statements=[b1u3ast.ExpressionStatement(expression=two())]))
                    ],
                    [b1u3ast.ReturnStatement(return_value=one()), b1u3ast.ReturnStatement(return_value=two())],
                    [b1u3ast.LetStatement(value=one()), b1u3ast.LetStatement(value=two())],
                    [b1u3ast.FunctionLiteral(parameters=[], body=b1u3ast.BlockStatement(statements=[b1u3ast.ExpressionStatement(expression=one())])),b1u3ast.FunctionLiteral(parameters=[], body=b1u3ast.BlockStatement(statements=[b1u3ast.ExpressionStatement(expression=two())]))],
                    [b1u3ast.ArrayLiteral(elements=[one(), one()]), b1u3ast.ArrayLiteral(elements=[two(), two()])],
                ]
        for tt in tests:
            modified = b1u3ast.modify(tt[0], self.turn_one_into_two)
            if isinstance(tt[1], b1u3ast.InfixExpression):
                self.assertEqual(modified.left.value, tt[1].right.value)
                self.assertEqual(modified.right.value, tt[1].right.value)
            elif isinstance(tt[1], b1u3ast.PrefixExpression):
                self.assertEqual(modified.right.value, tt[1].right.value)
            elif isinstance(tt[1], b1u3ast.IndexExpression):
                self.assertEqual(modified.left.value, tt[1].left.value)
                self.assertEqual(modified.index.value, tt[1].index.value)
            elif isinstance(tt[1], b1u3ast.IfExpression):
                self.assertEqual(modified.condition.value, tt[1].condition.value)
                self.assertEqual(modified.consequence.statements[0].expression.value,
                    tt[1].consequence.statements[0].expression.value)
                self.assertEqual(modified.alternative.statements[0].expression.value,
                    tt[1].alternative.statements[0].expression.value, 'alternative is not equal')
            elif isinstance(tt[1], b1u3ast.ReturnStatement):
                self.assertEqual(modified.return_value.value, tt[1].return_value.value)
            elif isinstance(tt[1], b1u3ast.LetStatement):
                self.assertEqual(modified.value.value, tt[1].value.value)
            elif isinstance(tt[1], b1u3ast.FunctionLiteral):
                self.assertEqual(modified.body.statements[0].expression.value, tt[1].body.statements[0].expression.value)
            elif isinstance(tt[1], b1u3ast.ArrayLiteral):
                self.assertEqual(modified.elements[0].value, tt[1].elements[0].value)
                self.assertEqual(modified.elements[1].value, tt[1].elements[1].value)
            else:
                self.assertEqual(modified.value, tt[1].value)

            hashLiteral = b1u3ast.HashLiteral(pairs={one(): one(), one(): one()})
            b1u3ast.modify(hashLiteral, self.turn_one_into_two)

            for k, v in hashLiteral.pairs.items():
                self.assertEqual(k.value, 2)
                self.assertEqual(v.value, 2)

