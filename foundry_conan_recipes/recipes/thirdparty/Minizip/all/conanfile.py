# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, CMake

class Minizip(ConanFile):
    name = "Minizip"
    settings = "os", "arch", "compiler", "build_type"
    author = "Gilles Vollant"
    description = "An archive in ZIP format can contain several files "\
        "compressed with this method, while a .gz archive can containt only " \
        "one file. It is a very popular format, that is why I have written " \
        "a package for reading files compressed within a Zip archive."
    url = "http://www.winimage.com/zLibDll/minizip.html"
    license = "Zlib"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = {"fPIC": True, "shared": False }
    generators = "cmake_paths"
    revision_mode = "scm"
    package_originator = "External"
    package_exportable = True
    exports_sources = "*"

    requires = ["zlib/1.2.11@thirdparty/development"]

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _minizip_source_subfolder(self):
        # Minizip is in a sub folder of zlib
        return "/".join([self._source_subfolder, "contrib", "minizip"])

    def configure(self):
        self.options["zlib"].shared = False

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        tokens = {}
        tokens["Minizip_LIBTYPE"] = "STATIC"
        tokens["Minizip_LIBEXT"] = ".lib" if is_windows else ".a"
        lib_name = "libMinizip"
        if self.settings.build_type == "Debug":
            lib_name += "_d"
        tokens["Minizip_LIBNAME"] = lib_name
        config_in_path = os.path.join(self.source_folder, "MinizipConfig.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "MinizipConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_Minizip_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
        cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
        cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = \
                self.options.fPIC

        source_folder = os.path.join(self.source_folder,
            self._minizip_source_subfolder).replace("\\","/")
        #ensure it ends in a "/"
        source_folder = source_folder + "/"
        cmake.definitions["MINIZIP_SRC_PREFIX"] = source_folder
        cmake.configure()
        return cmake

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self._write_cmake_config_file()

    def package_info(self):
        self.cpp_info.libs = ["Minizip"]
