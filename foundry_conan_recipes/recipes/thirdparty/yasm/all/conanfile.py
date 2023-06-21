# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil

from conans import ConanFile, CMake, tools


class YasmConan(ConanFile):
    name = 'yasm'
    description = 'Yasm is a complete rewrite of the NASM assembler under the "new" BSD License.'
    url = 'https://yasm.tortall.net/'
    license = 'BSD-2-Clause'
    author = 'Peter Johnson, Michael Urman and others'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @property
    def _run_unit_tests(self):
        return 'YASM_RUN_UNITTESTS' in os.environ

    def build(self):
        cmake = self._configure()
        cmake.build()

        if self._run_unit_tests:
            cmake.test()

    def _configure(self):
        cmake = CMake(self)

        cmake.definitions['YASM_BUILD_TESTS'] = 'ON' if self._run_unit_tests else 'OFF'
        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared

        if not self.options.shared:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
        else:
            if self.settings.os == 'Macos':
                cmake.definitions['CMAKE_INSTALL_NAME_DIR'] = '@rpath'
                cmake.definitions['CMAKE_INSTALL_RPATH'] = '@executable_path/../lib'
            elif self.settings.os == 'Linux':
                cmake.definitions['CMAKE_INSTALL_RPATH'] = '\$ORIGIN/../lib'

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        cmake.configure(source_folder=self._source_subfolder)

        return cmake

    def package(self):
        cmake = self._configure()
        cmake.install()

        shutil.rmtree(os.path.join(self.package_folder, 'lib'))
        shutil.rmtree(os.path.join(self.package_folder, 'include'))

        self.copy(pattern='BSD.txt', dst='licenses', src=self._source_subfolder)
        self.copy(pattern='COPYING', dst='licenses', src=self._source_subfolder)

    def package_id(self):
        del self.info.settings.build_type
        del self.info.settings.compiler
