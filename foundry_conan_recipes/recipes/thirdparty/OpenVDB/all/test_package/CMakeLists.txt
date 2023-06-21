cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(OpenVDB CONFIG REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_package test_package.cpp)

target_compile_definitions(test_package
    PRIVATE
        ${Boost_COMPILE_DEFINITIONS}
)

target_link_libraries(test_package
    PRIVATE
        OpenVDB::Dynamic
)

enable_testing()
add_test(NAME test_package
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_package)

if (${shared_openvdb})
  if (WIN32)
    set_tests_properties(test_package PROPERTIES ENVIRONMENT
      "PATH=${CONAN_BLOSC_ROOT}/bin\;${CONAN_IMATH_ROOT}/bin\;${CONAN_OPENEXR_ROOT}/bin\;${CONAN_TBB_ROOT}/bin\;${CONAN_OPENVDB_ROOT}/bin\;$ENV{PATH}")
  endif()
endif()
