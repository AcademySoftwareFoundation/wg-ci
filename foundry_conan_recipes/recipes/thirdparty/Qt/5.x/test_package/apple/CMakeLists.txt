# Just set it to something reasonable...
set(TEST_WORKING_DIRECTORY ${CMAKE_BINARY_DIR} PARENT_SCOPE)

find_program(DeploymentTools
    NAMES macdeployqt
    PATHS ${CONAN_QT_ROOT}/bin
    REQUIRED
)
