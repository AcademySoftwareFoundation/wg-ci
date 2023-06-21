# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, CMake


class TomlplusplusConan(ConanFile):
    name = "tomlplusplus"
    description = "Header-only TOML config file parser and serializer for modern C++."
    url = "https://marzer.github.io/tomlplusplus/"
    license = "MIT"
    author = "Mark Gillard"

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def package(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

    def package_id(self):
        self.info.header_only()
