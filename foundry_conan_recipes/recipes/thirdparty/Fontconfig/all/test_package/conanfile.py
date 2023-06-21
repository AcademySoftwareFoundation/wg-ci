# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake

class TestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    generators = "cmake_paths"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(self.build_folder, "conan_paths.cmake")
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
