# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools
from os import path


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_test_package_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        cmake.configure()
        cmake.build()

    def test(self):
        cmake = CMake(self)
        cmake.test(output_on_failure=True)
