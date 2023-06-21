# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class fmtConan(ConanFile):
    name = "fmt"
    license = "BSD-2-Clause"   # Later versions appear to have changed the license to MIT, if support were added: this will need review.
    url = "https://github.com/fmtlib/fmt"
    author = "https://a_gitlab_url/libraries/conan/thirdparty/fmt/-/blob/master/LICENSE.rst"
    description = "{fmt} is an open-source formatting library providing a fast and safe alternative to C stdio and C++ iostreams."
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
        return "FMT_RUN_UNITTESTS" in os.environ

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

        cmake.definitions["CMAKE_PROJECT_fmt_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
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
        self.cpp_info.libs = [ "fmt" ] 
