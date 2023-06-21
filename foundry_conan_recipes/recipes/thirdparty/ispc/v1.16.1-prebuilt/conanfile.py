# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, tools
import os


class IntelImplicitSpmdProgramCompiler(ConanFile):
    name = 'ispc'
    description = 'ispc is a compiler for a variant of the C programming language, ' \
                  'with extensions for single program, multiple data programming.'
    url = 'https://github.com/ispc/ispc'
    license = 'BSD-3-Clause'
    author = 'Intel (R)'
    settings = 'os', 'arch'
    version = '1.16.1-prebuilt'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        self.output.info('Nothing to build, progress to packaging...')

    def package(self):
        self.copy('bin/*', src=self._platform_path, keep_path=True, symlinks=True)

        if self.settings.os == 'Windows' or self.settings.os == 'Linux':
            self.copy('include/*', self._platform_path, keep_path=True, symlinks=True)

        if self.settings.os == 'Windows':
            self.copy('lib/*', self._platform_path, keep_path=True, symlinks=True)
        elif self.settings.os == 'Linux':
            self.copy('lib64/*', self._platform_path, keep_path=True, symlinks=True)

    @property
    def _platform_path(self):
        os_remap = {"Windows": "windows", "Macos": "macOS", "Linux": "linux"}
        platform_path = f'{self.name}-v{self.version}-{os_remap[str(self.settings.os)]}'.replace('-prebuilt', '')
        return os.path.join(self._source_subfolder, platform_path)

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'
