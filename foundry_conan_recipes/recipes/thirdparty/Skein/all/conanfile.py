# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import platform
from conans import ConanFile, CMake, tools

class SkeinConan(ConanFile):
    name = "Skein"
    license = "LicenceRef-BSD-3-Clause-Skein-1.1"
    url = "http://www.skein-hash.info/"
    author = "http://www.skein-hash.info/"
    description = "The Skein Hash Function Family: Fast, Secure, Simple, Flexible, Efficient. And it rhymes with \"rain.\""
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = { "shared": False, "fPIC": True }
    generators = "cmake_paths"
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
        git = tools.Git(folder=self._source_subfolder)
        version_data = self.conan_data["sources"][self.version]
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["CMAKE_PROJECT_Skein_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        # disable all RPATHs so that build machine paths do not appear in binaries
        cmake.definitions["CMAKE_SKIP_RPATH"] = "1"

        cmake.configure(
            source_folder=os.path.join(self.source_folder, self._source_subfolder)
        )
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
  
    def package_info(self):
        self.cpp_info.libs = [ "Skein" ] 
