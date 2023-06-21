# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class EmbreeConan(ConanFile):
    name = 'embree'
    description = 'Intel® Embree is a collection of high-performance ray tracing kernels, developed at Intel.'
    url = 'https://github.com/embree/embree'
    license = 'Apache-2.0'
    author = 'Intel Corporation'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': True, 'fPIC': True}

    revision_mode = 'scm'
    generators = 'cmake_paths'

    package_originator = 'External'
    package_exportable = True

    def build_requirements(self):
        self.build_requires('ispc/1.18.0')

    def requirements(self):
        self.requires('tbb/2020_U3')

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        cmake = self._configure()

        cpu_count = tools.cpu_count()
        if self.settings.os == 'Linux' and self.settings.build_type == 'Debug':
            cpu_count = max(cpu_count // 2, 1)

        with tools.environment_append({'CONAN_CPU_COUNT': str(cpu_count)}):
            cmake.build()

    def package(self):
        cmake = self._configure()
        cmake.install()

    @property
    def _project_name(self):
        return f'embree{tools.Version(self.version).major}'

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

    def _configure(self):
        cmake = CMake(self)

        cmake.definitions['EMBREE_STATIC'] = 'OFF' if self.options.shared else 'ON'
        cmake.definitions['EMBREE_TUTORIALS'] = 'OFF'

        cmake.definitions[f'CMAKE_PROJECT_{self._project_name}_INCLUDE'] = os.path.join(
            self.install_folder, 'conan_paths.cmake')

        if self.settings.os == 'Windows':
            cmake.definitions['CMAKE_INSTALL_MFC_LIBRARIES'] = 'OFF'
            cmake.definitions['CMAKE_INSTALL_OPENMP_LIBRARIES'] = 'OFF'
        else:
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        if self.options.shared:
            # Disable all RPATHs so that build machine paths do not appear in binaries.
            cmake.definitions['CMAKE_SKIP_RPATH'] = 'ON'
        else:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = 'ON'

        cmake.configure(source_folder=os.path.join(self.build_folder, self._source_subfolder))

        return cmake
