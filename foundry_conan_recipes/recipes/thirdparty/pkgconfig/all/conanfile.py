# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import time
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class PkgConfigConan(ConanFile):
    name = 'pkgconfig'
    license = 'GPL-2.0'
    author = 'James Henstridge'
    url = 'https://www.freedesktop.org/wiki/Software/pkg-config/'
    description = 'pkg-config is a helper tool used when compiling ' \
                  'applications and libraries.'

    settings = 'os', 'compiler', 'build_type', 'arch'

    options = {}
    default_options = {}

    exports_sources = '*'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    @property
    def _checkout_folder(self):
        return '{}_src'.format(self.name)

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

        # Files written by Git may present slightly different timestamps.
        # pkg-config will attempt to invoke aclocal if it detects that
        # `aclocal.m4` is older than `pkg.m4.in`. This is a problem, as
        # aclocal may not be available in the build machine. We'll touch every
        # file after checkout, so they all share the same modification time.
        timestamp = time.time()
        with tools.chdir(self._checkout_folder):
            for file_path in tools.relative_dirs('.'):
                tools.touch(file_path, (timestamp, timestamp))

    def build(self):
        src_dir = os.path.join(self.source_folder, self._checkout_folder)
        with tools.chdir(src_dir):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=['--with-internal-glib'])
            autotools.make()
            autotools.install()

    def package(self):
        pass
