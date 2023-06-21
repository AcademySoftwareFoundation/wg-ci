# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def test(self):
        cmake = CMake(self)
        cmake.definitions["shared_hdf5"] = self.options["HDF5"].shared
        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)

