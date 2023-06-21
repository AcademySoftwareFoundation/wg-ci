# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    def test(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

        if self.options["PyTorch"].cuda_version:
            # Make sure the CUDA arch list matches the list used in PyTorch
            cmake.definitions["TORCH_CUDA_ARCH_LIST"] = str(self.options["PyTorch"].cuda_arch_list)
            # Under windows need to force the NVTOOLEXT_HOME location (otherwise looks in default location)
            if self.settings.os == "Windows":
                cmake.definitions["NVTOOLSEXT_PATH"] = self.deps_cpp_info["CUDA"].rootpath
                cmake.definitions["NVTOOLEXT_HOME"] = self.deps_cpp_info["CUDA"].rootpath

        cmake.configure()
        cmake.build()
        cmake.test(output_on_failure=True)
