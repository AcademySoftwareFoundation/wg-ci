# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from os import path
import shutil
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
from jinja2 import Environment, FileSystemLoader
from semver import SemVer

class LibAlembicConan(ConanFile):
    name = "Alembic"
    license = "MIT"
    author = "Industrial Light & Magic"
    url = "https://github.com/alembic/alembic"
    description = "Alembic is an open framework for storing and sharing scene data that includes a C++ library, a file format, and client plugins and applications."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake_paths"
    exports_sources = "*.cmake.in"
    no_copy_source = True
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    requires = [
        "zlib/[~1.2.11]@thirdparty/development",
        "HDF5/[~1.8.7]@thirdparty/development",
    ]


    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "ALEMBIC_RUN_UNITTESTS" in os.environ


    def config_options(self):
        self.options["HDF5"].shared = False
        self.options["zlib"].shared = False

        if self.settings.os == 'Windows':
            del self.options.fPIC

    def requirements(self):
        if self.version == "1.7.10":
            self.requires("OpenEXR/2.4.2@thirdparty/development")
        elif self.version == "1.8.3":
            self.requires("OpenEXR/3.1.4@")
        else:
            raise ConanInvalidConfiguration(f"Version {self.version} of Alembic does not specify an OpenEXR reference")


    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])


    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_Alembic_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

        cmake.definitions["USE_HDF5"] = "ON"
        cmake.definitions["HDF5_NO_FIND_PACKAGE_CONFIG_FILE"] = "true" # Avoid badly constructed include paths
        cmake.definitions["ALEMBIC_DEBUG_WARNINGS_AS_ERRORS"] = "OFF" # Avoid deprecation warnings as per https://github.com/alembic/alembic/issues/309

        if self.options.shared:
            cmake.definitions["ALEMBIC_SHARED_LIBS"] = "ON"
        else:
            cmake.definitions["ALEMBIC_SHARED_LIBS"] = "OFF"
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake


    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

        if self._run_unit_tests:
            if self.settings.os == "Windows":
                # need to add the Alembic and OpenEXR bin paths for the unit tests to find the dll's
                paths = [os.path.join(os.path.join(self.build_folder, "lib"), "Alembic"),
                         self.deps_cpp_info["OpenEXR"].bin_paths[0]]
                os.environ['PATH'] += os.pathsep + os.pathsep.join(paths)
            cmake.build(target="test")


    def _write_cmake_config_file(self):
        p = path.join(self.package_folder, "cmake")
        if not path.exists(p):
            os.mkdir(p)

        ver = SemVer(self.version, False)
        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {
                "version_major": str(ver.major),
                "version_minor": str(ver.minor),
                "version_patch": str(ver.patch),
                "os": self.settings.os,
                "bt": self.settings.build_type,
                "shared": self.options.shared,
            }

            data["libsuffix"] = ".a"
            if tools.Version(self.version) < "1.8.3":
                data["openexr_libs"] = "OpenEXR::Imath;OpenEXR::IexMath;OpenEXR::IlmThread;OpenEXR::Iex;OpenEXR::Half"
            else:
                data["openexr_libs"] = "Imath::Imath;OpenEXR::OpenEXR"

            if self.options.shared:
                data["libsuffix"] = ".dylib" if self.settings.os == "Macos" else ".so"
            
            interpreter_template = env.get_template(file_name + ".in")
            interpreter_template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))
        
        _configure("AlembicConfig.cmake")
        _configure("AlembicConfigVersion.cmake")


    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self._write_cmake_config_file()

        lib_path = os.path.join(self.package_folder, "lib")

        # remove cmake folder (for the moment we want to provide our config file only)
        cmakefolder = os.path.join(lib_path, "cmake")
        if os.path.isdir(cmakefolder):
            shutil.rmtree(cmakefolder)

        if self.options.shared and self.settings.os == "Macos":
            lib_path = os.path.join(self.package_folder, "lib")
            bin_path = os.path.join(self.package_folder, "bin")

            # Make the dylib's relocatable
            dylib_path = os.path.join(lib_path, "libAlembic.{}.dylib".format(self.version))
            args = ["install_name_tool", "-id", "@rpath/libAlembic.dylib", dylib_path]
            self.run(" ".join(args))

            # Make the binaries relocatable
            major, minor, _ = self.version.split('.')
            dylib_path = "libAlembic.{}.{}.dylib".format(major, minor)
            package_binaries = os.listdir(bin_path)
            for binary in package_binaries:
                binary_path = os.path.join(bin_path, binary)
                args = ["install_name_tool", "-change", dylib_path, "@rpath/libAlembic.dylib", binary_path]
                self.run(" ".join(args))

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = ["libAlembic"]

