cmake_minimum_required(VERSION 3.1)
project(ProjectTest CXX)

find_package(SQLCipher REQUIRED)
find_package(Threads REQUIRED)

add_executable(ProjectTest example.cpp)
target_link_libraries(ProjectTest
    PRIVATE
        SQLCipher::SQLCipher
        Threads::Threads
)

if (NOT MSVC)
    target_link_libraries(ProjectTest
        PRIVATE
            dl
    )
else ()
    target_link_libraries(ProjectTest
        PRIVATE
            crypt32 Ws2_32
    )
endif ()

enable_testing()
add_test(NAME ProjectTest
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND ProjectTest)
