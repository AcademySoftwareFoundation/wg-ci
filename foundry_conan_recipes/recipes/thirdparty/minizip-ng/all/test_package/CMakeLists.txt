cmake_minimum_required(VERSION 3.0.0)
project(PackageTest LANGUAGES CXX)

if (minizip_compat)
    set(minizip_target minizip)
else ()
    set(minizip_target minizip-ng)
endif ()

find_package(${minizip_target} REQUIRED)

if (minizip_compat)
    add_executable(test_minizip test_package.cpp)
    target_link_libraries(test_minizip MINIZIP::${minizip_target})
endif ()

add_executable(test_minizip_zlib test_package_zlib.cpp)
target_link_libraries(test_minizip_zlib MINIZIP::${minizip_target})

enable_testing()

if (minizip_compat)
    add_test(NAME test_minizip
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
            COMMAND test_minizip)
    file(COPY "testFile.zip"  DESTINATION ${CMAKE_BINARY_DIR})
endif ()

add_test(NAME test_minizip_zlib
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_minizip_zlib)
