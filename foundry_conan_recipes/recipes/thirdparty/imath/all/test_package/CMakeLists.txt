cmake_minimum_required(VERSION 3.10)
project(ImathTest)

message(STATUS "prefix path: ${CMAKE_PREFIX_PATH}")
message(STATUS "include path: ${CMAKE_PROJECT_ImathTest_INCLUDE}")

find_package(Imath REQUIRED)

add_executable(succfpredf SuccAndPred.cpp)
target_compile_features(succfpredf PRIVATE cxx_std_11)
target_link_libraries(succfpredf PRIVATE Imath::Imath)

add_executable(config Config.cpp)
target_compile_features(config PRIVATE cxx_std_11)
target_link_libraries(config PRIVATE Imath::ImathConfig)

add_executable(limits Limits.cpp)
target_compile_features(limits PRIVATE cxx_std_11)
target_link_libraries(limits PRIVATE Imath::Imath)

enable_testing()
add_test(
    NAME SuccAndPred
    COMMAND succfpredf
)
add_test(
    NAME Config
    COMMAND config
)
add_test(
    NAME Limits
    COMMAND limits
)
set(new_path "${CONAN_IMATH_ROOT}/bin;$ENV{PATH}")
string(REPLACE ";" "\\;" new_path "${new_path}")
set_tests_properties(SuccAndPred PROPERTIES ENVIRONMENT "PATH=${new_path}")
set_tests_properties(Config PROPERTIES ENVIRONMENT "PATH=${new_path}")
set_tests_properties(Limits PROPERTIES ENVIRONMENT "PATH=${new_path}")
