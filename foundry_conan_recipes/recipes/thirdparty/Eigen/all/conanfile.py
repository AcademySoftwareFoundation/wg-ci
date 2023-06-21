# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools

class EigenConan(ConanFile):
    name = 'eigen'
    description = 'Eigen is a C++ template library for linear algebra: matrices, vectors, numerical solvers, and related algorithms.'
    url = 'http://eigen.tuxfamily.org/'
    license = 'MPL-2.0'
    author = 'Benoît Jacob and Gaël Guennebaud'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        self.output.info('Nothing to build, progress to packaging...')

    def package(self):
        cmake = CMake(self)
        cmake.definitions["PROJECT_VERSION"] = self.version
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

    def package_id(self):
        self.info.header_only()

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'
