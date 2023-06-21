set(TEST_WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin PARENT_SCOPE)

find_program(DeploymentTools
    NAMES windeployqt
    PATHS ${CONAN_QT_ROOT}/bin
    REQUIRED
)
