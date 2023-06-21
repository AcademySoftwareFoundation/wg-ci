# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake

class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = [ "cmake_paths" ]

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(self.build_folder, "conan_paths.cmake")
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
