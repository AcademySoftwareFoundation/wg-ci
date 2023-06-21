cmake_minimum_required(VERSION 3.0.0)
project(TinyXMLPackageTest CXX)

find_package(TinyXML REQUIRED)

add_executable(test_tinyxml test_package.cpp)
target_link_libraries(test_tinyxml TinyXML::TinyXML)

# Raw string literals are used for XML string literals.
target_compile_features(test_tinyxml PUBLIC cxx_raw_string_literals)

enable_testing()
add_test(NAME test_tinyxml
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_tinyxml
)

if(shared_TinyXML)
    if(MSVC)
        set_tests_properties(test_tinyxml
            PROPERTIES
            ENVIRONMENT "PATH=${CONAN_TINYXML_ROOT}/bin;$ENV{PATH}")
    endif()
endif()
