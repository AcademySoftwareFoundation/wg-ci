cmake_minimum_required(VERSION 3.10)
project(robinmapTest CXX)

find_package(tsl-robin-map REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_robinmap readme_example.cpp)
target_link_libraries(test_robinmap
    PRIVATE
    tsl::robin_map
)

enable_testing()
add_test(NAME test_robinmap
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_robinmap)
