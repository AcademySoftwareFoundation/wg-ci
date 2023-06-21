# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class LlvmOpenMpConan(ConanFile):
    name = "LLVM-OpenMP"
    url = "https://openmp.llvm.org/"
    author = "Chris Lattner"
    description = "The OpenMP subproject of LLVM contains the components required to build an executable LLVM-OpenMP program that are outside the compiler itself."
    settings = "os", "compiler", "build_type", "arch"
    license = "LicenceRef-Apache-2.0-with-LLVM-Exceptions"

    exports_sources = "*"
    short_paths = True
    no_copy_source = True
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    options = {
        "shared": [True],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": True,
        "fPIC": True,
    }

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

    def _configure_cmake(self):
        cmake = CMake(self)

        # Force the normal version of the library (as defaults to stubs version)
        cmake.definitions["LIBOMP_LIB_TYPE"] = "normal"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        if self.settings.os == "Macos":
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder, "openmp"))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = ['LLVM-OpenMP']
