from __future__ import print_function
import sys

try:
    import PyOpenColorIO
except ImportError:
    print("PyOpenColorIO module not found")
    print("Using python executable: {}".format(sys.executable))
    print("With PYTHONPATH:")
    for i in sys.path:
        print("\t{}".format(i))
    sys.exit(1)

print("bz2 module found at {}".format(PyOpenColorIO.__file__))
sys.exit(0)