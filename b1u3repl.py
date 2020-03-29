from b1u3token import Lexer, EOF
from b1u3parser import Parser
from b1u3evaluator import b1u3eval
from b1u3object import Environment
PROMPT = '>> '


def start(inp, outp):
    env = Environment()
    while True:
        print(PROMPT, end='', flush=True)
        line = inp.readline()
        if not line:
            return
        lexer = Lexer(line)
        parser = Parser(lexer)
        program = parser.parse_program()
        if len(parser.errors) != 0:
            print_parser_errors(outp, parser.errors)
            continue
        evaluated = b1u3eval(program, env)
        if evaluated is not None:
            print(evaluated.inspect())


def print_parser_errors(out, errors):
    for _, msg in enumerate(errors):
        print(f'\t{msg}', file=out, flush=True)

