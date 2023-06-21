# The readline library is GPL, so we cannot ship it
# Thus, ensure that Python's readline module is not included

from __future__ import print_function
import sys

try:
    import readline
except ImportError:
    # success when readline is not found
    sys.exit(0)

print("Unexpectedly found readline module")
print("Using python executable: {}".format(sys.executable))
print("With PYTHONPATH:")
for i in sys.path:
    print("\t{}".format(i))
print("readline module found at {}".format(readline.__file__))
sys.exit(1)
