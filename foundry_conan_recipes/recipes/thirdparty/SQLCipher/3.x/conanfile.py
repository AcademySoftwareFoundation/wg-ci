# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools


class SQLCipherConan(ConanFile):
    """
    Recipe for building Foundry's pre-amalgamated SQLCipher 3.1.0.

    Derived from `//Foundry/Thirdparty/sqlcipher/3.1.0/work/`.
    """

    name = 'SQLCipher'
    license = "BSD-3-Clause"
    author = 'Zetetic LLC'
    url = 'https://www.zetetic.net/sqlcipher'
    description = ('SQLCipher is an Open Source SQLite extension that provides'
                   ' transparent 256-bit AES full database encryption.')

    settings = 'os', 'compiler', 'build_type', 'arch'

    exports_sources = "*"
    no_copy_source = True

    options = {'shared': [False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    generators = 'cmake_paths'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    @property
    def _checkout_folder(self):
        return 'SQLCipher_src'

    def requirements(self):
        if "arm" in self.settings.arch:
            self.requires("OpenSSL/[~1.1.1m]")
        else:
            self.requires("OpenSSL/[~1.1.1g]@thirdparty/development")

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        cmake = CMake(self)
        if "fPIC" in self.options:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.definitions["CMAKE_PROJECT_SQLCipher_INCLUDE"] = \
            os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        pass
