# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = ["cmake_paths"]

    def configure(self):
        del self.settings.compiler.libcxx

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(
            self.install_folder, "conan_paths.cmake"
        )

        cmake.definitions["shared_python"] = True
        cmake.definitions["CONAN_PYTHON_VERSION"] = self.deps_cpp_info["pythontool"].version
        cmake.definitions["CONAN_PYHOME"] = path.join(self.deps_cpp_info["pythontool"].rootpath, self.deps_user_info["pythontool"].pyhome).replace("\\", "/")
        cmake.definitions["CONAN_PYTHON_INTERPRETER"] = path.join(self.deps_cpp_info["pythontool"].rootpath, self.deps_user_info["pythontool"].interpreter).replace("\\", "/")
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
