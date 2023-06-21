cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(FoundryGL)
find_package(USD REQUIRED CONFIGS pxrTargets.cmake)

add_executable(test_arch_threads example.cpp)
target_link_libraries(test_arch_threads arch)

enable_testing()

# environment variable to update per platform
if(WIN32)
  set(LIBENVNAME PATH)
elseif(UNIX AND NOT APPLE)
  set(LIBENVNAME LD_LIBRARY_PATH)
elseif(APPLE)
  set(LIBENVNAME DYLD_LIBRARY_PATH)
  set(FRAMEWORKENVNAME DYLD_FRAMEWORK_PATH)
endif()

# list of all the dependent dynamic library directories to append to environment
if(WIN32)
  list(APPEND SHARED_LIB_DIRS ${CONAN_TBB_ROOT}/bin)
else()
  list(APPEND SHARED_LIB_DIRS ${CONAN_TBB_ROOT}/lib)
endif()
if(shared_usd)
  list(APPEND SHARED_LIB_DIRS ${CONAN_USD_ROOT}/lib)
endif()
if(with_python_bindings)
  list(APPEND SHARED_LIB_DIRS ${CONAN_BOOST_ROOT}/lib)
  if(WIN32)
    list(APPEND SHARED_LIB_DIRS ${CONAN_PYTHON_ROOT})
  elseif(APPLE)
    list(APPEND SHARED_FRAMEWORK_DIRS ${CONAN_PYTHON_ROOT})
  elseif(UNIX)
    list(APPEND SHARED_LIB_DIRS ${CONAN_PYTHON_ROOT}/lib)
  endif()
endif()
if(with_imaging)
  if(WIN32)
    list(APPEND SHARED_LIB_DIRS ${CONAN_PYSIDE2_ROOT}/bin)  
    list(PREPEND SHARED_LIB_DIRS ${CONAN_QT_ROOT}/bin)
    list(APPEND SHARED_LIB_DIRS ${CONAN_USD_ROOT}/bin)
  elseif(UNIX AND NOT APPLE)
    list(APPEND SHARED_LIB_DIRS ${CONAN_PYSIDE2_ROOT}/lib)
    list(APPEND SHARED_LIB_DIRS ${CONAN_QT_ROOT}/lib)
    list(APPEND SHARED_LIB_DIRS ${CONAN_USD_ROOT}/lib)
  endif()
endif()
if(APPLE AND FOUNDRYGL_FOUND)
  list(APPEND SHARED_LIB_DIRS ${FOUNDRYGL_LIBRARY_DIR})
endif()
list(APPEND SHARED_LIB_DIRS $ENV{${LIBENVNAME}})
if(APPLE)
  list(APPEND SHARED_FRAMEWORK_DIRS $ENV{${FRAMEWORKENVNAME}})
endif()

# convert the list to a string
# the back slashes here are important
if(WIN32)
  list(JOIN SHARED_LIB_DIRS "\;" SHARED_LIB_DIRS_STR)
  file(TO_NATIVE_PATH "${SHARED_LIB_DIRS_STR}" SHARED_LIB_DIRS_STR)
else()
  list(JOIN SHARED_LIB_DIRS "\:" SHARED_LIB_DIRS_STR)
  if(APPLE)
    list(JOIN SHARED_FRAMEWORK_DIRS "\:" SHARED_FRAMEWORK_DIRS_STR)
  endif()
endif()

# bootstrap.py invocations use the --no-cache switch so that cached environment files are not written into the package root for upload to Artifactory

add_test(NAME test_arch_threads
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND test_arch_threads
)
if(APPLE)
  set_tests_properties(test_arch_threads PROPERTIES ENVIRONMENT "${LIBENVNAME}=${SHARED_LIB_DIRS_STR};${FRAMEWORKENVNAME}=${SHARED_FRAMEWORK_DIRS_STR}")
else()
  set_tests_properties(test_arch_threads PROPERTIES ENVIRONMENT "${LIBENVNAME}=${SHARED_LIB_DIRS_STR}")
endif()

add_test(NAME test_arch_threads_bootstrap
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND python ${CONAN_USD_ROOT}/bootstrap.py --no-cache ${CMAKE_BINARY_DIR}/test_arch_threads
)

add_test(NAME test_sdfdump
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND ${CONAN_USD_ROOT}/bin/sdfdump ${CONAN_USD_ROOT}/share/usd/tutorials/authoringProperties/HelloWorld.usda
)
if(APPLE)
  set_tests_properties(test_sdfdump PROPERTIES ENVIRONMENT "${LIBENVNAME}=${SHARED_LIB_DIRS_STR};${FRAMEWORKENVNAME}=${SHARED_FRAMEWORK_DIRS_STR}")
else()
  set_tests_properties(test_sdfdump PROPERTIES ENVIRONMENT "${LIBENVNAME}=${SHARED_LIB_DIRS_STR}")
endif()

add_test(NAME test_sdfdump_bootstrap
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
         COMMAND python ${CONAN_USD_ROOT}/bootstrap.py --no-cache  ${CONAN_USD_ROOT}/bin/sdfdump ${CONAN_USD_ROOT}/share/usd/tutorials/authoringProperties/HelloWorld.usda
)

if(with_python_bindings)
  # Configure file will replace @PXR_PY_PACKAGE_NAME@ with the one we specified.
  configure_file(${CMAKE_CURRENT_SOURCE_DIR}/check_usd.py.in ${CMAKE_BINARY_DIR}/check_usd.py)
  add_test(
    NAME test_usdpy
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND ${CONAN_PYTHON_INTERPRETER} -v -B ${CMAKE_BINARY_DIR}/check_usd.py
  )
  if(APPLE)
    set_tests_properties(test_usdpy PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${CONAN_USD_ROOT}/lib/python;${LIBENVNAME}=${SHARED_LIB_DIRS_STR};${FRAMEWORKENVNAME}=${SHARED_FRAMEWORK_DIRS_STR}")
  else()
    set_tests_properties(test_usdpy PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${CONAN_USD_ROOT}/lib/python;${LIBENVNAME}=${SHARED_LIB_DIRS_STR}")
  endif()

  if(test_openvdb)
    configure_file(${CMAKE_CURRENT_SOURCE_DIR}/check_plugins.py.in ${CMAKE_BINARY_DIR}/check_plugins.py)
    add_test(
      NAME test_hioOpenVDB_plugin
      WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
      COMMAND ${CONAN_PYTHON_INTERPRETER} -B ${CMAKE_BINARY_DIR}/check_plugins.py
    )
    if(WIN32)
      set(NEWENV "${CONAN_IMATH_ROOT}/bin\;${CONAN_OPENVDB_ROOT}/bin\;${CONAN_OPENEXR_ROOT}/bin\;${SHARED_LIB_DIRS_STR}")
    else()
      set(NEWENV "${CONAN_IMATH_ROOT}/lib\:${CONAN_OPENVDB_ROOT}/lib\:${CONAN_OPENEXR_ROOT}/lib\:${SHARED_LIB_DIRS_STR}")
    endif()
    if(APPLE)
      set_tests_properties(test_hioOpenVDB_plugin PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${CONAN_USD_ROOT}/lib/python;${LIBENVNAME}=${NEWENV};${FRAMEWORKENVNAME}=${SHARED_FRAMEWORK_DIRS_STR}")
    else()
      set_tests_properties(test_hioOpenVDB_plugin PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${CONAN_USD_ROOT}/lib/python;${LIBENVNAME}=${NEWENV}")
    endif()
  endif()

  add_test(
    NAME test_usdpy_bootstrap
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND python ${CONAN_USD_ROOT}/bootstrap.py --no-cache -p ${CMAKE_BINARY_DIR}/check_usd.py
  )

  add_test(
    NAME test_usdcat
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND ${CONAN_PYTHON_INTERPRETER} -v -B ${CONAN_USD_ROOT}/bin/usdcat ${CONAN_USD_ROOT}/share/usd/tutorials/authoringProperties/HelloWorld.usda
  )
  if(APPLE)
    set_tests_properties(test_usdcat PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${CONAN_USD_ROOT}/lib/python;${LIBENVNAME}=${SHARED_LIB_DIRS_STR};${FRAMEWORKENVNAME}=${SHARED_FRAMEWORK_DIRS_STR}")
  else()
    set_tests_properties(test_usdcat PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${CONAN_USD_ROOT}/lib/python;${LIBENVNAME}=${SHARED_LIB_DIRS_STR}")
  endif()

  add_test(
    NAME test_usdcat_bootstrap
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND python ${CONAN_USD_ROOT}/bootstrap.py --no-cache -p ${CONAN_USD_ROOT}/bin/usdcat ${CONAN_USD_ROOT}/share/usd/tutorials/authoringProperties/HelloWorld.usda
  )

  # Alembic files appear to be binary only, so don't really want to introduce any into the recipes.git repo
  # but USD has some in their source tree
  include(FetchContent)
  FetchContent_Declare(
    usd
    GIT_REPOSITORY git@a_gitlab_url:libraries/cpp/usd/fnusd.git
    GIT_TAG        090ef0d849ced875b3b99a15e454b69148ccd8e1 # v21.05 tag
    GIT_SHALLOW    TRUE
    GIT_PROGRESS   TRUE
    GIT_CONFIG
      core.longpaths=true
  )
  if(NOT usd_POPULATED)
    FetchContent_Populate(usd)
  endif()

  add_test(
    NAME test_usdcat_alembic_bootstrap
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND python ${CONAN_USD_ROOT}/bootstrap.py --no-cache -p ${CONAN_USD_ROOT}/bin/usdcat ${usd_SOURCE_DIR}/pxr/usd/plugin/usdAbc/testenv/testUsdAbcAlembicData/testasset.abc
  )

  # Disabled this test for FoundryGL builds due to python binary and RPATH package issues.
  if(with_imaging AND (NOT FOUNDRYGL_FOUND))
    #[[ commented out, because this fails on Windows in Release.
    add_test(
      NAME test_usdview
      WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
      COMMAND ${CONAN_PYTHON_INTERPRETER} -v -B ${CONAN_USD_ROOT}/bin/usdview -h
    )
    if(APPLE)
      set_tests_properties(test_usdview PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${CONAN_USD_ROOT}/lib/python:${CONAN_PYSIDE2_ROOT}/lib/python${CONAN_PYTHON_VERSION}/site-packages;${LIBENVNAME}=${SHARED_LIB_DIRS_STR};${FRAMEWORKENVNAME}=${SHARED_FRAMEWORK_DIRS_STR}")
    elseif(UNIX)
      set_tests_properties(test_usdview PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${CONAN_USD_ROOT}/lib/python:${CONAN_PYSIDE2_ROOT}/lib/python${CONAN_PYTHON_VERSION}/site-packages;${LIBENVNAME}=${SHARED_LIB_DIRS_STR}")
    else()
      set_tests_properties(test_usdview PROPERTIES ENVIRONMENT "PYHOME=${CONAN_PYHOME};PYTHONPATH=${CONAN_USD_ROOT}/lib/python\;${CONAN_PYSIDE2_ROOT}/lib/site-packages;${LIBENVNAME}=${SHARED_LIB_DIRS_STR};PXR_USD_WINDOWS_DLL_PATH=${SHARED_LIB_DIRS_STR}")
    endif()
    ]]

    add_test(
      NAME test_usdview_bootstrap
      WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
      COMMAND python ${CONAN_USD_ROOT}/bootstrap.py --no-cache -p ${CONAN_USD_ROOT}/bin/usdview -h
    )
  endif()
endif()
