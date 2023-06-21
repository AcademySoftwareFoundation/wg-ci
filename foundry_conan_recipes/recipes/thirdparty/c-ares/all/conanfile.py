# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class CAresConan(ConanFile):
    name = "c-ares"
    license = "MIT"
    author = "Daniel Stenberg with many contributors"
    url = "https://c-ares.haxx.se/"
    description = "c-ares is a C library for asynchronous DNS requests (including name resolves)."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @property
    def _run_unit_tests(self):
        return "C_ARES_RUN_UNITTESTS" in os.environ

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CARES_STATIC"] = "ON" if not self.options.shared else "OFF"
        cmake.definitions["CARES_SHARED"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["CARES_BUILD_TESTS"] = "ON" if self._run_unit_tests else "OFF"
        cmake.definitions["CARES_BUILD_CONTAINER_TESTS"] = "OFF"
        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
            cmake.definitions["CARES_STATIC_PIC"] = "ON" if self.options.fPIC else "OFF"
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
