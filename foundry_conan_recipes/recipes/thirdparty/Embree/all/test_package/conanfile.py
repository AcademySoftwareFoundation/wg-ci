# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class EmbreeTestConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'
    generators = 'cmake_paths'

    def imports(self):
        # Import TBB.
        self.copy('*.dll', '', 'bin')
        self.copy('*.dylib', '', 'lib')
        self.copy('*.so*', '', 'lib')

    def test(self):
        cmake = CMake(self)

        cmake.definitions['EMBREE_VERSION'] = tools.Version(self.deps_cpp_info['embree'].version)
        cmake.definitions['CMAKE_PROJECT_TestPackage_INCLUDE'] = os.path.join(
            self.install_folder, 'conan_paths.cmake')

        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
