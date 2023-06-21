# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools
from jinja2 import Environment, FileSystemLoader


class BulletPhysics(ConanFile):
    name = 'bulletphysics'
    description = 'A real-time collision detection and multi-physics simulation.'
    url = 'https://github.com/bulletphysics/bullet3/'
    license = 'Zlib'
    author = 'Bullet Physics development team'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [False], 'fPIC': [True]}
    default_options = { 'shared': False, 'fPIC': True }

    exports_sources = '*.cmake.in'
    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build(self):
        cmake = self._configure()
        cmake.build()

    def package(self):
        cmake = self._configure()
        cmake.install()

        self._write_cmake_config_file()

    def _configure(self):
        cmake = CMake(self)

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        if not self.options.shared:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = 'ON'

        if self.settings.compiler == 'Visual Studio':
            cmake.definitions['USE_MSVC_RUNTIME_LIBRARY_DLL'] = 'MD' in self.settings.compiler.runtime

        cmake.definitions['INSTALL_LIBS'] = 'ON'

        cmake.configure(source_folder=os.path.join(self.build_folder, self._source_subfolder))

        return cmake

    def _write_cmake_config_file(self):
        os.makedirs(os.path.join(self.package_folder, 'cmake'), exist_ok=True)

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {
                'bt': '_Debug' if self.settings.build_type == 'Debug' and self.settings.os == 'Windows' else '',
                'libprefix': '' if self.settings.os == 'Windows' else 'lib',
                'libext': 'lib' if self.settings.os == 'Windows' else 'a'
            }

            interpreter_template = env.get_template(file_name + '.in')
            interpreter_template.stream(data).dump(os.path.join(self.package_folder, 'cmake', file_name))

        _configure('bulletphysicsConfig.cmake')

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'
