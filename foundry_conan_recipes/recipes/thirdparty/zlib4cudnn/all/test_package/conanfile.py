# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake

class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = [
        "cmake_paths"
    ]

    def _get_loadable_lib(self):
        if self.settings.os == "Windows":
            return "zlibwapi.dll"
        elif self.settings.os == "Macos":
            return "libz.dylib"
        elif self.settings.os == "Linux":
            return "libz.so"

    def imports(self):
        self.copy(self._get_loadable_lib(), src=self.deps_cpp_info["zlib4cudnn"].rootpath, dst=self.install_folder)

    def configure(self):
        del self.settings.compiler.libcxx

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["ZLIB_LOADABLE_LIBRARY"] = self._get_loadable_lib()
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
