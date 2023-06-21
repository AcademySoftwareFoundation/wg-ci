from __future__ import print_function
import sys

try:
    import ssl
except ImportError:
    print("ssl module was not found")
    print("Using python executable: {}".format(sys.executable))
    for i in sys.path:
        print("\t{}".format(i))

    sys.exit(1)
print("ssl module found")

try:
    import hashlib
except ImportError:
    print("hashlib module was not found")
    print("Using python executable: {}".format(sys.executable))
    for i in sys.path:
        print("\t{}".format(i))

    sys.exit(1)
print("hashlib module found")


# Found both, all is good
sys.exit(0)