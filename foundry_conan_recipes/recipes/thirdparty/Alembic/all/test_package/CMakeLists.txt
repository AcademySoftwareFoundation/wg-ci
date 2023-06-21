cmake_minimum_required(VERSION 3.10.0)
project(PackageTest C CXX)

find_package(Alembic REQUIRED)

add_executable(test_alembic test_package.cpp)
target_link_libraries(test_alembic PRIVATE Alembic::Alembic)
target_compile_features(test_alembic PRIVATE cxx_std_14)

enable_testing()
add_test(
    NAME test_alembic
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND test_alembic
)
if (${shared_alembic})
    if (MSVC)
        set_tests_properties(test_alembic PROPERTIES ENVIRONMENT "PATH=${CONAN_ALEMBIC_ROOT}/lib;$ENV{PATH}")
    endif()
endif()

