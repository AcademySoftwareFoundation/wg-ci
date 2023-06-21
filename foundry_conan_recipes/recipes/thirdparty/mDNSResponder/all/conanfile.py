# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
from jinja2 import Environment, FileSystemLoader


class mDNSResponderConan(ConanFile):
    name = 'mdnsresponder'
    description = 'Apple’s Open Source DNS Service Discovery Collection.'
    url = 'https://github.com/apple-oss-distributions/mDNSResponder/'
    license = 'Apache-2.0'
    author = 'Apple'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True], 'fPIC': [True]}
    default_options = {'shared': True, 'fPIC': True}

    exports_sources = '*.cmake.in'
    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def build(self):
        if self.settings.os == 'Windows':
            self._upgrade_ms_build_scripts()            

            msbuild = MSBuild(self)
            sln = os.path.join(self.build_folder, self._source_subfolder, 'mDNSWindows', 'mDNSResponder.sln')
            msbuild.build(sln, targets=[self._msvs_target], upgrade_project=False)
        else:
            with tools.chdir(os.path.join(self.build_folder, self._source_subfolder, 'mDNSPosix')):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.make(target='libdns_sd')

    def package(self):
        self.copy('*.h', 'include/mDNSResponder', os.path.join(self._source_subfolder, 'mDNSCore'), keep_path=False)
        self.copy('*.h', 'include/mDNSResponder', os.path.join(self._source_subfolder, 'mDNSShared'), keep_path=False)

        if self.settings.os == 'Linux':
            self.copy('*.so*', 'lib', '.', keep_path=False)
        elif self.settings.os == 'Macos':
            self.copy('*.dylib', 'lib', '.', keep_path=False)

            # Make the dylib's relocatable
            dylib_path = os.path.join(self.package_folder, 'lib', 'libdns_sd.dylib')
            args = ['install_name_tool', '-id', '@rpath/libdns_sd.dylib', dylib_path]
            self.run(' '.join(args))
        else:
            self.copy('*.lib', 'lib', self._source_subfolder, keep_path=False)
            self.copy('*.dll', 'bin', self._source_subfolder, keep_path=False)

        self._write_cmake_config_file()

    def _upgrade_ms_build_scripts(self):
        old_sdk_version = '10.0.18362.0'
        new_sdk_version = '10.0.19041.0'

        project_files = [
            os.path.join('mDNSWindows', 'DLL', 'dnssd.vcxproj')
        ]

        for project_file in project_files:
            abs_project_file = os.path.join(self.build_folder, self._source_subfolder, project_file)
            tools.replace_in_file(abs_project_file, old_sdk_version, new_sdk_version)
            
    def _write_cmake_config_file(self):
        os.makedirs(os.path.join(self.package_folder, 'cmake'), exist_ok=True)

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {
                'libsuffix': 'dylib' if self.settings.os == 'Macos' else 'so',
                'os': self.settings.os
            }

            interpreter_template = env.get_template(file_name + '.in')
            interpreter_template.stream(data).dump(os.path.join(self.package_folder, 'cmake', file_name))

        _configure('mDNSResponderConfig.cmake')

    @property
    def _msvs_project_folder(self):
        return os.path.join(self.build_folder, self._source_subfolder, 'mDNSWindows', 'mDNSResponder.sln')

    @property
    def _msvs_target(self):
        return 'dnssd'

    @property
    def _source_subfolder(self):
        return f'{self.name}_src'

