# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment


class ImGuiConan(ConanFile):
    name = 'ImGui'
    author = 'Omar Cornut'
    license = 'MIT'
    url = 'https://github.com/ocornut/imgui'
    description = \
        'Dear ImGui is a bloat-free graphical user interface library for C++.'

    settings = 'os', 'compiler', 'build_type', 'arch'

    options = {'shared': [False, True], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    exports_sources = '*'

    revision_mode = 'scm'

    package_originator = 'External'
    package_exportable = True

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git()
        git.clone(version_data['git_url'], branch='master')
        git.checkout(version_data['git_hash'])

    def build(self):
        cmake = CMake(self)

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = \
                self.options.fPIC

        cmake.configure(source_folder=self.source_folder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy('*', src='cmake/', dst='cmake/', symlinks=True)

        cmake_template_filepath = os.path.join(self.package_folder, 'cmake',
                                               'IMGUIConfig.cmake.in')
        cmake_filepath = cmake_template_filepath[:-3]
        file_content = open(cmake_template_filepath, 'r').read()
        os.remove(cmake_template_filepath)
        wildcard_dict = {}
        wildcard_dict['@@APPLE_SUFFIX@@'] = \
            'dylib' if self.options.shared else 'a'
        wildcard_dict['@@UNIX_SUFFIX@@'] = 'so' if self.options.shared else 'a'
        wildcard_dict['@@WIN32_SUFFIX@@'] = 'lib'
        for wildcard, value in wildcard_dict.items():
            file_content = file_content.replace(wildcard, value)
        with open(cmake_filepath, 'w') as text_file:
            text_file.write(file_content)

    def package_info(self):
        self.cpp_info.libs = ['imgui']
