# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools

class NanobindConan(ConanFile):
    name = "nanobind"
    license = "BSD-3-Clause"
    author = "Wenzel Jakob <wenzel.jakob@epfl.ch>"
    url = "https://github.com/wjakob/nanobind"
    description = "Seamless operability between C++17 and Python"

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")

    def package(self):
        self.copy("include/nanobind/*.h", src=self._source_subfolder, dst=self.package_folder)
        self.copy("include/nanobind/stl/*.h", src=self._source_subfolder, dst=self.package_folder)
        self.copy("include/nanobind/stl/detail/*.h", src=self._source_subfolder, dst=self.package_folder)
        self.copy("ext/robin_map/include/tsl/*.h", src=self._source_subfolder, dst=self.package_folder)
        self.copy("cmake/nanobind-config.cmake", src=self._source_subfolder, dst=self.package_folder)
        self.copy("src/*.h", src=self._source_subfolder, dst=self.package_folder)
        self.copy("src/*.cpp", src=self._source_subfolder, dst=self.package_folder)
