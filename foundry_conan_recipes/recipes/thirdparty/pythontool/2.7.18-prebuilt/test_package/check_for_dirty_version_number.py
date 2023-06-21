from __future__ import print_function
import sys

version = sys.version
if "dirty" in version:
    print("Python version is identified as dirty: '{}'".format(version))
    sys.exit(1)

print("Python version identifies as: '{}'".format(version))
sys.exit(0)
