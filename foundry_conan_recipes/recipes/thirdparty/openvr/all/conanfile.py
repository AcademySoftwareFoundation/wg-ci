# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools
from jinja2 import Environment, FileSystemLoader


class OpenVrConan(ConanFile):
    description = 'OpenVR is an API and runtime that allows access to VR hardware from multiple ' \
                  'vendors without requiring that applications have specific knowledge of the '   \
                  'hardware they are targeting.'
    url = 'https://github.com/ValveSoftware/openvr'
    license = 'BSD-3-Clause'
    author = 'Valve Software'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': True, 'fPIC': True}

    exports_sources = "*.cmake.in"
    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy('*.h', dst='include/OpenVR', src=os.path.join(self._source_subfolder, 'headers'))

        self._write_cmake_config_file()

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

    def _configure_cmake(self):
        cmake = CMake(self)

        # There is a tri-state possible on `Mac`: `Shared`, `Framework` or `Static`.
        # See, https://a_gitlab_url/libraries/conan/thirdparty/openvr/blob/v1.0.8/src/CMakeLists.txt#L62-64
        # Use `Shared` and `Static variants on all platforms.
        cmake.definitions['BUILD_SHARED'] = 'ON' if self.options.shared else 'OFF'

        if not self.options.shared:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = 'ON'

        cmake.definitions['BUILD_UNIVERSAL'] = 'OFF'

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))

        return cmake

    def _write_cmake_config_file(self):
        if not os.path.exists(os.path.join(self.package_folder, "cmake")):
            os.makedirs(os.path.join(self.package_folder, "cmake"))

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {
                'libprefix': '' if self.settings.os == 'Windows' else 'lib',
                'libsuffix': '64.lib' if self.settings.os == 'Windows' else '.a',
                'os': self.settings.os,
                'shared': self.options.shared,
            }

            if self.options.shared:
                data['libsuffix'] = '.dylib' if self.settings.os == 'Macos' else '.so'

            interpreter_template = env.get_template(file_name + '.in')
            interpreter_template.stream(data).dump(os.path.join(self.package_folder, 'cmake', file_name))

        _configure('OpenVRConfig.cmake')
