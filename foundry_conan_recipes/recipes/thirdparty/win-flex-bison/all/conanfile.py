# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class WinFlexBisonConan(ConanFile):
    name = 'win-flex-bison'
    license = 'GPL-3.0-or-later'
    author = 'Alex Zhondin (in addition to original authors of flex and bison)'
    url = 'https://github.com/lexxmark/winflexbison'
    description = ('WinFlexBison is a Windows port of Flex (the fast lexical '
                    'analyser) and GNU Bison (parser generator). Both win_flex and '
                    'win_bison are based on upstream sources but depend on system '
                    'libraries only.')
    settings = 'os', 'build_type', 'arch'

    revision_mode = 'scm'
    generators = 'cmake_paths'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        version_data = self.conan_data['sources'][self.version]
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        src_path = os.path.join(self.build_folder, self._source_subfolder, 'bin')

        self.copy(pattern='*.exe', dst='bin', src=src_path, keep_path=False)
        self.copy(pattern='data/*', dst='bin', src=os.path.join(src_path, str(self.settings.build_type)))

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    @property
    def _source_subfolder(self):
        return '{}_src'.format(self.name)

    def package_id(self):
        del self.info.settings.build_type
