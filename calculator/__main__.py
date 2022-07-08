import sys

from .calculator import calculate

print("Result:", calculate("".join(sys.argv[1:])))
