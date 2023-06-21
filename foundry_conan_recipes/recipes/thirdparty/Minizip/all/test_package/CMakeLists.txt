cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(Minizip REQUIRED)

add_executable(test_minizip test_package.cpp)
target_link_libraries(test_minizip Minizip::Minizip)

enable_testing()
add_test(NAME test_minizip
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_minizip)
# Copy the test zip file..
file(COPY "testFile.zip"  DESTINATION ${CMAKE_BINARY_DIR})
