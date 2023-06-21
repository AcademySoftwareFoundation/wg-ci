# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake

class TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def build(self):
        cmake = CMake(self)

        cmake.definitions["CMAKE_PROJECT_TestPackage_INCLUDE"] = os.path.join(
            self.install_folder, "conan_paths.cmake")

        cmake.configure()
        cmake.build()
        cmake.install()

    def test(self):
        path = os.path.join(self.build_folder, 'CPackConfig.cmake')
        self.run( f'cpack --config {path}', cwd=self.build_folder )
        if not os.path.exists( os.path.join( self.build_folder, "package", "WixTest.msi" ) ):
            raise Exception("WIX installer package is missing")
