# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import CMake, ConanFile, tools
from jinja2 import FileSystemLoader, Environment


class SwigConan(ConanFile):
    name = "SWIG"
    # IMPORTANT: SWIG is GPL licensed, and has only been approved as a build-time tool for code
    # generation. It may NOT be bundled or shipped with our products.
    license = "GPL-3.0"
    author = "David M. Beazley, SWIG developers"
    url = "https://github.com/swig/swig"
    description = ("SWIG is a software development tool that connects programs written in C and "
                   "C++ with a variety of high-level programming languages.")

    settings = "os", "arch"

    exports_sources = "cmake/*"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    build_requires = ('pcre2/10.42', )

    generators = 'cmake_paths'

    def build_requirements(self):
        if self.settings.os == 'Windows':
            self.build_requires('win-flex-bison/2.5.24')
        else:
            self.build_requires('bison/3.8.2')

    @property
    def _run_unit_tests(self):
        return 'SWIG_RUN_UNITTESTS' in os.environ

    @property
    def _checkout_subfolder(self):
        return f'{self.name}_src'

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['CMAKE_PROJECT_swig_INCLUDE'] = os.path.join(
            self.install_folder, 'conan_paths.cmake')
        if self.settings.os == 'Windows':
            bison_filepath = os.path.join(self.deps_cpp_info['win-flex-bison'].rootpath, 'bin',
                                          'win_bison.exe')
        else:
            bison_filepath = os.path.join(self.deps_cpp_info['bison'].rootpath, 'bin', 'bison')
        cmake.definitions['BISON_EXECUTABLE'] = bison_filepath
        cmake.configure(source_folder=self._checkout_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test(output_on_failure=True)

    def package(self):
        self._configure_cmake().install()

        self._write_cmake_config_files()

    def _write_cmake_config_files(self):
        cmake_dst = os.path.join(self.package_folder, 'cmake')
        os.makedirs(cmake_dst, exist_ok=True)

        data = {'lib_version': str(self.version)}

        if self.settings.os == "Windows":
            data['executable_filename'] = 'swig.exe'
        else:
            data['executable_filename'] = 'swig'

        file_loader = FileSystemLoader(os.path.join(self.source_folder, 'cmake'))
        env = Environment(loader=file_loader)

        cmakeconfig_template = env.get_template('SWIGConfig.cmake.in')
        cmakeconfig_template.stream(data).dump(os.path.join(cmake_dst, 'SWIGConfig.cmake'))

        cmakeconfigversion_template = env.get_template('SWIGConfigVersion.cmake.in')
        cmakeconfigversion_template.stream(data).dump(
            os.path.join(cmake_dst, 'SWIGConfigVersion.cmake'))

    def package_id(self):
        if self.settings.os == "Macos":
            # no os.version so not tied to a minimum deployment target
            del self.info.settings.os.version
