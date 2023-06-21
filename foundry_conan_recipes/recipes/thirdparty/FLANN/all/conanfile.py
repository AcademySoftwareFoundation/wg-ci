# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class FLANNConan(ConanFile):
    name = "FLANN"
    settings = "os", "compiler", "build_type", "arch"
    description = "FLANN is a library for performing fast approximate nearest neighbour searches in high dimensional spaces."
    url = "https://github.com/flann-lib/flann"
    license = "BSD-3-Clause"
    author = "Marius Muja"
    generators = "cmake_paths"
    exports_sources = "FLANNConfig.cmake"
    no_copy_source = True
    package_originator = "External"
    package_exportable = True
    revision_mode = 'scm'
    options = {'fPIC': [True, False], "shared": [False]}
    default_options = {'fPIC': True, 'shared' : False}

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

    def _configure_cmake(self):
        cmake = CMake(self)
        checkout_folder = os.path.join(self.source_folder, self._source_subfolder)

        cmake.definitions["CMAKE_PROJECT_flann_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.definitions["BUILD_C_BINDINGS"] = "OFF"

        cmake.configure(source_folder=checkout_folder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(src="", pattern="FLANNConfig.cmake", dst="cmake")
