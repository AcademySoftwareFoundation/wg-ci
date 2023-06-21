# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class OpenAlConan(ConanFile):
    name = 'openal'
    description = 'OpenAL Soft is a cross-platform software implementation of the OpenAL 3D audio API.'
    url = 'https://openal-soft.org/'
    license = 'LGPL-2.0-only'
    author = 'Creative Labs'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True]}
    default_options = {'shared': True}

    revision_mode = 'scm'
    generators = 'cmake_paths'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        cmake = self._configure()
        cmake.build()

    def package(self):
        cmake = self._configure()
        cmake.install()

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

    def _configure(self):
        cmake = CMake(self)

        cmake.configure(source_folder=os.path.join(self.build_folder, self._source_subfolder))

        return cmake
