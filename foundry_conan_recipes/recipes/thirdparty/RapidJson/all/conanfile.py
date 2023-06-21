# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class RapidJsonConan(ConanFile):
    name = "RapidJson"
    license = "MIT"
    author = "Milo Yip"
    url = "https://github.com/Tencent/rapidjson"
    description = "A fast JSON parser/generator for C++ with both SAX/DOM style API"

    # RapidJSON is header-only.
    options = {}
    default_options = {}

    exports_sources = "cmake/*"
    no_copy_source = True
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
        git.checkout(version_data["git_hash"])

    def build(self):
        # RapidJson is header-only, but we need to configure to generate the
        # version config file.
        cmake = CMake(self)

        cmake.definitions["RAPIDJSON_BUILD_DOC"] = "OFF"
        cmake.definitions["RAPIDJSON_BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["RAPIDJSON_BUILD_TESTS"] = "OFF"

        cmake.configure(source_folder=self._source_subfolder)

    def package(self):
        
        self.copy("include/*", src=self._source_subfolder)
        self.copy("*", src="cmake/", dst="cmake/")

        cmake_dir = os.path.join(self.package_folder, "cmake")
        self.copy("RapidJSONConfigVersion.cmake", src=self.build_folder, dst=cmake_dir)
        os.rename(os.path.join(cmake_dir, "RapidJSONConfigVersion.cmake"),
                  os.path.join(cmake_dir, "RapidJsonConfigVersion.cmake"))

    def package_id(self):
        self.info.header_only()
