# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake
from conans.model.version import Version


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = ["cmake_paths"]

    def configure(self):
        del self.settings.compiler.libcxx


    @property
    def _is_python3(self):
        return Version(self.requires["Python"].ref.version) >= Version("3.0.0")


    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(
            self.install_folder, "conan_paths.cmake"
        )

        cmake.definitions["shared_python"] = self.options["Python"].shared
        cmake.definitions["CONAN_PYTHON_VERSION"] = self.deps_cpp_info["Python"].version
        cmake.definitions["CONAN_PYHOME"] = path.join(self.deps_cpp_info["Python"].rootpath, self.deps_user_info["Python"].pyhome).replace("\\", "/")
        cmake.definitions["CONAN_PYTHON_INTERPRETER"] = path.join(self.deps_cpp_info["Python"].rootpath, self.deps_user_info["Python"].interpreter).replace("\\", "/")
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
