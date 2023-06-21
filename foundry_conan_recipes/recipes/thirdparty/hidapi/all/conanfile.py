# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools


class HIDAPIConan(ConanFile):
    name = 'HIDAPI'
    author = 'Alan Ott'
    description = ('Multi-platform library which allows an application to interface with USB and '
                   'Bluetooth HID-Class devices')
    license = 'BSD-3-Clause'
    url = 'https://github.com/libusb/hidapi'
    revision_mode = 'scm'
    package_originator = 'External'
    package_exportable = True

    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': True, 'fPIC': True}

    settings = ['os', 'compiler', 'build_type', 'arch']
    generators = 'cmake_paths'

    @property
    def _checkout_subfolder(self):
        return f'{self.name}_src'

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._checkout_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def requirements(self):
        if self.settings.os == 'Linux':
            self.requires('Libusb/1.0.26')

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['CMAKE_PROJECT_hidapi_INCLUDE'] = os.path.join(
            self.install_folder, 'conan_paths.cmake')
        if self.settings.os == 'Linux':
            cmake.definitions['HIDAPI_WITH_LIBUSB'] = True
            cmake.definitions['HIDAPI_WITH_HIDRAW'] = False

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        if not self.options.shared:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'

        cmake.configure(source_folder=os.path.join(self.source_folder, self._checkout_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
