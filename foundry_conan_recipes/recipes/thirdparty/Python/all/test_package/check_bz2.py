from __future__ import print_function
import sys

try:
    import bz2
except ImportError:
    print("bz2 module not found")
    print("Using python executable: {}".format(sys.executable))
    print("With PYTHONPATH:")
    for i in sys.path:
        print("\t{}".format(i))
    sys.exit(1)

print("bz2 module found at {}".format(bz2.__file__))
sys.exit(0)
