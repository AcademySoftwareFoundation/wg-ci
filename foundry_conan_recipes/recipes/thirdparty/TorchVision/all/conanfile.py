# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class TorchVisionConan(ConanFile):
    name = "TorchVision"
    url = "https://pytorch.org/vision/stable/index.html"
    author = "Adam Paszke, Sam Gross, Soumith Chintala and Gregory Chanan"
    description = "The torchvision package consists of popular datasets, model architectures, and common image transformations for computer vision."
    topics = ("machine learning")
    settings = "os", "compiler", "build_type", "arch"
    license = "BSD-3-Clause"

    generators = "cmake_paths"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    options = {
        "shared": [True],
        "fPIC": [True, False],
        "cuda_version": [None, "10.1", "11.1"]
    }

    default_options = {
        "shared": True,
        "fPIC": True,
        "cuda_version": None
    }

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        # Forward cuda_version to Pytorch
        if self.options.cuda_version:
            self.options["PyTorch"].cuda_version = self.options.cuda_version
            if self.version >= "0.13.0":
                self.options["PyTorch"].cudnn_version = "8.4.1"
            else:
                self.options["PyTorch"].cudnn_version = "8.0.5"

        # MKL / LLVM-OpenMP aren't working on Apple Silicon
        if 'arm' in self.settings.arch:
            self.options["PyTorch"].use_mkl = False
            self.options["PyTorch"].use_openmp = False

        # Use the following defaults for Pytorch cuda_arch_list
        # Note that debug builds have a limited set of achitectures supported
        # in order to limit the build sizes and avoid linking issues
        if self.options.cuda_version == "10.1":
            if self.settings.build_type == "Release":
                self.options["PyTorch"].cuda_arch_list = "3.0;3.5;3.7;5.0;5.2;6.0;6.1;7.0;7.5+PTX"
            else:
                self.options["PyTorch"].cuda_arch_list = "6.0;6.1;7.0;7.5+PTX"
        elif self.options.cuda_version == "11.1":
            if self.settings.build_type == "Release":
                self.options["PyTorch"].cuda_arch_list = "3.5;3.7;5.0;5.2;6.0;6.1;7.0;7.5;8.6+PTX"
            else:
                self.options["PyTorch"].cuda_arch_list = "6.0;6.1;7.0;7.5;8.6+PTX"
        else:
            self.options["PyTorch"].cuda_arch_list = None

    def requirements(self):
        if self.options.cuda_version == "10.1":
            self.requires("CUDA/10.1.2@foundry/stable")
        elif self.options.cuda_version == "11.1":
            self.requires("CUDA/11.1.1@thirdparty/development")

        if self.version >= "0.13.1":
            self.requires("PyTorch/1.12.1@thirdparty/development")
            self.requires("PNG/1.6.9@thirdparty/development")
            self.requires("JPEG/6b")
        else:
            self.requires("PyTorch/1.6.0")
            self.requires("Python/3.7.7@thirdparty/development")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_torchvision_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        if self.options.cuda_version:
            cmake.definitions["WITH_CUDA"] = "ON"

        cmake.definitions["USE_PYTHON"] = "No"        

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    @property
    def _env(self):
        env = {}
        if self.options.cuda_version:
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

    def package_info(self):
        self.cpp_info.libs = ['TorchVision']
