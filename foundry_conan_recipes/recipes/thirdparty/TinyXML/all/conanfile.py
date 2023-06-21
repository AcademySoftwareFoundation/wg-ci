# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools


class TinyxXMLConan(ConanFile):
    name = "TinyXML"
    license = "Zlib"
    author = "Lee Thomason"
    url = "http://www.grinninglizard.com/tinyxml/"
    description = "TinyXML is a simple, small C++ XML parser that can be easily integrated into other programs."

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "*"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        cmake = CMake(self)
        
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        cmake.definitions["TINYXML_SOURCE_DIR"] = src_dir.replace('\\', '/')

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if "fPIC" in self.options:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        print(cmake.definitions)

        # CMakeLists.txt is not part of TinyXML source, so lives in source_folder.
        cmake.configure(source_folder=self.source_folder)

        cmake.build()

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"

        tokens = {}
        if is_windows:
            tokens["TINYXML_LIBNAME"] = "TinyXML"
        else:
            tokens["TINYXML_LIBNAME"] = "libTinyXML"

        if self.options.shared:
            tokens["TINYXML_LIBTYPE"] = "SHARED"
            tokens["TINYXML_LIBDIR"] = "bin" if is_windows else "lib"
            tokens["TINYXML_LIBEXT"] = ".dll" if is_windows else ".so" if is_linux else ".dylib"
        else:
            tokens["TINYXML_LIBTYPE"] = "STATIC"
            tokens["TINYXML_LIBDIR"] = "lib"
            tokens["TINYXML_LIBEXT"] = ".lib" if is_windows else ".a"

        src_path = os.path.join(self.source_folder, "cmake/TinyXMLConfig.cmake.in")
        with open(src_path, "r") as src_file:
            config_contents = src_file.read()

        dst_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)

        dst_path = os.path.join(dst_dir, "TinyXMLConfig.cmake")
        with open(dst_path, "wt") as dst_file:
            dst_file.write(config_contents.format(**tokens))

    def package(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        self._write_cmake_config_file()

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tinyxml"]
