# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools


class GLM(ConanFile):
    name = 'glm'
    settings = ['os', 'arch']
    description = ('OpenGL Mathematics (GLM) is a header only C++ mathematics library for '
                   'graphics software based on the OpenGL Shading Language (GLSL) specifications.')
    url = 'https://github.com/g-truc/glm'
    license = 'MIT'
    author = 'G-Truc Creation'

    generators = 'cmake'
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
        self.copy('*', 'cmake', os.path.join(self._source_subfolder, 'cmake'))
        self.copy('*', 'glm', os.path.join(self._source_subfolder, 'glm'))
        
        self.copy('CMakeLists.txt', '.', self._source_subfolder)
        self.copy('copying.txt', '.', self._source_subfolder)

    def package_id(self):
        self.info.header_only()
