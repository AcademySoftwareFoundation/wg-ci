cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(QtJSON CONFIG REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_package
  test_package.cpp
)
target_link_libraries(test_package
  PRIVATE
    QtJSON::QtJSON
)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CONAN_QT_ROOT}/bin
         COMMAND test_package)
