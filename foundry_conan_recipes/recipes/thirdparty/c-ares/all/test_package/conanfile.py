# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake


class TestCAresConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_c-ares_test_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["shared_c-ares"] = self.options["c-ares"].shared
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
