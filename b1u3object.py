# identify type as str
INTEGER_OBJ = 'INTEGER'
BOOLEAN_OBJ = 'BOOLEAN'
NULL_OBJ = 'NULL'
RETURN_VALUE_OBJ = 'RETURN_VALUE'
ERROR_OBJ = 'ERROR'
FUNCTION_OBJ = 'FUNCTION'
STRING_OBJ = 'STRING'
BUILTIN_OBJ = 'BUILTIN'
ARRAY_OBJ = 'ARRAY'
HASH_OBJ = 'HASH'
QUOTE_OBJ = 'QUOTE'
MACRO_OBJ = 'MACRO'

# Object Interface
class Object:
    def __init__(self,**kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def type(self) -> str:
        raise NotImplementedError()

    def inspect(self) -> str:
        raise NotImplementedError()

class Hashable:
    def hash_key(self):
        raise NotImplementedError()

class HashKey(Object):
    type=None
    value=None

    def __eq__(self, v):
        return self.value == v.value

    def __hash__(self):
        return self.value


class Integer(Object, Hashable):
    value:int=None

    def type(self):
        return INTEGER_OBJ

    def inspect(self):
        return f'{self.value}'

    def hash_key(self):
        return HashKey(type=self.type(), value=self.value)



class Boolean(Object, Hashable):
    value:bool=None

    def type(self):
        return BOOLEAN_OBJ

    def inspect(self):
        return f'{self.value}'.lower()

    def hash_key(self):
        value = None
        if self.value:
            value = 1
        else:
            value = 0
        return HashKey(type=self.type(), value=value)



class Null(Object):

    def type(self):
        return NULL_OBJ

    def inspect(self):
        return 'null'


class ReturnValue(Object):
    def type(self):
        return RETURN_VALUE_OBJ

    def inspect(self):
        return self.value.inspect()




class Error(Object):
    msg:str=None
    def type(self):
        return ERROR_OBJ

    def inspect(self):
        return f'ERROR: {self.msg}'


class Function(Object):
    parameters=None
    body=None
    env=None

    def type(self):
        return FUNCTION_OBJ

    def inspect(self):
        out = ""
        params = []
        for p in self.parameters:
            params.append(repr(p))
        out += "fn"
        out += "("
        out += ", ".join(params)
        out += ") {\n"
        out += repr(self.body)
        out += "\n}"
        return out

class Environment:
    store:dict=None
    outer=None

    def __init__(self, **kwargs):
        self.store=dict()
        self.outer=dict()
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError(f'Key is not type of str, got={type(key)}')
        try:
            return self.store[key]
        except KeyError:
            return self.outer[key]

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError(f'key is not type of str, got={type(key)}')
        self.store[key] = value


def new_enclosed_environment(outer):
    env=Environment()
    env.outer=outer
    return env


class String(Object, Hashable):
    value:str=None

    def type(self):
        return STRING_OBJ

    def inspect(self):
        return self.value

    def hash_key(self):
        return HashKey(type=self.type(), value=sum(list(self.value.encode())))



class Builtin(Object):
    fn=None

    def type(self):
        return BUILTIN_OBJ

    def inspect(self):
        return 'builtin function'


class Array(Object):
    elements=None

    def type(self):
        return ARRAY_OBJ

    def inspect(self):
        return f"[{', '.join([e.inspect() for e in self.elements])}]"


class HashPair(Object):
    key:Object=None
    value:Object=None


class Hash(Object):
    pairs=None

    def type(self):
        return HASH_OBJ

    def inspect(self):
        strs = []
        for p in self.pairs:
            strs.append(f'{p.key.inspect()}: {p.value.inspect()}')
        return '{'+f'{", ".join(strs)}'+'}'

class Quote(Object):
    node=None

    def type(self):
        return QUOTE_OBJ

    def inspect(self):
        return f"QUOTE({repr(self.node)})"


class Macro(Object):
    parameters=[]
    body=None
    env=None
    def type(self):
        return MACRO_OBJ

    def inspect(self):
        params = []
        for p in self.parameters:
            params.append(repr(p))
        return f'macro({", ".join(params)})'+'{\n'+f'{repr(self.body)}'+'\n}'

