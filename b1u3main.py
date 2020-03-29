import b1u3repl
import getpass
import sys

def main():
    user = getpass.getuser()
    print(f'Hello {user}! This is the Monkey programming language')
    print('Feel free to type in commands')
    b1u3repl.start(sys.stdin, sys.stdout)


if __name__ == '__main__':
    main()

