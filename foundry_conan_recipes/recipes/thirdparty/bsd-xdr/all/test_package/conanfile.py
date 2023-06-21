# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import tempfile

from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def build(self):
        pass

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = os.path.join(
            self.install_folder, "conan_paths.cmake")
        cmake.configure()
        cmake.build()
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = os.path.join(tmp_dir, 'data.bin')
            with tools.environment_append({'TEST_PACKAGE_TEMP_PATH': tmp_path}):
                cmake.test(output_on_failure=True)
