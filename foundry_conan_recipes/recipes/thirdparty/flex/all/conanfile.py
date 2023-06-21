# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, AutoToolsBuildEnvironment, tools


class FlexConan(ConanFile):
    name = 'flex'
    description = 'flex is a tool for generating scanners: programs which recognize lexical patterns in text.'
    url = 'https://github.com/westes/flex/'
    license = 'BSD-2-Clause'
    author = 'John Millaway, Aaron Stone, Vern Paxson, Van Jacobson, Jef Poskanzer'
    settings = 'os', 'arch'

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
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        with tools.chdir(src_dir):
            self.run('./autogen.sh')

        configure_args = [
            '--disable-nls',
            'HELP2MAN=/bin/true',
            'M4=m4',
            'MAKEINFO=/bin/true'
        ]

        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=self._source_subfolder, args=configure_args)
        autotools.make()

    def package(self):
        self.copy(pattern='flex', dst='bin', src=os.path.join(self.build_folder, 'src'))

    @property
    def _source_subfolder(self):
        return '{}_src'.format(self.name)
