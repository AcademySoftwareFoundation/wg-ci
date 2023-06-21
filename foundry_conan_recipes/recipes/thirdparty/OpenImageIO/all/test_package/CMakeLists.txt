cmake_minimum_required(VERSION 3.20.0)
project(PackageTest CXX)

add_compile_definitions(${Boost_COMPILE_DEFINITIONS})

find_package(OpenImageIO REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_openimageio test_package.cpp)
target_link_libraries(test_openimageio OpenImageIO::OpenImageIO)

enable_testing()
add_test(NAME test_openimageio
         COMMAND test_openimageio)
if(WIN32)
  set_tests_properties(test_openimageio PROPERTIES ENVIRONMENT "PATH=${CONAN_BOOST_ROOT}/lib\;${CONAN_BOOST_ROOT}/bin\;${CONAN_OPENEXR_ROOT}/bin\;${CONAN_IMATH_ROOT}/bin\;${CONAN_LIBTIFF_ROOT}/lib\;${CONAN_LIBTIFF_ROOT}/bin")
  if(${shared_openimageio})
    set_tests_properties(test_openimageio PROPERTIES WORKING_DIRECTORY ${CONAN_OPENIMAGEIO_ROOT}/bin)
  endif()
endif()

