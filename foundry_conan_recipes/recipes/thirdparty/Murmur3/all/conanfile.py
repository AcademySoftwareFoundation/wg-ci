# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools
import os

class Murmur3Conan(ConanFile):
    name = "Murmur3"
    settings = "os", "compiler", "build_type", "arch"
    description = "Murmur3 is a non-cryptographic hash, designed to be fast and excellent-quality for making things like hash tables or bloom filters."
    url = "https://github.com/PeterScott/murmur3"
    license = "LicenceRef-Public-Domain-Murmur3-Scott"
    generators = "cmake_paths"
    author = "Peter Scott, based on Austin Appleby's C++ library"
    revision_mode = "scm"
    package_originator = "External"
    package_exportable = True
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {"shared": True, "fPIC": True}

    exports_sources = "*"

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_Murmur3_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        cmake.definitions['MURMUR3_VERSION'] = self.version

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

    def package_info(self):
       self.cpp_info.libs = tools.collect_libs(self)
