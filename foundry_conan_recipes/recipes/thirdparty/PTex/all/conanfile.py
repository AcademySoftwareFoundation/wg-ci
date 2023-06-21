# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, CMake
from conans.model.version import Version

class PtexConan(ConanFile):
    name = "PTex"
    license = "BSD-3-Clause"
    author = "Walt Disney Animation Studios"
    url = "https://ptex.us/"
    description = "Ptex is a texture mapping system developed by Walt Disney Animation Studios for production-quality rendering:"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    generators = "cmake_paths"
    exports_sources = "*"
    no_copy_source = True
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    requires = ["zlib/1.2.11@thirdparty/development"]

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _library_name(self):
        suffix = "" if self.options.shared else "_static"
        libname = "Ptex" if self.settings.os == "Windows" else "libPtex"
        library = "{}{}".format(libname , suffix)
        return library

    @property
    def _cmake_project_name(self):
        return "Ptex" if Version(self.version) >= Version("2.3.2") else "ptex"

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)

        # Ptex started needing a definition for its version
        if Version(self.version) >= Version("2.3.2"):
            cmake.definitions["PTEX_VER"] = self.version
        
        # From 2.4.1 we must use PTEX_BUILD_STATIC_LIBS/PTEX_BUILD_SHARED_LIBS to choose which library type
        # to build to prevent library name collisions
        if Version(self.version) >= Version("2.4.1"):
            cmake.definitions["PTEX_BUILD_STATIC_LIBS"] = "OFF" if self.options.shared else "ON"
            cmake.definitions["PTEX_BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"

        cmake.definitions["CMAKE_PROJECT_{}_INCLUDE".format(self._cmake_project_name)] = os.path.join(self.install_folder, "conan_paths.cmake")

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        if self.options.shared and self.settings.os == "Macos":
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"

        # needed as otherwise release type defaults to release
        os.environ["FLAVOR"] = "" if self.settings.build_type == "Release" else "debug"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"
        tokens = {}
        if self.options.shared:
            tokens["PTEX_LIBTYPE"] = "SHARED"
            tokens["PTEX_LIBEXT"] = ".dll" if is_windows else ".so" if is_linux else ".dylib"
        else:
            tokens["PTEX_LIBTYPE"] = "STATIC"
            tokens["PTEX_LIBEXT"] = ".lib" if is_windows else ".a"

        tokens["PTEX_LIBNAME"] = self._library_name

        config_in_path = os.path.join(self.source_folder, "PTexConfig.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "PTexConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        if self.options.shared:
            # both static and dynamic libs are built, but we only want dynamic
            lib_path = os.path.join(self.package_folder, "lib")
            ext = ".lib" if self.settings.os == "Windows" else ".a"
            staticlib_path = os.path.join(lib_path, "{}_static{}".format(self._library_name, ext))

            if os.path.isfile(staticlib_path):
                os.unlink(staticlib_path)

        self._write_cmake_config_file()

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = ["PTex"]

        if not self.options.shared:
            self.cpp_info.defines = ["PTEX_STATIC"]

