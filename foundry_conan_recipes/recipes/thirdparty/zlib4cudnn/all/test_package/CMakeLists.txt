cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 14)

add_executable(test_zlib test_package.cpp)
target_compile_definitions(test_zlib PRIVATE -DLIBRARY_TO_LOAD=${ZLIB_LOADABLE_LIBRARY})
if(UNIX)
  target_link_libraries(test_zlib PRIVATE ${CMAKE_DL_LIBS})
endif()

enable_testing()
add_test(NAME test_zlib
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_zlib)
