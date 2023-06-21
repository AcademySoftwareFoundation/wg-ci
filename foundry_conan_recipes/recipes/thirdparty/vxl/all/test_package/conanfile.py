# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake
import os

class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = [ "cmake_paths" ]

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = os.path.join(self.build_folder, "conan_paths.cmake")
        cmake.definitions["shared_vxllib"] = self.options["VXL"].shared
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
