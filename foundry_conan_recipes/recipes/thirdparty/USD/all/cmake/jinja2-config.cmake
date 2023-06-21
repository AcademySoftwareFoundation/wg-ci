# Jinja2 is used as a build dependency to generate code (e.g. pxr/base/gf/gfGenCode.py) and is invoked by the Python that CMake finds
# so this can be Python 2 or Python 3 from the Conan local cache, not the Python that Conan is invoked with
# Pip install Jinja2 to a new pip directory target. The Conan script will then invoke CMake with that on the PYTHONPATH.
# Jinja-v2.11.3 was the last version compatible with both Python 2 and 3 (https://pypi.org/project/Jinja2/)

if (NOT Python_EXECUTABLE)
    message(WARNING "Skipping finding Jinja2 since Python_EXECUTABLE is not defined")
    return()
endif()

execute_process(
    COMMAND "${Python_EXECUTABLE}" "-m" "pip" "install" "--target=${CMAKE_CURRENT_BINARY_DIR}/site-packages" "jinja2==2.11.3.post1"
    RESULT_VARIABLE installJinja
)
message("Ran ${Python_EXECUTABLE} -m pip install --target=${CMAKE_CURRENT_BINARY_DIR}/site-packages jinja2=2.11.3.post1; result was ${installJinja}")
if(NOT installJinja EQUAL 0)
    return()
endif()

execute_process(
    COMMAND "${Python_EXECUTABLE}" "-c" "import jinja2"
    RESULT_VARIABLE jinja2Available
)

message("Ran ${Python_EXECUTABLE} -c 'import jinja2' to find Jinja2; result was ${jinja2Available}")
if(NOT jinja2Available EQUAL 0)
    message(FATAL_ERROR "Jinja2 cannot be found, even though it was pip installed.")
endif()

set(JINJA2_FOUND True)
