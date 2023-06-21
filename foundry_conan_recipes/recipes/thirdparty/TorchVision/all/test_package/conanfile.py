# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"

    @property
    def _env(self):
        env = {}
        if self.options["TorchVision"].cuda_version:
            if self.settings.os == "Windows":
                env["NVTOOLSEXT_PATH"] = self.deps_cpp_info["CUDA"].rootpath
        return env

    def test(self):
        with tools.environment_append(self._env):
            cmake = CMake(self)
            cmake.definitions["CMAKE_PROJECT_PackageTest_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
            if self.settings.os == "Linux" and self.options["TorchVision"].cuda_version:
                # Work around as under Linux its looking for libcuda.so.1 rather than libcuda.so (so create a symlink)
                lib_path = os.path.join(self.deps_cpp_info["CUDA"].rootpath, "lib64", "stubs")
                if not os.path.exists(os.path.join(lib_path, "libcuda.so.1")):
                    os.symlink(os.path.join(lib_path, "libcuda.so"), os.path.join(lib_path, "libcuda.so.1"))

                # On 0.13.1 we also need cusolver symlink in pytorch
                if self.deps_cpp_info["TorchVision"].version >= "0.13.0":
                    if not os.path.exists(os.path.join(lib_path, "libcusolver.so.11")):
                        os.symlink(os.path.join(lib_path, "libcusolver.so"), os.path.join(lib_path, "libcusolver.so.11"))

            cmake.configure()
            cmake.build()
            cmake.test(output_on_failure=True)
