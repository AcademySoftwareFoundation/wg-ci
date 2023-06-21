# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    requires = "OpenColorIO/2.1.2"
    generators = ["cmake_paths"]

    def configure(self):
        self.options["OpenColorIO"].python_version = 3.9
    
    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
