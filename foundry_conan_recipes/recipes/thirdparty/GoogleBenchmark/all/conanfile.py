# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools
class GoogleBenchmarkConan(ConanFile):
    name = "GoogleBenchmark"
    license = "Apache-2.0"
    author = "https://github.com/google/benchmark/blob/master/AUTHORS"
    url = "https://github.com/google/benchmark"
    description = "A library to benchmark code snippets, similar to unit tests."
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = { "shared": False, "fPIC": True }
    generators = "cmake_paths"
    revision_mode = "scm"
   
    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "GOOGLEBENCHMARK_RUN_UNITTESTS" in os.environ

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        version_data = self.conan_data["sources"][self.version]
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["CMAKE_PROJECT_benchmark_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        # disable all RPATHs so that build machine paths do not appear in binaries
        cmake.definitions["CMAKE_SKIP_RPATH"] = "1"

        cmake.configure(
            source_folder=os.path.join(self.source_folder, self._source_subfolder)
        )
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
  
    def package_info(self):
        self.cpp_info.libs = [ "benchmark" ] 
