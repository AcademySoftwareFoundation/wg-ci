# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake
import os

class EigenTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)
        
        cmake.definitions["EIGEN_MPL2_ONLY"] = "1"
        cmake.definitions["CMAKE_PROJECT_TestPackage_INCLUDE"] = os.path.join(
            self.install_folder, "conan_paths.cmake")

        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
