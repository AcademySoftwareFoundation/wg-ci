import common

import sys
expected_version = sys.argv[1]

import PySide2
assert PySide2.__version__== expected_version, "expected version {} got version {}".format(expected_version, PySide2.__version__)

import shiboken2
assert shiboken2.__version__== expected_version, "expected version {} got version {}".format(expected_version, shiboken2.__version__)
