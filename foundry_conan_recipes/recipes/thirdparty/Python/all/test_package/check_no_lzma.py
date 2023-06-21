# the lzma module has been removed temporarily while we do not have
# a build of the library
# this test to be removed once we have a build
# this is a valid test for Python2 since it has no lzma module

from __future__ import print_function
import sys

try:
    import lzma
except ImportError:
    # success when module is not found
    sys.exit(0)

print("Unexpectedly found lzma module")
print("Using python executable: {}".format(sys.executable))
print("With PYTHONPATH:")
for i in sys.path:
    print("\t{}".format(i))
print("lzma module found at {}".format(lzma.__file__))
sys.exit(1)

