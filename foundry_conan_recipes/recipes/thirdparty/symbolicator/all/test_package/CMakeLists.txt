cmake_minimum_required(VERSION 3.20)

project(TestPackage C)

find_package(Symbolicator REQUIRED)

set(CMAKE_BUILD_TYPE Debug)

add_executable(testapp)
target_sources(testapp PRIVATE main.c)

enable_testing()
# Run the testapp
add_test(NAME testapp COMMAND testapp)

# Symbolicate the testapp using symsorter in the unified_symbols format (-zz compresses)
add_test(NAME test_symsort COMMAND Symbolicator::symsorter -zz --output unified_symbols testapp)
