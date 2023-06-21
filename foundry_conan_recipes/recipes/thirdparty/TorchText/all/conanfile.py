# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class TorchTextConan(ConanFile):
    name = "torchtext"
    url = "https://pytorch.org/text/stable/index.html"
    author = "TorchText contributors"
    description = "The torchtext package consists of data processing utilities and popular datasets for natural language."
    topics = ("machine learning")
    settings = "os", "compiler", "build_type", "arch"
    license = "BSD-3-Clause"
    generators = "cmake_paths"
    revision_mode = "scm"
    exports_sources = ["TorchTextConfig.cmake"]
    package_originator = "External"
    package_exportable = True

    options = {
        "shared": [True]
    }

    default_options = {
        "shared": True
    }

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def configure(self):
        if self.settings.os == "Windows" or self.settings.os == "Linux":
            self.options["PyTorch"].cuda_version="11.1"
            self.options["PyTorch"].cudnn_version="8.4.1"
            
        if "arm" in self.settings.arch:
            self.options["PyTorch"].use_mkl=False
            self.options["PyTorch"].use_openmp=False

    def requirements(self):
        self.requires("PyTorch/1.12.1@thirdparty/development")
        
    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TORCHTEXT_PYTHON_EXTENSION"] = "OFF"
        cmake.definitions["CMAKE_PROJECT_torchtext_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["TORCH_INSTALL_PREFIX"] = self.deps_cpp_info["PyTorch"].rootpath
        cmake.definitions["SPM_ENABLE_SHARED"]="OFF" # Fixes a problem in building sentencepiece module
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    @property
    def _env(self):
        env = {}
        if self.options["PyTorch"].cuda_version:
            if self.settings.os == "Windows":
                env["NVTOOLSEXT_PATH"] = self.deps_cpp_info["CUDA"].rootpath
        return env

    def build(self):
        with tools.environment_append(self._env):
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        with tools.environment_append(self._env):
            cmake = self._configure_cmake()
            cmake.install()
            cpp_source_dir = os.path.join(self.source_folder, "{}_src".format(self.name), "torchtext", "csrc")

            """ TorchText doesn't define any install headers or clearly separate out API headers from internal ones.
            Just copy everything for now """
            self.copy("*.h", dst=os.path.join(self.package_folder, "include", "torchtext", "csrc"), src=cpp_source_dir)
            self.copy("TorchTextConfig.cmake", dst=os.path.join(self.package_folder, "cmake"), src=self.source_folder)

            src_bin_dir = os.path.join(self.install_folder, "bin")
            dst_bin_dir = os.path.join(self.package_folder, "bin")

            src_lib_dir = os.path.join(self.install_folder, "lib")
            dst_lib_dir = os.path.join(self.package_folder, "lib")

            # put all libraries in the lib dir
            for libtype in ('dll','so','dylib', 'lib'):
                self.copy("*.{}".format(libtype), dst=dst_lib_dir, src=src_lib_dir)
                self.copy("*.{}".format(libtype), dst=dst_lib_dir, src=src_bin_dir)

            # put the executables in the bin dir
            self.copy("spm_*", dst=dst_bin_dir, src=src_bin_dir)

    def package_info(self):
        self.cpp_info.libs = ['TorchText']
