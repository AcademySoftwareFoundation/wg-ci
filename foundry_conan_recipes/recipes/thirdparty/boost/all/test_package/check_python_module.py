import os
import sys
# Since Python 3.8 Non system paths added to the dll directories by default,
# including any additional directories on the PATH envvar. Full notes:
#
# `DLL dependencies for extension modules and DLLs loaded with ctypes on Windows
# are now resolved more securely. Only the system paths, the directory containing
# the DLL or PYD file, and directories added with add_dll_directory() are searched
# for load-time dependencies. Specifically, PATH and the current working directory
# are no longer used, and modifications to these will no longer have any effect on
# normal DLL resolution. If your application relies on these mechanisms, you
# should check for add_dll_directory() and if it exists, use it to add your DLLs
# directory while loading your library. Note that Windows 7 users will need to
# ensure that Windows Update KB2533623 has been installed (this is also verified
# by the installer). (Contributed by Steve Dower in bpo-36085.).`
v = sys.version_info
if os.name == "nt" and ((v.major == 3 and v.minor >= 8) or v.major > 4):
    [os.add_dll_directory(os.path.abspath(dir)) for dir in os.environ["PATH"].split(os.pathsep) if os.path.isdir(dir)]
import greetings
assert greetings.hello() == "Hello, World!"