# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools
from jinja2 import Environment, FileSystemLoader


class BsdXdrConan(ConanFile):
    name = "bsd-xdr"
    license = "LicenseRef-bsd-xdr"
    author = "Sun Microsystems"
    url = "https://github.com/woodfishman/bsd-xdr"
    description = ("This package contains a port of Sun's XDR library. It was derived from the "
                   "implementation in the libtirpc package (version 0.1.10-7) from Fedora 11. That "
                   "version was relicensed with explicit permission from the copyright holder (Sun "
                   "Microsystems) to a BSD license.  See the LICENSE file for more information.")

    settings = "os", "compiler", "build_type", "arch"

    options = {"shared": [False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "cmake/*"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    def _get_cygwin_bin_dir(self):
        return os.path.join(self.source_folder, 'cygwin64', 'bin').replace('\\', '/')

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

        if self.settings.os == 'Windows':
            # Cygwin is required with at least the following packages:
            #    * make
            #    * sed
            git = tools.Git(folder='cygwin-standalone')
            git.clone(
                'git@a_gitlab_url:libraries/conan/thirdparty/cygwin-standalone.git',
                branch='1314ea3bef2e60760e40d147c855bbcc53525fd8',  # foundry/v3.4.3
                shallow=True)
            tools.untargz('cygwin-standalone/cygwin64.tgz')

            # Cygwin's `link.exe` file conflicts with MSVC's linker; remove it.
            os.remove(os.path.join(self._get_cygwin_bin_dir(), 'link.exe'))

    def build(self):
        env_vars = {}

        if self.settings.build_type == "Debug":
            env_vars['ENABLE_DEBUG'] = '1'

        if self.settings.os == "Windows":
            makefile = 'Makefile.msvc80'
            env_vars['PATH'] = [self._get_cygwin_bin_dir()]
        else:
            makefile = 'Makefile.unix'
            if self.options.fPIC:
                env_vars['ENABLE_PIC'] = '1'

        with tools.chdir(self._source_subfolder):
            with tools.environment_append(env_vars):
                self.run(f'make -f {makefile}')

    def package(self):
        self._write_cmake_config_files()

        self.copy('rpc/*', dst='include', src=self._source_subfolder, keep_path=True)

        if self.settings.os == "Windows":
            self.copy('src/msvc/*.h', dst='include', src=self._source_subfolder, keep_path=False)
            self.copy('msvc80/xdr_s.lib', dst='lib', src=self._source_subfolder, keep_path=False)
        else:
            self.copy('linux/libxdr.a', dst='lib', src=self._source_subfolder, keep_path=False)

    def _write_cmake_config_files(self):
        cmake_dst = os.path.join(self.package_folder, 'cmake')
        os.makedirs(cmake_dst, exist_ok=True)

        data = {'lib_version': str(self.version)}

        if self.settings.os == "Windows":
            data['lib_filename'] = 'xdr_s.lib'
            data['libs'] = 'ws2_32.lib'
        else:
            data['lib_filename'] = 'libxdr.a'

        file_loader = FileSystemLoader(os.path.join(self.source_folder, 'cmake'))
        env = Environment(loader=file_loader)

        cmakeconfig_template = env.get_template('BSDXdrConfig.cmake.in')
        cmakeconfig_template.stream(data).dump(os.path.join(cmake_dst, 'BSDXdrConfig.cmake'))

        cmakeconfigversion_template = env.get_template('BSDXdrConfigVersion.cmake.in')
        cmakeconfigversion_template.stream(data).dump(
            os.path.join(cmake_dst, 'BSDXdrConfigVersion.cmake'))
