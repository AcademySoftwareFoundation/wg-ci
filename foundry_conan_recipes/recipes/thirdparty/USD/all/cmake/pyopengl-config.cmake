if (NOT Python_EXECUTABLE)
    message(WARNING "Skipping finding PyOpenGL since Python_EXECUTABLE is not defined")
    return()
endif()

execute_process(
    COMMAND "${Python_EXECUTABLE}" "-m" "pip" "install" "--target=${CMAKE_CURRENT_BINARY_DIR}/site-packages" "PyOpenGL==3.1.5"
    RESULT_VARIABLE installPyOpenGL
)
message("Ran ${Python_EXECUTABLE} -m pip install --target=${CMAKE_CURRENT_BINARY_DIR}/site-packages PyOpenGL=3.1.5; result was ${installPyOpenGL}")
if(NOT installPyOpenGL EQUAL 0)
    return()
endif()

execute_process(
    COMMAND "${Python_EXECUTABLE}" "-c" "import OpenGL"
    RESULT_VARIABLE pyOpenGLAvailable
)

message("Ran ${Python_EXECUTABLE} -c 'import OpenGL' to find PyOpenGL; result was ${pyOpenGLAvailable}")
if(NOT pyOpenGLAvailable EQUAL 0)
    message(FATAL_ERROR "PyOpenGL cannot be found, even though it was pip installed.")
endif()
