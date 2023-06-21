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
        cmake.definitions["shared_openjpeg"] = self.options["OpenJPEG"].shared
        if tools.Version(self.deps_cpp_info["OpenJPEG"].version) < tools.Version("2.1.1"):
            cmake.definitions["openjpeg_import_target"] = "OpenJPEG::OpenJPEG"
        else:
            cmake.definitions["openjpeg_import_target"] = "openjp2"
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)

