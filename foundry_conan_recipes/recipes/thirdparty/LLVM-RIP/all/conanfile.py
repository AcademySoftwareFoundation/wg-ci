# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools


class LLVMRIPConan(ConanFile):
    name = "LLVM-RIP"
    url = "https://llvm.org/"
    author = "Chris Lattner"
    description = "A patched version of LLVM used for statically linking tools within RIP"
    settings = "os", "compiler", "build_type", "arch"
    license = "Apache-2.0"

    generators = "cmake_paths"
    short_paths = True
    no_copy_source = True
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    options = {
        "shared": [True, False],
        "enable_assertions": [True, False],
        "target_arch": ["X86", "AArch64"]
    }

    default_options = {
        "shared": False,
        "enable_assertions": False,
        "target_arch": "X86"
    }

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["LLVM_ENABLE_PROJECTS"] = "clang;lld"
        cmake.definitions["LLVM_ENABLE_ASSERTIONS"] = self.options.enable_assertions
        cmake.definitions["LLVM_TARGETS_TO_BUILD"] = self.options.target_arch
        cmake.definitions["LLVM_PARALLEL_LINK_JOBS"] = 2
        cmake.definitions["LLVM_INCLUDE_BENCHMARKS"] = "OFF"
        cmake.definitions["LLVM_INCLUDE_EXAMPLES"] = "OFF"
        cmake.definitions["LLVM_INCLUDE_TESTS"] = "OFF"
        cmake.definitions["LLVM_INSTALL_UTILS"] = "ON"
        cmake.definitions["LLVM_ENABLE_RTTI"] = "ON"
        cmake.definitions["LLVM_ENABLE_TERMINFO"] = "OFF"
        cmake.definitions["LLVM_ENABLE_LIBXML2"] = "OFF"
        cmake.definitions["LLVM_BUILD_TOOLS"] = "OFF"
        cmake.definitions["CLANG_BUILD_TOOLS"] = "OFF"
        cmake.definitions["LLD_BUILD_TOOLS"] = "OFF"

        # Hide LLVM symbols so that they don't leak out from RIP
        cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
        cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
        cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.os == "Windows":
            cmake.definitions["LLD_ENABLE_PROJECTS"] = "COFF"
        elif self.settings.os == "Macos":
            cmake.definitions["LLD_ENABLE_PROJECTS"] = "MachO"
        elif self.settings.os == "Linux":
            cmake.definitions["LLD_ENABLE_PROJECTS"] = "ELF"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder, "llvm"))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
