# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools
from jinja2 import Environment, FileSystemLoader


class OpenFXConan(ConanFile):
    name = 'openfx'
    description = ('OFX is an open API for writing visual effects plug-ins for a wide variety of '
                   'applications, such as video editing systems and compositing systems.')
    url = 'https://github.com/AcademySoftwareFoundation/openfx'
    license = 'BSD-3-Clause'
    author = 'The Open Effects Association'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    exports_sources = "cmake/*"

    @property
    def _checkout_subfolder(self):
        return f'{self.name}_src'

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._checkout_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        pass

    def package(self):
        self.copy('include/*.h', dst='.', keep_path=True, src=self._checkout_subfolder)

        self._write_cmake_config_files()

    def _write_cmake_config_files(self):
        cmake_dst = os.path.join(self.package_folder, 'cmake')
        os.makedirs(cmake_dst, exist_ok=True)

        data = {'version': str(self.version)}

        file_loader = FileSystemLoader(os.path.join(self.source_folder, 'cmake'))
        env = Environment(loader=file_loader)

        cmakeconfig_template = env.get_template('OFXConfig.cmake.in')
        cmakeconfig_template.stream(data).dump(os.path.join(cmake_dst, 'OFXConfig.cmake'))

        cmakeconfigversion_template = env.get_template('OFXConfigVersion.cmake.in')
        cmakeconfigversion_template.stream(data).dump(
            os.path.join(cmake_dst, 'OFXConfigVersion.cmake'))

    def package_id(self):
        self.info.header_only()
