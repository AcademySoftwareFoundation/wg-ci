# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools, CMake
from jinja2 import Environment, FileSystemLoader


class OpenHMDConan(ConanFile):
    name = 'OpenHMD'
    license = 'BSL-1.0'
    author = 'OpenHMD Developers'
    description = 'Free and Open Source API and drivers for immersive technology.'
    url = 'https://github.com/OpenHMD/OpenHMD'

    settings = 'os', 'arch', 'compiler', 'build_type'

    generators = 'cmake_paths'

    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': True, 'fPIC': True}

    revision_mode = 'scm'
    package_originator = 'External'
    package_exportable = True

    exports_sources = 'cmake/*'

    requires = ('HIDAPI/0.13.1', )

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    @property
    def _checkout_subfolder(self):
        return f'{self.name}_src'

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._checkout_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['CMAKE_PROJECT_openhmd_INCLUDE'] = os.path.join(
            self.install_folder, 'conan_paths.cmake')
        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        if not self.options.shared:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
        cmake.configure(source_dir=self._checkout_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self._write_cmake_config_files()

    def _write_cmake_config_files(self):
        cmake_dst = os.path.join(self.package_folder, 'cmake')
        os.makedirs(cmake_dst, exist_ok=True)

        if self.settings.os == 'Windows':
            lib_dirname = 'lib'
            lib_prefix = ''
            lib_extension = '.dll' if self.options.shared else '.lib'
        else:
            lib_dirname = 'lib'
            lib_prefix = 'lib'
            if self.options.shared:
                lib_extension = '.so' if self.settings.os == 'Linux' else '.dylib'
            else:
                lib_extension = '.a'

        data = {
            'os': self.settings.os,
            'lib_version': str(self.version),
            'lib_type': 'SHARED' if self.options.shared else 'STATIC',
            'lib_dirname': lib_dirname,
            'lib_filename': f'{lib_prefix}openhmd{lib_extension}',
        }

        if self.settings.os == 'Windows' and self.options.shared:
            data['win_lib_filename'] = 'openhmd.lib'

        if not self.options.shared:
            data['compile_definitions'] = 'OHMD_STATIC'

        file_loader = FileSystemLoader(os.path.join(self.source_folder, 'cmake'))
        env = Environment(loader=file_loader)

        cmakeconfig_template = env.get_template('OpenHMDConfig.cmake.in')
        cmakeconfig_template.stream(data).dump(os.path.join(cmake_dst, 'OpenHMDConfig.cmake'))

        cmakeconfigversion_template = env.get_template('OpenHMDConfigVersion.cmake.in')
        cmakeconfigversion_template.stream(data).dump(
            os.path.join(cmake_dst, 'OpenHMDConfigVersion.cmake'))
