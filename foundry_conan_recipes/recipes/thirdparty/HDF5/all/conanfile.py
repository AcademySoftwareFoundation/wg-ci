# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, CMake

class HDF5Conan(ConanFile):
    name = "HDF5"
    license = "BSD-3-Clause"
    author = "HDF Group"
    url = "https://support.hdfgroup.org/HDF5/"
    description = "HDF5 is a unique technology suite that makes possible the management of extremely large and complex data collections."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    no_copy_source = True
    generators = "cmake_paths"
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    build_requires = (
        "zlib/1.2.11@thirdparty/development"
    )

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def configure(self):
        self.options["zlib"].shared = False

        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["HDF5_BUILD_TOOLS"] = "ON"
        cmake.definitions["HDF5_BUILD_HL_LIB"] = "ON"
        cmake.definitions["HDF5_BUILD_CPP_LIB"] = "ON"
        cmake.definitions["HDF5_ENABLE_Z_LIB_SUPPORT"] = "ON"
        cmake.definitions["ZLIB_USE_EXTERNAL"] = "ON"
        cmake.definitions["CMAKE_PROJECT_HDF5_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        if self.options.shared and self.settings.os == "Macos":
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        # TODO as need to verify is something Jenkins can reproduce
        self.cpp_info.libs = ["HDF5"]

