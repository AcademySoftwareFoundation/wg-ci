# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools


class FakeItConan(ConanFile):
    name = "fakeit"
    description = "A modern, C++-native, header-only, framework for unit-tests, TDD and BDD"
    url = "https://github.com/eranpeer/FakeIt"
    license = "MIT"
    author = "Eran Pe'er"

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
        cmake.definitions["PROJECT_VERSION"] = self.version
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

        self.copy(pattern="LICENSE.txt", dst="licenses")

    def package_id(self):
        self.info.header_only()
