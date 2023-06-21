# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil

from conans import ConanFile, CMake, tools


class CppzmqConan(ConanFile):
    name = 'cppzmq'
    license = 'MIT'
    author = 'Martin Sustrik'
    url = 'https://github.com/zeromq/cppzmq'
    description = 'Header-only C++ binding for libzmq.'

    exports_sources = '*'

    revision_mode = 'scm'

    no_copy_source = True

    package_originator = 'External'
    package_exportable = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, '{}_src'.format(self.name))

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        pass  # Nothing to build; header-only library.

    def package(self):
        self.copy('zmq.hpp', dst='include', src=self._source_subfolder)
        self.copy('zmq_addon.hpp', dst='include', src=self._source_subfolder)
        self.copy('*', dst='cmake', src='cmake')

        cmake_version_file_path = os.path.join(self.package_folder, 'cmake',
                                               'cppzmqConfigVersion.cmake.in')
        tools.replace_in_file(cmake_version_file_path, '@@VERSION@@',
                              self.version)
        shutil.move(cmake_version_file_path,
                    os.path.splitext(cmake_version_file_path)[0])

    def package_id(self):
        self.info.header_only()
