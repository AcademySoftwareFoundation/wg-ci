# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools


class Sse2Neon(ConanFile):
    name = 'sse2neon'
    description = 'A C/C++ header file that converts Intel SSE intrinsics to Arm/Aarch64 NEON intrinsics.'
    url = 'https://github.com/DLTcollab/sse2neon'
    license = 'MIT'
    author = 'DLTcollab'

    exports_sources = 'cmake/*.cmake'
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

    def package(self):
        self.copy('LICENSE', 'sse2neon', self._source_subfolder)
        self.copy('README.md', 'sse2neon', self._source_subfolder)
        self.copy('sse2neon.h', 'sse2neon', self._source_subfolder)
        self.copy('sse2neonConfig.cmake', 'cmake', 'cmake')

    def package_id(self):
        self.info.header_only()
