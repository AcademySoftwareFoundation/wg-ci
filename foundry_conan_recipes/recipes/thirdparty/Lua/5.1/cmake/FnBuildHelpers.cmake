include (CMakeParseArguments)

# Enable debug symbols or PDBs, even in release builds. Call this once, in your
# top-level CMakeLists.txt file.
function (FnEnableDebugSymbols)
    if (NOT MSVC)
        add_compile_options($<$<CONFIG:Release>:-g>)
    else ()
        # Compiler flags for PDB generation.
        add_compile_options($<$<CONFIG:Release>:-Zi>)

        # Linker flags for PDB generation.
        foreach (var CMAKE_SHARED_LINKER_FLAGS_RELEASE
                     CMAKE_EXE_LINKER_FLAGS_RELEASE
                     CMAKE_MODULE_LINKER_FLAGS_RELEASE)
            # We must re-enable /OPT:REF, as /DEBUG disables it.
            set("${var}" "${${var}} -DEBUG -OPT:REF" PARENT_SCOPE)
        endforeach ()
    endif ()
endfunction ()

# Sets up install rules for `target` such that its PDB files will be installed
# to the directory specified by DESTINATION. DESTINATION defaults to "bin" for
# RUNTIME targets, and "lib" otherwise.
#
# BUGS:
# - If using a custom OUTPUT_NAME, it needs to be set before calling this
#   function.
# - We don't examine the config-specific property variants (OUTPUT_NAME_DEBUG,
#   etc).
function (FnMSVCTargetInstallPDB target)
    if (NOT MSVC)
        return ()
    endif ()

    cmake_parse_arguments(args "" "DESTINATION" "" ${ARGN})
    get_target_property(output_name "${target}" OUTPUT_NAME)
    get_target_property(target_type "${target}" TYPE)

    if (args_DESTINATION)
        set(destination "${args_DESTINATION}")
    elseif (target_type MATCHES "SHARED_LIBRARY|EXECUTABLE")
        set(destination bin)
    else ()
        set(destination lib)
    endif ()

    # PDBs come in two flavours:
    # - PDBs produced by cl.exe when creating object files. CMake refers
    #   to them as 'compile PDB'. Enabled by the -Zi flag.
    # - PDBs produced by link.exe when creating an executable or DLL. CMake
    #   calls these simply 'PDBs'.
    #
    # The compiler-produced PDBs are only needed when distributing a static
    # library -- there's no linker step, hence no linker-produced PDBs.
    #
    # In CMake, we need to explicitly name the compile PDB, otherwise it gets
    # assigned by the compiler. (Something like vc100.pdb.)

    if (target_type MATCHES "SHARED_LIBRARY|MODULE_LIBRARY|EXECUTABLE")
        install(FILES "$<TARGET_PDB_FILE:${target}>"
            DESTINATION "${destination}"
        )
    elseif (target_type MATCHES "STATIC_LIBRARY")
        if (NOT output_name)
            set(output_name "${target}")
        endif ()

        get_target_property(compile_pdb_name "${target}" COMPILE_PDB_NAME)
        if (NOT compile_pdb_name)
            set_target_properties(${target} PROPERTIES
                COMPILE_PDB_NAME "${output_name}")
        endif ()

        get_target_property(compile_pdb_output_directory "${target}"
            COMPILE_PDB_OUTPUT_DIRECTORY)
        if (NOT compile_pdb_output_directory)
            set_target_properties(${target} PROPERTIES
                COMPILE_PDB_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}")
        endif ()

        string(CONCAT compile_pdb_path
            "$<TARGET_PROPERTY:${target},COMPILE_PDB_OUTPUT_DIRECTORY>"
            "/"
            "$<TARGET_PROPERTY:${target},PREFIX>"
            "$<TARGET_PROPERTY:${target},COMPILE_PDB_NAME>"
            ".pdb")
        install(FILES "${compile_pdb_path}" DESTINATION "${destination}")
    else ()
        message(FATAL_ERROR "Unsupported target type: ${target_type}")
    endif ()
endfunction ()
