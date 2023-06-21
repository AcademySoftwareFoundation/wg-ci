# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class robinmapConan(ConanFile):
    name = 'robin-map'
    license = 'MIT'
    author = "Thibaut Goetghebuer-Planchon"
    url = 'https://github.com/Tessil/robin-map'
    description = 'C++ implementation of a fast hash map and hash set using robin hood hashing.'

    revision_mode = 'scm'

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
        # Header-only library; nothing to build.
        pass

    def package(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

    def package_id(self):
        self.info.header_only()
