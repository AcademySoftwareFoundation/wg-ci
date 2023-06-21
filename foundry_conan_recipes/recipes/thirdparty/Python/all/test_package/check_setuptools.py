from __future__ import print_function
import sys

try:
    import setuptools
except ImportError:
    print("setuptools module not found")
    print("Using python executable: {}".format(sys.executable))
    print("With PYTHONPATH:")
    for i in sys.path:
        print("\t{}".format(i))
    sys.exit(1)

print("setuptools module found at {}".format(setuptools.__file__))
sys.exit(0)
