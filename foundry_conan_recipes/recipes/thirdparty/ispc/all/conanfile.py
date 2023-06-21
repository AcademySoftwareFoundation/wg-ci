# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class IntelImplicitSpmdProgramCompiler(ConanFile):
    name = 'ispc'
    description = ('ispc is a compiler for a variant of the C programming language, '
                  'with extensions for single program, multiple data programming.')
    url = 'https://github.com/ispc/ispc'
    license = 'BSD-3-Clause'
    author = 'Intel (R)'
    settings = 'os', 'arch'

    revision_mode = 'scm'
    generators = 'cmake_paths'

    package_originator = 'External'
    package_exportable = True

    build_requires = [
        'LLVM/13.0.1'
    ]

    def build_requirements(self):
        if self.settings.os == 'Windows':
            self.build_requires('win-flex-bison/2.5.24')
        elif self.settings.os == 'Macos':
            self.build_requires('bison/3.8.2')
        else:
            self.build_requires('bison/3.8.2')
            self.build_requires('flex/2.6.4')

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

    def source(self):
        version_data = self.conan_data['sources'][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

        if self.settings.os == 'Windows':
            # Checkout a standalone Cygwin installation that is required for 'm4'.
            cygwin_dir = os.path.join(self.source_folder, 'cygwin-standalone')
            git = tools.Git(folder=cygwin_dir)
            git.clone('git@a_gitlab_url:libraries/conan/thirdparty/cygwin-standalone.git',
                      branch='foundry/v3.1.7')
            tools.untargz(os.path.join(cygwin_dir, 'cygwin64.tgz'))

    @property
    def _environment(self):
        if self.settings.os == 'Windows':
            return { 'PATH': [os.path.join(self.source_folder, 'cygwin64', 'bin')] }
        elif self.settings.os == 'Macos':
            return { 'PATH': [self.deps_cpp_info['bison'].bin_paths[0], self.deps_cpp_info['LLVM'].bin_paths[0]] }
        else:
            return { 'PATH': [self.deps_cpp_info['bison'].bin_paths[0], self.deps_cpp_info['flex'].bin_paths[0], self.deps_cpp_info['LLVM'].bin_paths[0]] }

    def build(self):
        with tools.environment_append(self._environment):
            cmake = self._configure()
            cmake.build()

    def package(self):
        cmake = self._configure()
        cmake.install()

    def _configure(self):
        cmake = CMake(self)

        if self.settings.os == 'Windows':
            cmake.definitions['CYGWIN_INSTALL_PATH'] = os.path.join(self.source_folder, 'cygwin64')
            cmake.definitions['CMAKE_PREFIX_PATH'] = os.path.join(self.source_folder, 'cygwin64', 'bin')

        if self.settings.os == 'Linux':
            cmake.definitions['ARM_ENABLED'] = 'OFF'
        
        cmake.definitions['32BIT_ENABLED'] = 'OFF'

        cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
        cmake.definitions['ISPC_INCLUDE_EXAMPLES'] = 'OFF'
        cmake.definitions['ISPC_INCLUDE_TESTS'] = 'OFF'
        cmake.definitions['ISPC_NO_DUMPS'] = 'ON'
        cmake.definitions['ISPCRT_BUILD_TASKING'] = 'OFF'

        cmake.definitions[f'CMAKE_PROJECT_{self.name}_INCLUDE'] = os.path.join(
            self.install_folder, 'conan_paths.cmake')

        cmake.configure(source_folder=os.path.join(self.build_folder, self._source_subfolder))

        return cmake
