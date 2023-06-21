# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class LLVMConan(ConanFile):
    name = "LLVM"
    description = "The LLVM Project is a collection of modular and reusable compiler and toolchain technologies."
    url = "https://llvm.org/"
    author = "Chris Lattner"
    license = "LicenceRef-Apache-2.0-with-LLVM-Exceptions"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    revision_mode = "scm"
    short_paths = True

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, f"{self.name}_src")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["LLVM_ENABLE_PROJECTS"] = "clang"
        cmake.definitions["LLVM_PARALLEL_LINK_JOBS"] = 2
        cmake.definitions["LLVM_INSTALL_UTILS"] = "ON"

        cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
        cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
        cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder, "llvm"))
        return cmake

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self._configure_cmake().install()
