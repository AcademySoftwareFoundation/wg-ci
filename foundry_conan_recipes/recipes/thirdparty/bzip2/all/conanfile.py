# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class Bzip2Conan(ConanFile):
    name = "bzip2"
    license = "bzip2-1.0.6"
    author = "Julian R Seward"
    url = "https://www.sourceware.org/bzip2/"
    description = "bzip2 is a free and open-source file compression program that uses the Burrows Wheeler algorithm."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "*"
    no_copy_source = True
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "BZIP2_RUN_UNITTESTS" in os.environ

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SOURCE_DIR"] = os.path.join(self.source_folder, self._checkout_folder)
        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test(output_on_failure=True)

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["bz2"]
