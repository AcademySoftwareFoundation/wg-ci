# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake
class TestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["CMAKE_MODULE_PATH"] = path.join(self.deps_cpp_info["FlatBuffers"].rootpath + "/lib/cmake/flatbuffers")
        # Need to have the full path to "flatc" as it is not in the PATH.
        cmake.definitions["FLATBUFFERS_FLATC_EXECUTABLE"] = self.deps_cpp_info["FlatBuffers"].rootpath + "/bin/flatc" 
        unescaped_path = path.join(self.source_folder, "Game.fbs")
        cmake.definitions["CMAKE_SCHEMA_FILE"] = unescaped_path.replace("\\", "\\\\") if self.settings.os == "Windows" else unescaped_path
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
