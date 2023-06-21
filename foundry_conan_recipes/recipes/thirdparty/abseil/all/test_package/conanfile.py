# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake


class AbseilTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def build(self):
        pass

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_abseilTest_INCLUDE"] = \
            os.path.join(self.install_folder, "conan_paths.cmake")

        # Abseil requires at least C++11 (see absl/base/policy_checks.h).
        # If `CMAKE_CXX_STANDARD` is not set, the compiler's default C++
        # standard will be used. While this works fine with MSVC and GCC, where
        # the compiler's version is bound to a specific default C++ standard,
        # in macOS, the default C++ standard is C++98, which Abseil does not
        # support.
        cmake.definitions['CMAKE_CXX_STANDARD'] = 11

        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
