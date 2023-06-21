# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake


class TestPackageConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'
    generators = 'cmake_paths'

    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': True, 'fPIC': True}

    build_requires = ('ZeroMQ/4.3.3@thirdparty/development')

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        self.options['ZeroMQ'].shared = self.options.shared
        if self.settings.os != 'Windows':
            self.options['ZeroMQ'].fPIC = self.options.fPIC

    def build(self):
        pass

    def test(self):
        cmake = CMake(self)
        cmake.definitions['CMAKE_PROJECT_PackageTest_INCLUDE'] = \
            os.path.join(self.install_folder, 'conan_paths.cmake')
        cmake.definitions['shared_zeromq'] = self.options.shared
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
