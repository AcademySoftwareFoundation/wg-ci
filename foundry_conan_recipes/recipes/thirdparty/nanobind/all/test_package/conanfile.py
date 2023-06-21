# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class NanobindTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    requires = [
        "Python/3.9.10"
    ]

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_nanobindTest_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
