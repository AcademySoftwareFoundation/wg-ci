# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools


class IcuTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["ICU_SHARED"] = "TRUE" if self.options["icu"].shared else "FALSE"
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)