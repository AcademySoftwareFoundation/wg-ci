# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, CMake

class LibtiffConan(ConanFile):
    name = "libtiff"
    license = "libtiff"
    author = "Sam Leffler"
    url = "http://www.simplesystems.org/libtiff/"
    description = "TIFF provides support for the Tag Image File Format (TIFF), a widely used format for storing image data."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    revision_mode = "scm"
    generators = "cmake_paths"

    package_originator = "External"
    package_exportable = True

    requires = [
        "zlib/1.2.11@thirdparty/development",
        "JPEG/9e",
    ]

    @property
    def _run_unit_tests(self):
        return "LIBTIFF_RUN_UNITTESTS" in os.environ

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_tiff_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["cxx"] = "OFF"
        cmake.definitions["zstd"] = "OFF"

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test()

    def package(self):
        self._configure_cmake().install()

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["tiffd.lib" if self.settings.build_type == "Debug" else "tiff.lib"]
        else:
            self.cpp_info.libs = ["tiff"]
