# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools


class CatchConan(ConanFile):
    name = "catch2"
    settings = ["os", "arch", "compiler", "build_type"]
    description = "A modern, C++-native, header-only, framework for unit-tests, TDD and BDD"
    url = "https://github.com/catchorg/Catch2"
    homepage = url
    license = "BSL-1.0"
    author = "Phil Nash <github@philnash.me>"

    generators = "cmake"
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

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
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["CATCH_INSTALL_DOCS"] = "OFF"
        cmake.definitions["CATCH_INSTALL_HELPERS"] = "ON"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

        self.copy(pattern="LICENSE.txt", dst="licenses")


    def package_id(self):
        self.info.header_only()


    def package_info(self):
        self.cpp_info.builddirs.append("lib/cmake/Catch2")
