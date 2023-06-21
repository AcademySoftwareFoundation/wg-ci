# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake
from conans.model.version import Version


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    requires = "OpenColorIOConfigs/0bb079c@foundry/staging"

    generators = ["cmake_paths"]

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = path.join(
            self.install_folder, "conan_paths.cmake"
        )
        cmake.definitions['ocio_configured_version'] = str(
            self.deps_cpp_info['OpenColorIO'].version)
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
