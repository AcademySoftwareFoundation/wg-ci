# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake

class TestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(self.build_folder, "conan_paths.cmake")
        # Include a test font, "Printed Circuit Board Regular" from
        #  http://www.publicdomainfiles.com/show_file.php?id=13949892922495.
        unescaped_path = path.join(self.source_folder, "test_font.ttf")
        cmake.definitions["CMAKE_EXAMPLE_FONT_FILE"] = unescaped_path.replace("\\", "\\\\") if self.settings.os == "Windows" else unescaped_path
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
