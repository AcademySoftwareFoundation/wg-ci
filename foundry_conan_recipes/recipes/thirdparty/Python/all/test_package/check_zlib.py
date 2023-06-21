from __future__ import print_function
import sys

try:
    import zlib
except ImportError:
    print("zlib module was not found")
    print("Using python executable: {}".format(sys.executable))
    for i in sys.path:
        print("\t{}".format(i))

    sys.exit(1)

print("zlib module found")
sys.exit(0)