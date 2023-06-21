import os
import subprocess
import sys

import common


def version_tuple(v):
    return tuple(map(int, (v.split("."))))

def get_test_args():
    path = sys.argv[1]
    vers = sys.argv[2]

    test_file = os.path.join(os.path.dirname(__file__), 'test.ui')

    if version_tuple(vers) >= version_tuple('5.15.2.1'):
        path = os.path.join(path, 'bin', 'uic')
        return [path, test_file]
    else:
        path = os.path.join(path, 'bin', 'pyside2-uic')
        return [sys.executable, path, test_file]

assert 0 == subprocess.check_call(get_test_args())
