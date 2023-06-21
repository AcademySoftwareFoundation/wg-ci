cmake_minimum_required(VERSION 3.12)
project(PackageTest)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Vulkan CONFIG REQUIRED)

add_executable(vulkan-test vulkan-test.cpp)
target_link_libraries(
    vulkan-test
    PRIVATE
        Vulkan::Headers
        $<$<BOOL:${UNIX}>:${CMAKE_DL_LIBS}>
)

enable_testing()
add_test(
    NAME vulkan-test
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND vulkan-test
)

if( WIN32 )
    # Make libvulkan-1.dll accessible on build machines which doesn't have
    # latest GPU drivers (with Vulkan runtime) installed
    set_tests_properties( vulkan-test
        PROPERTIES
            ENVIRONMENT "PATH=$<TARGET_FILE_DIR:Vulkan::Vulkan>\\..\\Runtime\\x64\\;$ENV{PATH}"
    )
endif()
