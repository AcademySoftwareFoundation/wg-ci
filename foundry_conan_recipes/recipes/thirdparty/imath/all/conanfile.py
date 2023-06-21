# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools
from os import path


class imath(ConanFile):
    name = "imath"
    description = ("Imath is a basic, light-weight, and efficient C++ representation of 2D and 3D "
                   "vectors and matrices and other simple but useful mathematical objects, functions, "
                   "and data types common in computer graphics applications, "
                   "including the “half” 16-bit floating-point type.")

    author = "Academy Software Foundation"
    license = "BSD-3-Clause"
    url = "https://github.com/AcademySoftwareFoundation/Imath"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {"shared": True, "fPIC": True}

    generators = "cmake_paths"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _config_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_DEBUG_POSTFIX"] = ""
        # avoid having extra symlinking
        cmake.definitions["IMATH_LIB_SUFFIX"] = ""
        cmake.definitions["BUILD_SHARED"] = "ON" if self.options.shared else "OFF"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure(source_folder=path.join(
            self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self._config_cmake()
        cmake.build()

    def package(self):
        cmake = self._config_cmake()
        cmake.install()
