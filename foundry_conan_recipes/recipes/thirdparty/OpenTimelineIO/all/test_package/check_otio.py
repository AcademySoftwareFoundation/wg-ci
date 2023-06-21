import sys

try:
    import opentimelineio as otio
except ImportError as exc:
    print("Error importing opentimelineio package: {}".format(exc))
    print("Using python executable: {}".format(sys.executable))
    print("With PYTHONPATH:")
    for i in sys.path:
        print("\t{}".format(i))
    sys.exit(1)

print("opentimelineio package found at {}".format(otio.__file__))
sys.exit(0)
