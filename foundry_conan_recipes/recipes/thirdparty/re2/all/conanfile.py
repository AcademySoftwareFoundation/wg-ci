# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class Re2Conan(ConanFile):
    name = "re2"
    license = "BSD-3-Clause"
    author = "Google"
    url = "https://github.com/google/re2"
    description = "RE2 is a fast, safe, thread-friendly alternative to backtracking regular expression engines like those used in PCRE, Perl, and Python. It is a C++ library."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _run_unit_tests(self):
        return "RE2_RUN_UNITTESTS" in os.environ

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["RE2_BUILD_TESTING"] = "ON" if self._run_unit_tests else "OFF"
        if not self.options.shared:
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test()

    def package(self):
        self.configure_cmake().install()

    def package_info(self):
        # TODO: needed if consumers other than CMake are used (but aren't currently tested)
        pass
