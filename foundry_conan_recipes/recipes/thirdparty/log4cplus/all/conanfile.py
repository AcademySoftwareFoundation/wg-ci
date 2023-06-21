# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment


class Log4cplusConan(ConanFile):
    name = 'Log4cplus'
    license = 'Apache-2.0'
    author = 'https://github.com/log4cplus/log4cplus/blob/master/AUTHORS'
    url = 'https://github.com/log4cplus/log4cplus'
    description = 'log4cplus is a simple to use C++ logging API providing ' \
                  'thread-safe, flexible, and arbitrarily granular control ' \
                  'over log management and configuration. It is modelled ' \
                  'after the Java log4j API.'

    settings = 'os', 'compiler', 'build_type', 'arch'

    options = {'shared': [False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    exports_sources = '*'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git()
        git.clone(version_data['git_url'], 'master')
        git.checkout(version_data['git_hash'])

    def build(self):
        if self.settings.os == 'Linux' or self.settings.os == 'Macos':
            autotools = AutoToolsBuildEnvironment(self)
            autotools_vars = autotools.vars

            config_args = []
            if not self.options.shared:
                autotools_vars['CFLAGS'] += ' -fvisibility=hidden'
                autotools_vars['CXXFLAGS'] += \
                    ' -fvisibility=hidden -fvisibility-inlines-hidden'
                config_args.append('--disable-shared')
                config_args.append('--enable-static')

            with tools.environment_append(autotools_vars):
                autotools.configure(configure_dir=self.source_folder,
                                    args=config_args)
                autotools.make()
                autotools.install()

        else:
            cmake = CMake(self)
            if not self.options.shared:
                cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
                cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
                cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = 'ON'
            cmake.configure(source_folder=self.source_folder)
            cmake.build()
            cmake.install()

    def package(self):
        self.copy('*', dst='cmake/', src='cmake/', symlinks=True)

        cmake_version_template_file_path = os.path.join(
            self.package_folder, 'cmake', 'Log4cplusConfigVersion.cmake.in')
        cmake_version_file_path = cmake_version_template_file_path[:-3]
        file_content = open(cmake_version_template_file_path, 'r').read()
        os.remove(cmake_version_template_file_path)
        file_content = file_content.replace('@@VERSION@@', self.version)
        with open(cmake_version_file_path, 'w') as text_file:
            text_file.write(file_content)

    def package_info(self):
        self.cpp_info.libs = ['log4cplus']
