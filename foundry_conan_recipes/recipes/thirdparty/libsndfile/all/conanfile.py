# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import CMake, ConanFile, tools


class LibsndfileConan(ConanFile):
    name = "libsndfile"
    license = "LGPL-2.1-or-later"
    author = "Erik de Castro Lopo"
    url = "https://github.com/libsndfile/libsndfile"
    description = "A C library for reading and writing sound files containing sampled audio data."

    settings = "os", "arch", "compiler", "build_type"

    options = {"shared": [True]}
    default_options = {"shared": True}

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    @property
    def _run_unit_tests(self):
        return "LIBSNDFILE_RUN_UNITTESTS" in os.environ

    @property
    def _checkout_subfolder(self):
        return f"{self.name}_src"

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_REGTEST"] = False
        cmake.definitions["BUILD_TESTING"] = self._run_unit_tests
        cmake.definitions["ENABLE_EXTERNAL_LIBS"] = False

        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Ogg"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Vorbis"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_FLAC"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Opus"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Speex"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_SQLite3"] = True

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"

        cmake.configure(source_folder=self._checkout_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test(output_on_failure=True)

    def package(self):
        self._configure_cmake().install()
