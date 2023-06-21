# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools
import os

class GTestConan(ConanFile):
    name = "GTest"
    license = "BSD-3-Clause"
    author = "Google"
    url = "https://github.com/google/googletest"
    description = "Googletest is a testing framework developed by the " \
        "Testing Technology team with Google's specific requirements and " \
        "constraints in mind. It combines googletest and googlemock."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    generators = "cmake_paths"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "GTEST_RUN_UNITTESTS" in os.environ

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test()

    def _configure_cmake(self):
        cmake = CMake(self)
        if self.options.shared:
            cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
        else:
            cmake.definitions["gtest_force_shared_crt"] = "ON"


        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = \
                self.options.fPIC
        srcFolder = os.path.join(self.source_folder, self._source_subfolder)
        cmake.configure(source_folder=srcFolder)
        return cmake

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["gtest", "gmock"]

