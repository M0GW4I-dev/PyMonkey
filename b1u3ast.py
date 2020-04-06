from b1u3token import Token
from typing import List, Dict


class Node():
    __data = set()
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def token_literal(self):
        """ テストのためだけに実装されている AST ノードに関連づけられているトークンのリテラルを返す """
        raise NotImplementedError()

    def __str__(self):
        s = []
        for key in dir(self):
            if not key.startswith('__'):
                s.append(f'{key}: {getattr(self, key)}')
        s = ',\n'.join(s)
        return f'<{self.__class__.__name__}: {s}>'

    def __repr__(self):
        raise NotImplementedError()


class Statement(Node):
    def statement_node(self):
        raise NotImplementedError()


class Expression(Node):
    def expression_node(self):
        raise NotImplementedError()


class Program(Node):
    statements:[Statement] = []

    def token_literal(self):
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ''

    def __repr__(self):
        ret = ''
        for s in self.statements:
            ret += repr(s)
        return ret


class Identifier(Expression):
    token:Token=None # token.IDENT
    value:str=None


    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return self.value


class LetStatement(Statement):
    token:Token=None # token.LET
    name:Identifier=None # let の左辺
    value:Expression=None # let の右辺

    def statement_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return ' '.join([self.token_literal(), repr(self.name), '=', repr(self.value)])+';'


class ReturnStatement(Statement):
    token:Token=None # この文の最初のトークン。 文の判別用。
    return_value:Expression=None

    def statement_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return ' '.join([self.token_literal(), repr(self.return_value)])+';'


class ExpressionStatement(Statement):
    token:Token=None # この文の最初のトークン。 文の判別用。
    expression:Expression=None

    def statement_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return repr(self.expression)

class IntegerLiteral(Expression):
    token:Token=None
    value:int=None

    def token_literal(self):
        return self.token.literal

    def expression_node(self):
        pass

    def __repr__(self):
        return self.token.literal

class PrefixExpression(Expression):
    token:Token=None
    operator:str=None
    right:Expression=None

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        out = f'({self.operator}{repr(self.right)})'
        return out


class InfixExpression(Expression):
    token:Token=None # Operator token: For example, '+'
    left:Expression=None
    right:Expression=None
    Operator:str=None

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        out = f'({repr(self.left)} {self.operator} {repr(self.right)})'
        return out


class Boolean(Expression):
    token:Token=None
    value:bool=None

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return self.token.literal

class BlockStatement(Statement):
    token:Token=None
    statements:[Statement]=None

    def statement_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        ret = '{ '
        for s in self.statements:
            ret += repr(s)
        ret += ' }'
        return ret


class IfExpression(Expression):
    token:Token=None
    condition:Expression=None
    consequence:BlockStatement=None
    alternative:BlockStatement=None

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        ret = f'if {repr(self.condition)} {repr(self.consequence)}'
        if self.alternative:
            ret += f'else {repr(self.alternative)}'
        return ret

class FunctionLiteral(Expression):
    parameters=None
    body:BlockStatement=None
    env=None

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        out = ''
        params = list(map(lambda x:repr(x), self.parameters))
        out += self.token_literal()
        out += '('
        out += ", ".join(params)
        out += ') '
        out += repr(self.body)
        return out


class CallExpression(Expression):
    function:Expression=None
    arguments:[Expression]=None

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        out = ''
        out += repr(self.function)
        out += '('
        out += ", ".join(list(map(lambda x: repr(x), self.arguments)))
        out += ')'
        return out

class StringLiteral(Expression):
    token=None
    value:str=None
    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return self.token.literal

class ArrayLiteral(Expression):
    elements:List[Expression]=None
    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        s = [repr(i) for i in self.elements]
        return f"[ {', '.join(s)} ]"

class IndexExpression(Expression):
    left:Expression=None
    index:Expression=None

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return f'({repr(self.left)}[{repr(self.index)}])'

class HashLiteral(Expression):
    pairs:Dict[Expression, Expression]=None

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        pairs = []
        for k in self.pairs:
            pairs.append(repr(k)+":"+repr(self.pairs[k]))
        return "{"+f"{', '.join(pairs)}"+"}"


def modify(node, modifier):
    """ 再帰的にたどって、自身を更新していく """
    if isinstance(node, Program):
        for i, s in enumerate(node.statements):
            node.statements[i] = modify(s, modifier)
    elif isinstance(node, ExpressionStatement):
        node.expression = modify(node.expression, modifier)
    elif isinstance(node, InfixExpression):
        node.right = modify(node.right, modifier)
        node.left = modify(node.left, modifier)
    elif isinstance(node, PrefixExpression):
        node.right = modify(node.right, modifier)
    elif isinstance(node, IndexExpression):
        node.left = modify(node.left, modifier)
        node.index = modify(node.index, modifier)
    elif isinstance(node, IfExpression):
        node.condition = modify(node.condition, modifier)
        node.consequence = modify(node.consequence, modifier)
        if node.alternative is not None:
            node.alternative = modify(node.alternative, modifier)
    elif isinstance(node, BlockStatement):
        for i, s in enumerate(node.statements):
            node.statements[i] = modify(node.statements[i], modifier)
    elif isinstance(node, ReturnStatement):
        node.return_value = modify(node.return_value, modifier)
    elif isinstance(node, LetStatement):
        node.value = modify(node.value, modifier)
    elif isinstance(node, FunctionLiteral):
        for i, p in enumerate(node.parameters):
            node.parameters[i] = modify(node.parameters[i], modifier)
        node.body = modify(node.body, modifier)
    elif isinstance(node, ArrayLiteral):
        for i, e in enumerate(node.elements):
            node.elements[i] = modify(node.elements[i], modifier)
    elif isinstance(node, HashLiteral):
        new_pairs = {}
        for k, v in node.pairs.items():
            new_k = modify(k, modifier)
            new_v = modify(k, modifier)
            new_pairs[new_k] = new_v
        node.pairs = new_pairs
    return modifier(node)


class MacroLiteral(Expression):
    token=None
    parameters=[]
    body=[]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters=[]
        self.body=[]

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        s = []
        for p in self.parameters:
            s.append(repr(p))
        return f'{self.token_literal()}({", ".join(s)}){repr(self.body)}'

        
