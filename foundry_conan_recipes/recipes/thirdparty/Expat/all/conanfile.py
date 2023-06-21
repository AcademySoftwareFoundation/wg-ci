# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
from conans import ConanFile, tools, CMake

class ExpatConan(ConanFile):
    name = "Expat"
    license = "MIT"
    author = "James Clark"
    url = "https://libexpat.github.io/"
    description = "Expat, a stream-oriented XML parser library written in C"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True,False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    exports_sources = "*"
    no_copy_source = False
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _library_source_subfolder(self):
        return os.path.join(self._source_subfolder, "expat")

    @property
    def _library_version(self):
        # The library version (i.e the version suffix for libexpat) differs from the
        # package version, map one to the other
        if self.version == "2.2.0":
            return "1.6.2"
        else:
            raise ValueError("No known library version for package version: {}".format(self.version))

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
        if self.options.shared:
            cmake.definitions["BUILD_shared"] = "ON"
        else:
            cmake.definitions["BUILD_shared"] = "OFF"
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.build_type == "Debug" and self.settings.os == "Windows":
            cmake.definitions["CMAKE_DEBUG_POSTFIX"] = ""

        if self.options.shared and self.settings.os == "Macos":
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure(source_folder=os.path.join(self.source_folder, self._library_source_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        cmake.build(target="test")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        lib_path = os.path.join(self.package_folder, "lib")

        # remove pkgconfig folder
        pkgfolder = os.path.join(lib_path, "pkgconfig")
        if os.path.isdir(pkgfolder):
            shutil.rmtree(pkgfolder)

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = ["expat"]

        if not self.options.shared:
            self.cpp_info.defines = ["XML_STATIC"]

