cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)
set(CMAKE_CXX_STANDARD 14)

find_package(LLVM REQUIRED)
# Nothing in the test package currently uses clang, but we check we can find it anyway.
find_package(Clang REQUIRED)

add_executable(test_llvm test_package.cpp)
target_include_directories(test_llvm SYSTEM PUBLIC "${LLVM_INCLUDE_DIRS}")
target_link_libraries(test_llvm LLVMSupport)

enable_testing()
add_test(
    NAME test_llvm
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_llvm
)
