import b1u3ast, b1u3object, b1u3token
from typing import List, Dict

TRUE = b1u3object.Boolean(value=True)
FALSE = b1u3object.Boolean(value=False)
NULL = b1u3object.Null()

def b1u3eval(node:b1u3ast.Node, env:Dict[str, b1u3object.Object]) -> b1u3object.Object:
    if isinstance(node, b1u3ast.Program):
        return eval_program(node.statements, env)
    elif isinstance(node, b1u3ast.ExpressionStatement):
        return b1u3eval(node.expression, env)
    elif isinstance(node, b1u3ast.IntegerLiteral):
        return b1u3object.Integer(value=node.value)
    elif isinstance(node, b1u3ast.Boolean):
        if node.value:
            return TRUE
        else:
            return FALSE
    elif isinstance(node, b1u3ast.PrefixExpression):
        # then already ast node has right expression
        right = b1u3eval(node.right, env)
        if is_error(right):
            return right
        return eval_prefix_expression(node.operator, right, env)
    elif isinstance(node, b1u3ast.InfixExpression):
        left = b1u3eval(node.left, env)
        if is_error(left):
            return left
        right = b1u3eval(node.right, env)
        if is_error(right):
            return right
        return eval_infix_expression(node.operator, left, right, env)
    elif isinstance(node, b1u3ast.BlockStatement):
        return eval_block_statement(node, env)
    elif isinstance(node, b1u3ast.IfExpression):
        return eval_if_expression(node, env)
    elif isinstance(node, b1u3ast.ReturnStatement):
        val = b1u3eval(node.return_value, env)
        if is_error(val):
            return val
        return b1u3object.ReturnValue(value=val)
    elif isinstance(node, b1u3ast.LetStatement):
        val = b1u3eval(node.value, env)
        if is_error(val):
            return val
        env[node.name.value] = val
    elif isinstance(node, b1u3ast.Identifier):
        return eval_identifier(node, env)
    elif isinstance(node, b1u3ast.FunctionLiteral):
        params = node.parameters
        body = node.body
        return b1u3object.Function(parameters=params, env=env, body=body)
    elif isinstance(node, b1u3ast.CallExpression):
        if node.function.token_literal() == "quote":
            return quote(node.arguments[0], env)
        function = b1u3eval(node.function, env)
        if is_error(function):
            return function
        args = eval_expressions(node.arguments, env)
        if len(args) == 1 and is_error(args[0]):
            return args[0]
        return apply_function(function, args)
    elif isinstance(node, b1u3ast.StringLiteral):
        return b1u3object.String(value=node.value)
    elif isinstance(node, b1u3ast.ArrayLiteral):
        elements = eval_expressions(node.elements, env)
        if len(elements) == 1 and is_error(elements[0]):
            return [0]
        return b1u3object.Array(elements=elements)
    elif isinstance(node, b1u3ast.IndexExpression):
        left = b1u3eval(node.left, env)
        if is_error(left):
            return left
        index = b1u3eval(node.index, env)
        if is_error(index):
            return index
        return eval_index_expression(left, index)
    elif isinstance(node, b1u3ast.HashLiteral):
        return eval_hash_literal(node, env)
    return NULL

def apply_function(fn, args):
    if isinstance(fn, b1u3object.Function):
        extended_env = extend_function_env(fn, args)
        evaluated = b1u3eval(fn.body, extended_env)
        return unwrap_return_value(evaluated)
    elif isinstance(fn, b1u3object.Builtin):
        return fn.fn(*args)
    else:
        return new_error(f"not a function: {fn.type()}")


def extend_function_env(fn, args):
    env = b1u3object.new_enclosed_environment(fn.env)
    for paramidx, param in enumerate(fn.parameters):
        env[param.value] = args[paramidx]
    return env


def unwrap_return_value(obj):
    if isinstance(obj, b1u3object.ReturnValue):
        return obj.value
    return obj



def eval_expressions(exps, env):
    res = []
    for e in exps:
        evaluated = b1u3eval(e, env)
        if is_error(evaluated):
            return b1u3object.Object(evaluated=evaluated)
        res.append(evaluated)
    return res

def eval_identifier(node: b1u3ast.Node, env:Dict[str, b1u3object.Object]):
    try:
        return env[node.value]
    except KeyError:
        return new_error(f"identifier not found: {node.value}")

def eval_prefix_expression(operator, right, env):
    if operator == '!':
        return eval_bang_operator_expression(right, env)
    elif operator == '-':
        return eval_minus_operator_expression(right, env)
    else:
        return new_error(f'unknown operator: {operator}{right.type()}')

def eval_minus_operator_expression(right, env):
    if right.type() != b1u3object.INTEGER_OBJ:
        return new_error(f'unknown operator: -{right.type()}')
    value = right.value
    return b1u3object.Integer(value=-value)

def eval_bang_operator_expression(right, env):
    if right == TRUE:
        return FALSE
    elif right == FALSE:
        return TRUE
    elif right == NULL:
        return TRUE
    else:
        return FALSE


def eval_program(stmts:List[b1u3ast.Statement], env) -> b1u3object.Object:
    res = b1u3object.Object()

    for statement in stmts:
        res = b1u3eval(statement, env)
        if isinstance(res, b1u3object.ReturnValue):
            return res.value
        elif isinstance(res, b1u3object.Error):
            return res
    return res


def eval_infix_expression(operator, left, right, env):
    if left.type() == b1u3object.INTEGER_OBJ and right.type() == b1u3object.INTEGER_OBJ:
        return eval_integer_infix_expression(operator, left, right, env)
    elif left.type() == b1u3object.STRING_OBJ and right.type() == b1u3object.STRING_OBJ:
        return eval_string_infix_expression(operator, left, right, env)
    elif operator == '==':
        return TRUE if left == right else FALSE
    elif operator == '!=':
        return TRUE if left != right else FALSE
    elif left.type() != right.type():
        return new_error(f"type mismatch: {left.type()} {operator} {right.type()}")
    else:
        return new_error(f"unknown operator: {left.type()} {operator} {right.type()}")


def eval_integer_infix_expression(operator, left, right, env):
    if operator == '+':
        return b1u3object.Integer(value=left.value+right.value)
    elif operator == '-':
        return b1u3object.Integer(value=left.value-right.value)
    elif operator == '*':
        return b1u3object.Integer(value=left.value*right.value)
    elif operator == '/':
        return b1u3object.Integer(value=left.value//right.value)
    elif operator == '<':
        return TRUE if left.value < right.value else FALSE
    elif operator == '>':
        return TRUE if left.value > right.value else FALSE
    elif operator == '==':
        return TRUE if left.value == right.value else FALSE
    elif operator == '!=':
        return TRUE if left.value != right.value else FALSE
    else:
        return new_error(f'unknown operator: {left.type()} {operator} {right.type()}')

def eval_if_expression(ie, env):
    condition = b1u3eval(ie.condition, env)
    if is_error(condition):
        return condition
    if is_truthy(condition):
        return b1u3eval(ie.consequence, env)
    elif ie.alternative is not None:
        return b1u3eval(ie.alternative, env)
    else:
        return NULL

def is_truthy(obj):
    if obj == NULL:
        return False
    elif obj == TRUE:
        return True
    elif obj == FALSE:
        return False
    else:
        return True


def eval_block_statement(block, env):
    res = None
    for s in block.statements:
        res = b1u3eval(s, env)
        if res is not None and (res.type() == b1u3object.RETURN_VALUE_OBJ or res.type() == b1u3object.ERROR_OBJ):
            return res
    return res


def new_error(msg:str):
    return b1u3object.Error(msg=msg)

def is_error(obj)->bool:
    if obj is not None:
        return obj.type() == b1u3object.ERROR_OBJ
    return False


def eval_string_infix_expression(operator, left, right, env):
    if operator == '+':
        return b1u3object.String(value=left.value+right.value)
    else:
        return new_error(f"unknown operator: {left.type()} {operator} {right.type()}")


def len_function(*args):
    if len(args) != 1:
        return new_error(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], b1u3object.String):
        return b1u3object.Integer(value=len(args[0].value))
    elif isinstance(args[0], b1u3object.Array):
        return b1u3object.Integer(value=len(args[0].elements))
    return new_error(f"argument to `len` not supported, got {args[0].type()}")

def first_function(*args):
    if len(args) != 1:
        return new_error(f"wrong number of arguments. got={len(args)}, want=1")
    if not isinstance(args[0], b1u3object.Array):
        return new_error(f"argument to `first` must be ARRAY, got {args[0].type()}")
    if len(args[0].Elements) > 0:
        return arr.elements[0]
    return NULL

def last_function(*args):
    if len(args) != 1:
        return new_error(f"wrong number of arguments. got={len(args)}, want=1")
    if not isinstance(args[0], b1u3object.Array):
        return new_error(f"argument to `first` must be ARRAY, got {args[0].type()}")
    if len(args[0].elements) > 0:
        return arr.elements[len(arr.elements)-1]
    return NULL

def rest_function(*args):
    if len(args) != 1:
        return new_error(f"wrong number of arguments. got={len(args)}, want=1")
    if args[0].type () != b1u3object.ARRAY_OBJ:
        return new_error(f"argument to `rest` must be ARRAY, got {args[0].type()}")
    if len(args[0].elements) > 0:
        new_elements = args[0].elements.copy()[1:len(args[0].elements)]
        return b1u3object.Array(elements=new_elements)
    return NULL

def push_function(*args):
    if len(args) != 2:
        return new_error(f"wrong number of arguments. got={len(args)}, want=2")
    if args[0].type() != b1u3object.ARRAY_OBJ:
        return new_error(f"argument to `push` must be ARRAY, got {args[0].type()}")
    arr = args[0]
    new_ele = arr.elements.copy()
    new_ele.append(args[1])
    return b1u3object.Array(elements=new_ele)


def puts_function(*args):
    for v in args:
        print(v.inspect())
    return NULL


builtins = {
        "len": b1u3object.Builtin(fn=len_function),
        "first": b1u3object.Builtin(fn=first_function),
        "last": b1u3object.Builtin(fn=last_function),
        "rest": b1u3object.Builtin(fn=rest_function),
        "push": b1u3object.Builtin(fn=push_function),
        "puts": b1u3object.Builtin(fn=puts_function)
}

def eval_identifier(node, env):
    try:
        return env[node.value]
    except KeyError:
        try:
            return builtins[node.value]
        except KeyError:
            return new_error("identifier not found: " + node.value)

def eval_index_expression(left, index):
    if left.type() == b1u3object.ARRAY_OBJ and index.type() == b1u3object.INTEGER_OBJ:
        return eval_array_index_expression(left, index)
    elif left.type() == b1u3object.HASH_OBJ:
        return eval_hash_index_expression(left, index)
    else:
        return new_error("index operator not supported {left.type()}")

def eval_array_index_expression(array, index):
    idx = index.value
    max = len(array.elements)-1
    if idx < 0 or idx > max:
        return NULL
    return array.elements[idx]

def eval_hash_index_expression(hashobj, index):
    if not isinstance(index, b1u3object.Hashable):
        return new_error(f"unusable as hash key: {index.type()}")
    pair = None
    try:
        pair = hashobj.pairs[index.hash_key()]
    except KeyError:
        return NULL
    return pair.value

def eval_hash_literal(node, env):
    pairs={}
    for keyNode, valueNode in node.pairs.items():
        key = b1u3eval(keyNode, env)
        if is_error(key):
            return key
        if not isinstance(key, b1u3object.Hashable):
            return new_error(f"unusable as hash key: {key.type()}")
        value = b1u3eval(valueNode, env)
        if is_error(value):
            return value
        hashed = key.hash_key()
        pairs[hashed] = b1u3object.HashPair(key=key, value=value)
    return b1u3object.Hash(pairs=pairs)

def quote(node, env):
    # この中で quote 内の unquote を処理する
    node = eval_unquote_calls(node, env)
    return b1u3object.Quote(node=node)

def extend_unquote(node, env):
    if not is_unquote_call(node):
        return node
    if not isinstance(node, b1u3ast.CallExpression):
        return node
    if len(node.argunments) != 1:
        return node
    unquoted = b1u3eval(node.arguments[0], env)
    return convert_object_to_ast(unquoted)

def convert_object_to_ast(obj):
    if isinstance(obj, b1u3object.Integer):
        t = b1u3token.Token(type=b1u3token.INT, literal=f'{obj.value}')
        return b1u3ast.IntegerLiteral(token=t, value=obj.value)
    elif isinstance(obj, b1u3object.Boolean):
        t = b1u3token.Token(type=b1u3token.TRUE if obj.value else b1u3token.FALSE, literal='true' if obj.value else 'false')
        return b1u3ast.Boolean(token=t, value=obj.value)
    elif isinstance(obj, b1u3object.Quote):
        return obj.node
    return None

def eval_unquote_calls(quoted, env):
    def extend_unquote(node):
        if not is_unquote_call(node):
            return node
        if not isinstance(node, b1u3ast.CallExpression):
            return node
        if len(node.arguments) != 1:
            return node
        unquoted = b1u3eval(node.arguments[0], env)
        return convert_object_to_ast(unquoted)
    return b1u3ast.modify(quoted, extend_unquote)


def is_unquote_call(node):
    if not isinstance(node, b1u3ast.CallExpression):
        return False
    return node.function.token_literal() == "unquote"

def define_macros(program, env):
    definitions = []
    for i, statement in enumerate(program.statements):
        if is_macro_definition(statement):
            add_macro(statement, env)
            definitions.append(i)
    for i in range(len(definitions)-1, -1, -1):
        definition_index = definitions[i]
        program.statements = program.statements[:definition_index]+program.statements[definition_index+1:]
    

def is_macro_definition(node):
    if not isinstance(node, b1u3ast.LetStatement):
        return False
    if not isinstance(node.value, b1u3ast.MacroLiteral):
        return False
    return True


def add_macro(stmt, env):
    macro_literal = stmt.value
    macro = b1u3object.Macro(parameters=macro_literal.parameters, env=env, body=macro_literal.body)
    env[stmt.name.value] = macro
    
def expand(node):
    if not isinstance(node, b1u3ast.CallExpression):
        return node
    macro, ok = is_macro_call(node, env)
    if not ok:
        return node
    args = quote_args(node)
    eval_env = extend_macro_env(macro, args)
    evaluated = b1u3eval(macro.body, eval_env)
    if not isinstance(evaluated, b1u3object.Quote):
        import sys
        print('we only support returning AST-nodes from macros', file=sys.stderr)
    return evaluated.node


def expand_macros(program, env):
    def expand(node):
        if not isinstance(node, b1u3ast.CallExpression):
            return node
        macro, ok = is_macro_call(node, env)
        if not ok:
            return node
        args = quote_args(node)
        eval_env = extend_macro_env(macro, args)
        evaluated = b1u3eval(macro.body, eval_env)
        if not isinstance(evaluated, b1u3object.Quote):
            import sys
            print('we only support returning AST-nodes from macros', file=sys.stderr)
            sys.exit()
        return evaluated.node
    return b1u3ast.modify(program, expand)


def is_macro_call(exp, env):
    identifier = exp.function
    if not isinstance(identifier, b1u3ast.Identifier):
        return None, False

    obj = None
    try:
        obj = env[identifier.value]
    except KeyError:
        return None, False
    if not isinstance(obj, b1u3object.Macro):
        return None, False
    return obj, True


def quote_args(exp):
    args = []
    for a in exp.arguments:
        args.append(b1u3object.Quote(node=a))
    return args

def extend_macro_env(macro, args):
    extended = b1u3object.new_enclosed_environment(macro.env)
    for i, param in enumerate(macro.parameters):
        extended[param.value] = args[i]
    return extended

