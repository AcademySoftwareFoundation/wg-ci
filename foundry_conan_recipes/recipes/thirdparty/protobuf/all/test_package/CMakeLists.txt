cmake_minimum_required(VERSION 3.0)
project(PackageTest CXX)

# Note: using module mode here would require Protobuf_USE_STATIC_LIBS to identify a static library build, so config files are preferred
find_package(protobuf CONFIG REQUIRED)

add_executable(protobuf_example)
target_sources(
    protobuf_example
    PRIVATE
    example.cpp
    example.proto
)
target_include_directories(
    protobuf_example
    PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
)
target_link_libraries(
    protobuf_example
    PRIVATE
    protobuf::libprotobuf
)
target_compile_features(
    protobuf_example
    PRIVATE
    cxx_std_11 # surprised this is not in the config file (but is in the module)
)
protobuf_generate(TARGET protobuf_example)

enable_testing()
add_test(
    NAME protobuf_example
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND protobuf_example
)
if (shared_protobuf)
    if (WIN32)
        set_tests_properties(protobuf_example PROPERTIES ENVIRONMENT "PATH=${CONAN_PROTOBUF_ROOT}/bin;$ENV{PATH}")
    endif()
endif()
