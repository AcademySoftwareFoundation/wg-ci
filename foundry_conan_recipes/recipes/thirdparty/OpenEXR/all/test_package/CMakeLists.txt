cmake_minimum_required(VERSION 3.10)
project(OpenEXRTest)

message(STATUS "prefix path: ${CMAKE_PREFIX_PATH}")
message(STATUS "include path: ${CMAKE_PROJECT_OpenEXRTest_INCLUDE}")

find_package(OpenEXR REQUIRED)

enable_testing()

if(OpenEXR_VERSION_MAJOR LESS 3)
    add_executable(loadexr LoadEXR.cpp)
    target_compile_features(loadexr PRIVATE cxx_std_11)
    target_link_libraries(loadexr PRIVATE OpenEXR::IlmImf)

    add_test(
        NAME LoadEXR
        COMMAND loadexr ${CMAKE_CURRENT_SOURCE_DIR}/BrightRings.exr
    )
    set(new_path "${CONAN_OPENEXR_ROOT}/bin;$ENV{PATH}")
    string(REPLACE ";" "\\;" new_path "${new_path}")
    set_tests_properties(LoadEXR PROPERTIES ENVIRONMENT "PATH=${new_path}")

    add_executable(succfpredf SuccAndPred.cpp)
    target_compile_features(succfpredf PRIVATE cxx_std_11)
    target_link_libraries(succfpredf PRIVATE OpenEXR::Imath)

    add_test(
        NAME SuccAndPred
        COMMAND succfpredf
    )
    set_tests_properties(SuccAndPred PROPERTIES ENVIRONMENT "PATH=${new_path}")
else()
    find_package(Imath REQUIRED)
    add_executable(loadexr LoadEXR.cpp)
    target_compile_features(loadexr PRIVATE cxx_std_11)
    target_link_libraries(loadexr PRIVATE OpenEXR::OpenEXR)

    add_test(
        NAME LoadEXR
        COMMAND loadexr ${CMAKE_CURRENT_SOURCE_DIR}/BrightRings.exr
    )
    # TODO(kyle.hewitt) Assuming a single-config generator in the test_package should be safe?
    string(TOUPPER ${CMAKE_BUILD_TYPE} UPPER_BUILD_TYPE)
    get_target_property(imath_loc Imath::Imath IMPORTED_LOCATION_${UPPER_BUILD_TYPE})
    get_filename_component(imath_loc ${imath_loc} DIRECTORY)
    set(new_path "${CONAN_OPENEXR_ROOT}/bin;${imath_loc};$ENV{PATH}")
    string(REPLACE ";" "\\;" new_path "${new_path}")
    set_tests_properties(LoadEXR PROPERTIES ENVIRONMENT "PATH=${new_path}")
endif()
