# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake, tools

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["shared_openimageio"] = self.options["OpenImageIO"].shared

        # OIIO 2 requires at least C++14. If `CMAKE_CXX_STANDARD` is not set, the compiler's default
        # C++ standard will be used. While this works fine with MSVC and GCC, where the compiler's
        # version is bound to a specific default C++ standard, in macOS the default C++ standard is
        # C++98, which OIIO 2 does not support.
        if self.settings.os == 'Macos':
            cmake.definitions['CMAKE_CXX_STANDARD'] = 14

        cmake.definitions.update(self.deps_user_info["boost"].vars)

        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)

