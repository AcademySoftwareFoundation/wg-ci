# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake


class StbTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)

        include_dir = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["CMAKE_PROJECT_StbTestPackage_INCLUDE"] = include_dir

        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
