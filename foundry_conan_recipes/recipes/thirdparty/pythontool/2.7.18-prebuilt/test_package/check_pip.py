from __future__ import print_function
import os
import sys

try:
    import pip
except ImportError:
    print("pip module not found")
    print("Using python executable: {}".format(sys.executable))
    print("With PYTHONPATH:")
    for i in sys.path:
        print("\t{}".format(i))
    sys.exit(1)

if not os.path.commonprefix([sys.executable, pip.__file__]):
    print("pip module found does not share a common prefix with the interpreter")
    print("pip   : {}".format(pip.__file__))
    print("python: {}".format(sys.executable))
    print("With PYTHONPATH:")
    for i in sys.path:
        print("\t{}".format(i))
    sys.exit(1)

print("pip module found at {}".format(pip.__file__))
sys.exit(0)
