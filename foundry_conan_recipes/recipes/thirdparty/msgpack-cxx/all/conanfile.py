# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil

from conans import ConanFile, CMake, tools


class MessagePack(ConanFile):
    name = 'msgpack-cxx'
    description = 'MessagePack is an extremely efficient object serialization library.'
    url = 'https://msgpack.org'
    license = 'BSL-1.0'
    author = 'Sadayuki Furuhashi'

    exports_sources = 'cmake/*.cmake'
    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        cmake = self._configure()
        cmake.build()

    def package(self):
        cmake = self._configure()
        cmake.install()

        # The build-provided cmake files are deleted, because they force a dependency on Boost.
        shutil.rmtree(os.path.join(self.package_folder, 'lib'))
        self.copy('msgpack-cxxConfig.cmake', 'cmake', 'cmake')

    def package_id(self):
        self.info.header_only()

    def _configure(self):
        cmake = CMake(self)

        cmake.definitions['MSGPACK_USE_BOOST'] = 'OFF'

        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

