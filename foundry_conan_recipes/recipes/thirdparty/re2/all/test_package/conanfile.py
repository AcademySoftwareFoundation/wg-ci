# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake


class TestRe2Conan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_re2_test_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["shared_re2"] = self.options["re2"].shared
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
