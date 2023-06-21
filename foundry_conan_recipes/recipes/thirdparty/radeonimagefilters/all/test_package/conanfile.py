# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake


class TestPackage(ConanFile):
    settings = 'os', 'compiler', 'arch', 'build_type'
    generators = 'cmake_paths'

    def test(self):
        cmake = CMake(self)
        cmake.definitions['CMAKE_PROJECT_TestPackage_INCLUDE'] = os.path.join(
            self.install_folder, 'conan_paths.cmake')

        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
