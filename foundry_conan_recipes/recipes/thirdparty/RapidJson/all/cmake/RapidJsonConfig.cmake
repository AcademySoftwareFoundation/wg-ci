if(TARGET RapidJson::RapidJson)
    return()
endif()

get_filename_component(_rapidjson_install_prefix "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
message(STATUS "Found RapidJson: ${_rapidjson_install_prefix}.")

add_library(RapidJson::RapidJson INTERFACE IMPORTED)

set_target_properties(RapidJson::RapidJson
    PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${CONAN_RAPIDJSON_ROOT}/include"
)
