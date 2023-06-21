# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import CMake, ConanFile, tools


class DoxygenConan(ConanFile):
    name = "Doxygen"
    # IMPORTANT: Doxygen is GPL licensed, and has only been approved as a build-time tool for code
    # generation. It may NOT be bundled or shipped with our products.
    license = "GPL-2.0"
    author = "Dimitri van Heesch"
    url = "https://github.com/doxygen/doxygen"
    description = ("Doxygen is the de facto standard tool for generating documentation from "
                   "annotated C++ sources.")

    settings = "os", "arch"

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    generators = 'cmake_paths'

    def build_requirements(self):
        if self.settings.os == 'Windows':
            self.build_requires('win-flex-bison/2.5.24')
        else:
            self.build_requires('bison/3.8.2')
            if self.settings.os == 'Linux':
                self.build_requires('flex/2.6.4')
            else:
                # TODO(CA): flex package not yet available for macOS. System's installation will be
                # used.
                pass

    @property
    def _run_unit_tests(self):
        return 'DOXYGEN_RUN_UNITTESTS' in os.environ

    @property
    def _checkout_subfolder(self):
        return f'{self.name}_src'

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_subfolder)
        git.clone(version_data["git_url"], branch=version_data["git_hash"], shallow=True)
        # NOTE: Repository is relatively large; it will be a shallow clone.
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)

        if self.settings.os == 'Windows':
            win_flex_bison_dir = os.path.join(self.deps_cpp_info['win-flex-bison'].rootpath, 'bin')
            bison_filepath = os.path.join(win_flex_bison_dir, 'win_bison.exe')
            flex_filepath = os.path.join(win_flex_bison_dir, 'win_flex.exe')
        else:
            bison_filepath = os.path.join(self.deps_cpp_info['bison'].rootpath, 'bin', 'bison')
            if self.settings.os == 'Linux':
                flex_filepath = os.path.join(self.deps_cpp_info['flex'].rootpath, 'bin', 'flex')

        cmake.definitions['BISON_EXECUTABLE'] = bison_filepath
        if self.settings.os != 'Macos':
            cmake.definitions['FLEX_EXECUTABLE'] = flex_filepath

        cmake.configure(source_folder=self._checkout_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            # NOTE: xmllint (part of libxml2-utils) and LaTeX needed for unit tests.
            cmake.test(output_on_failure=True)

    def package(self):
        self._configure_cmake().install()

    def package_id(self):
        if self.settings.os == "Macos":
            # no os.version so not tied to a minimum deployment target
            del self.info.settings.os.version

    def package_info(self):
        extension = '.exe' if self.settings.os == 'Windows' else ''
        self.user_info.executable = f'doxygen{extension}'
