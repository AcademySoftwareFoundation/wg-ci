# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake
import os


class ImathTest(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake_paths"

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_ImathTest_INCLUDE"] = os.path.join(
            self.install_folder, "conan_paths.cmake")
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def test(self):
        cmake = self._configure_cmake()
        cmake.test(output_on_failure=True)
