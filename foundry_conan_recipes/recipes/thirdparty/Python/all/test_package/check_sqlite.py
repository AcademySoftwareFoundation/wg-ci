from __future__ import print_function
import sys

try:
    import sqlite3
except ImportError:
    print("sqlite3 module was not found")
    print("Using python executable: {}".format(sys.executable))
    for i in sys.path:
        print("\t{}".format(i))

    sys.exit(1)

print("sqlite3 module found at {}".format(sqlite3.__file__))
sys.exit(0)