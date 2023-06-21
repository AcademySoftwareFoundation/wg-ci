# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake

class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = ["cmake_paths"]

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(self.build_folder, "conan_paths.cmake")
        # Include a test font, "Fira Code" a cross-platform font from
        # https://github.com/tonsky/FiraCode.
        unescaped_path = path.join(self.source_folder, "FiraCode-Regular.ttf")
        cmake.definitions["CMAKE_EXAMPLE_FONT_FILE"] = unescaped_path.replace("\\", "\\\\") if self.settings.os == "Windows" else unescaped_path
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
