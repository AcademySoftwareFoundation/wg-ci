# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools
from jinja2 import Environment, FileSystemLoader

class Lz4Conan(ConanFile):
    name = 'liblz4'
    description = 'LZ4 is a lossless data compression algorithm that is focused on compression and decompression speed.'
    url = 'https://github.com/lz4/lz4/'
    license = 'BSD-2-Clause'
    author = 'Yann Collet'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    exports_sources = '*.cmake.in'
    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build(self):
        cmake = self._configure()
        cmake.build()

    def package(self):
        cmake = self._configure()
        cmake.install()

        self._write_cmake_config_file()

    def _configure(self):
        cmake = CMake(self)

        cmake.definitions['BUILD_SHARED_LIBS'] = 'ON' if self.options.shared else 'OFF'
        cmake.definitions['BUILD_STATIC_LIBS'] = 'OFF' if self.options.shared else 'ON'

        cmake.definitions['LZ4_BUILD_CLI'] = 'OFF'
        cmake.definitions['LZ4_BUILD_LEGACY_LZ4C'] = 'OFF'

        if not self.options.shared:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'

        cmake.configure(source_folder=os.path.join(self.build_folder, self._source_subfolder, 'build', 'cmake'))

        return cmake

    def _write_cmake_config_file(self):
        if not os.path.exists(os.path.join(self.package_folder, 'cmake')):
            os.makedirs(os.path.join(self.package_folder, 'cmake'))

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {
                'libprefix': '' if self.settings.os == 'Windows' else 'lib',
                'libsuffix': 'lib' if self.settings.os == 'Windows' else 'a',
                'os': self.settings.os,
                'shared': self.options.shared
            }

            if self.options.shared:
                data['libsuffix'] = '.dylib' if self.settings.os == 'Macos' else '.so'

            interpreter_template = env.get_template(file_name + '.in')
            interpreter_template.stream(data).dump(os.path.join(self.package_folder, 'cmake', file_name))

        _configure('LZ4Config.cmake')

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'        
