cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

include(CheckSymbolExists)

find_package(SQLite REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

get_target_property(SQLite3_HDR_DIR SQLite::SQLite3 INTERFACE_INCLUDE_DIRECTORIES)

check_symbol_exists(sqlite3_column_table_name16 ${SQLite3_HDR_DIR}/sqlite3ext.h HAVE_SQLITE3_COLUMN_TABLE_NAME16)
if(NOT HAVE_SQLITE3_COLUMN_TABLE_NAME16)
    message(FATAL_ERROR "SQLite must have been built with 'SQLITE_ENABLE_COLUMN_METADATA' according to https://www.sqlite.org/compile.html#_options_to_enable_features_normally_turned_off to have the necessary features for Qt5.")
endif()

add_executable(test_sqlite example.cpp)
target_link_libraries(test_sqlite SQLite::SQLite3)

enable_testing()
add_test(NAME test_sqlite
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_sqlite)
if (${shared_sqlite} AND MSVC)
  set_tests_properties(test_sqlite PROPERTIES ENVIRONMENT "PATH=${CONAN_SQLITE_ROOT}/bin;$ENV{PATH}")
endif()
