# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake
from conans.errors import ConanException

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    @property
    def _useFoundryGLBackend(self):
        try:
            return self.options["GLEW"].GLBackend == "FoundryGL"
        except ConanException:
            return False

    def requirements(self):
        if self._useFoundryGLBackend:
            self.requires("foundrygl/0.1@common/development")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["shared_glew"] = self.options["GLEW"].shared
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)

