# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
import time

from conans import ConanFile, AutoToolsBuildEnvironment, tools


class BisonConan(ConanFile):
    name = 'bison'
    description = ('GNU Bison is a general-purpose parser generator that converts an'
                   'annotated context-free grammar into a deterministic LR or'
                   'generalized LR (GLR) parser employing LALR(1) parser tables')
    url = 'https://www.gnu.org/software/bison/'
    license = 'GPL-3.0-or-later'
    author = 'The GNU Project'
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

        # Files written by Git may present slightly different timestamps.
        # docs will attempt to be rebuilt if the modification dates are slightly off
        # This presents a problem, as makeinfo might not be on the build machines
        # We'll touch every file after checkout, so they all share the same modification time.
        timestamp = time.time()
        with tools.chdir(self._source_subfolder):
            for file_path in tools.relative_dirs('.'):
                tools.touch(file_path, (timestamp, timestamp))

    def build(self):
        autotools = self._configure()
        autotools.make()

    def package(self):
        autotools = self._configure()
        autotools.make(args=['install'])

        self.copy(pattern='COPYING', dst='.', src=self._source_subfolder)

        shutil.rmtree(os.path.join(self.package_folder, 'lib'))

    def _configure(self):
        configure_args = [
            '--enable-relocatable'
        ]

        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=self._source_subfolder, args=configure_args)
        return autotools

    @property
    def _source_subfolder(self):
        return '{}_src'.format(self.name)
