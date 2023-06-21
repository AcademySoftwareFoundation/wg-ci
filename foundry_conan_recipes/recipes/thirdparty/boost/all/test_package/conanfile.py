# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake


class BoostTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

        self.output.info("Configuring CMake with Boost user-info:")
        cmake.definitions.update(self.deps_user_info["boost"].vars)

        if "Python" in self.deps_cpp_info.deps:
            cmake.definitions["PYTHON_VERSION"] = self.deps_cpp_info["Python"].version
        
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
