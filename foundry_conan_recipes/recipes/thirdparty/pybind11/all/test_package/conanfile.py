# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class Pybind11TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_pybind11Test_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["PYTHON_VERSION"] = self.deps_cpp_info["Python"].version

        is_python2 = tools.Version(self.deps_cpp_info['Python'].version) < '3.0.0'
        is_debug = self.settings.build_type == 'Debug'
        is_windows = self.settings.os == 'Windows'

        # Python 2 debug builds on Windows search for `_d.pyd` files instead of `.pyd` files. The
        # suffix needs to be set.
        cmake.definitions['_LIB_DEBUG_POSTFIX'] = ('_d' if is_python2 and is_debug and is_windows
                                                   else '')

        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
