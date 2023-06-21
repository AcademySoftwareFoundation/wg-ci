cmake_minimum_required(VERSION 3.0.0)
project(PackageTest CXX)

find_package(OpenNURBS REQUIRED NO_SYSTEM_ENVIRONMENT_PATH)

add_executable(test_OpenNURBS test_package.cpp)

target_compile_features(test_OpenNURBS PRIVATE cxx_std_14)

target_link_libraries(test_OpenNURBS
    OpenNURBS::OpenNURBS
    $<$<PLATFORM_ID:Linux>:uuid>
    $<$<PLATFORM_ID:Windows>:Shlwapi.lib>
)

enable_testing()
add_test(NAME test_OpenNURBS WORKING_DIRECTORY ${CMAKE_BINARY_DIR} COMMAND test_OpenNURBS)
