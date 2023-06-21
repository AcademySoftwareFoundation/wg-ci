# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake
import os

class GTestTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def imports(self):
        self.copy("*.dll", dst=".", src="bin")
        self.copy("*.dylib*", dst=".", src="lib")
        self.copy("*.so*", dst=".", src="lib")


    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["shared_gtest"] = self.options["GTest"].shared
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
