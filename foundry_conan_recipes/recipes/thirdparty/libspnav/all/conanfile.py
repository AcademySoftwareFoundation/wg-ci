# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import re

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from jinja2 import Environment, FileSystemLoader


class SpNavConan(ConanFile):
    name = 'libspnav'
    description = 'The libspnav library is provided as a replacement of the magellan library.'
    url = 'http://spacenav.sourceforge.net/'
    license = 'BSD-3-Clause'
    author = 'John Tsiombikas'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False], 'fPIC': [True]}
    default_options = {'shared': False, 'fPIC': True}

    exports_sources = '*.cmake.in'
    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True
    

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build(self):
        autotools = self._configure()
        autotools.make()

    def package(self):
        autotools = self._configure()
        autotools.install()

        self._write_cmake_config_file()

        ext = re.compile('\.a' if self.options.shared else '\.so.*')
        for p in os.listdir(os.path.join(self.package_folder, 'lib')):
            if ext.search(p):
                os.remove(os.path.join(self.package_folder, 'lib', p))

    def _configure(self):
        autotools = AutoToolsBuildEnvironment(self)

        if not self.options.shared:
            autotools.flags.append('-fvisibility=hidden')

        config_args = [
            '--disable-opt' if self.settings.build_type == 'Debug' else '--enable-opt',
            '--enable-debug' if self.settings.build_type == 'Debug' else '--disable-debug'
        ]

        autotools.configure(configure_dir=self._source_subfolder, args=config_args)

        return autotools

    def _write_cmake_config_file(self):
        if not os.path.exists(os.path.join(self.package_folder, 'cmake')):
            os.makedirs(os.path.join(self.package_folder, 'cmake'))

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {
                'shared': self.options.shared
            }

            interpreter_template = env.get_template(file_name + '.in')
            interpreter_template.stream(data).dump(os.path.join(self.package_folder, 'cmake', file_name))

        _configure('SpaceNavConfig.cmake')

    @property
    def _source_subfolder(self):
        return '{}_src'.format(self.name)
