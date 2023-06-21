cmake_minimum_required(VERSION 3.1)
project(abseilTest CXX)

find_package(absl REQUIRED)

add_executable(abseilTest abseilTest.cpp)
target_link_libraries(abseilTest
    PRIVATE
    absl::flat_hash_map
    absl::numeric
)

enable_testing()
add_test(NAME abseilTest
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND abseilTest)
