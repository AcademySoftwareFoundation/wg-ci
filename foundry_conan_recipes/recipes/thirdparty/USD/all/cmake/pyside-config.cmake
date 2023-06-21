if (NOT Python_EXECUTABLE)
    message(WARNING "Skipping finding PySide since Python_EXECUTABLE is not defined")
    return()
endif()

set(find_pyside_cmd [[
import os
import sys

if os.name == 'nt':
    if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
        import_paths = os.getenv('PATH', '')
        if import_paths is not None:
            for path in import_paths.split(os.pathsep):
                if os.path.exists(path) and path != '.':
                    os.add_dll_directory(path)
import PySide2
]])

execute_process(
    COMMAND "${Python_EXECUTABLE}" "-c" ${find_pyside_cmd}
    RESULT_VARIABLE pyside2Available
)

message("Ran ${Python_EXECUTABLE} -c ${find_pyside_cmd} to find PySide2; result was ${pyside2Available}")
if(NOT pyside2Available EQUAL 0)
    execute_process(
        COMMAND "${Python_EXECUTABLE}" "-c" "import os, sys; print('PYTHONPATH={}'.format(sys.path)); print('PATH={}'.format(os.environ['PATH']))"
    )
    message(FATAL_ERROR "PySide2 cannot be found, even though it was installed by Conan into the local cache at ${CONAN_PYSIDE2_ROOT}")
endif()

find_program(
    PYSIDEUICBINARY
    NAMES pyside2-uic python2-pyside2-uic pyside2-uic-2.7 uic
    HINTS ${CONAN_PYSIDE2_ROOT}/bin
    REQUIRED
    NO_DEFAULT_PATH
)
message(STATUS "Will invoke PySide2 uic using '${PYSIDEUICBINARY}'")
