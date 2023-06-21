import common

import platform
from PySide2.QtCore import QSysInfo

cpu_arch = QSysInfo.currentCpuArchitecture()
expected_arch = platform.machine()

# remap on Windows
if expected_arch == "AMD64":
    expected_arch = "x86_64"

assert cpu_arch == expected_arch, 'Expected "{}" but got "{}"'.format(expected_arch, cpu_arch)
