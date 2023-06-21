# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class OpenImageDenoise(ConanFile):
    name = 'openimagedenoise'
    description = ('Intel Open Image Denoise is an open source library of high-performance,'
                   'high-quality denoising filters for images rendered with ray tracing.')
    url = 'https://www.openimagedenoise.org/'
    license = 'Apache-2.0'
    author = 'Intel Corporation'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': True, 'fPIC': True}

    revision_mode = 'scm'
    generators = 'cmake_paths'

    package_originator = 'External'
    package_exportable = True

    build_requires = [
        'ispc/1.18.0'
    ]

    requires = [
        'tbb/2020_U3'
    ]

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'], submodule='shallow')

    def _configure(self):
        cmake = CMake(self)

        cmake.definitions['CMAKE_PROJECT_OpenImageDenoise_INCLUDE'] = os.path.join(
            self.install_folder, 'conan_paths.cmake')

        cmake.definitions['OIDN_STATIC_LIB'] = 'OFF' if self.options.shared else 'ON'

        if self.options.shared:
            # Disable all RPATHs so that build machine paths do not appear in binaries.
            cmake.definitions['CMAKE_SKIP_RPATH'] = 'ON'
        else:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = 'ON'

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))

        return cmake

    def build(self):
        cmake = self._configure()
        cmake.build()

    def package(self):
        cmake = self._configure()
        cmake.install()



