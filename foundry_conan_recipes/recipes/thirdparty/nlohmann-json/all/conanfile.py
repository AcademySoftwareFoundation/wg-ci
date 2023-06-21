# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools
import os

class NlohmannJsonConan(ConanFile):
    name = "nlohmann-json"
    description = "JSON parser and generator for modern C++."
    url = "https://github.com/nlohmann/json"
    license = "MIT"
    author = "Niels Lohmann <mail@nlohmann.me>"

    package_originator = "External"
    package_exportable = True
    revision_mode = "scm"

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
        cmake.definitions["JSON_BuildTests"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        self.copy("*", src=os.path.join(self._source_subfolder, "include"), dst="include")


    def package_id(self):
        self.info.header_only()
