cmake_minimum_required(VERSION 3.11)

project(PackageTest CXX)

find_package(ICU REQUIRED COMPONENTS io i18n uc data) # using CMake's FindICU
find_package(Threads REQUIRED)

add_executable(icuexample icuexample.cpp)
if(ICU_SHARED)
    target_link_libraries(
        icuexample
        PRIVATE
        ICU::i18n
    )
else()
    target_link_libraries(
        icuexample
        PRIVATE
        ICU::io
        ICU::i18n
        ICU::uc
        ICU::data
        Threads::Threads # necessary to avoid a std::system_error from std::call_once (https://gcc.gnu.org/bugzilla/show_bug.cgi?id=55394)
        ${CMAKE_DL_LIBS}
    )
endif()

enable_testing()

add_test(
    NAME icuexample
    COMMAND icuexample
)
