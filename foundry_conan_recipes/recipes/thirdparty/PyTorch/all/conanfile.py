# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class PyTorchConan(ConanFile):
    name = "PyTorch"
    url = "https://pytorch.org"
    author = "Adam Paszke, Sam Gross, Soumith Chintala and Gregory Chanan"
    description = "PyTorch is an open source machine learning library based on the Torch library"
    topics = ("machine learning")
    settings = "os", "compiler", "build_type", "arch"
    license = "BSD-3-Clause"

    generators = "cmake_paths"
    exports_sources = "requirements.txt"
    short_paths = True
    no_copy_source = True
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    options = {
        "shared": [True],
        "fPIC": [True, False],
        "build_binary": [True, False],
        "build_test": [True, False],
        "build_docs": [True, False],
        "build_python": [True, False],
        "cuda_arch_list" : "ANY",
        "cuda_version": [None, "10.1", "11.1"],
        "cudnn_version": [None, "8.0.5", "8.4.1"],
        "use_distributed": [True, False],
        "use_mkl": [True, False],
        "use_openmp": [True, False],
        "use_mps": [True, False], # MacOS Metal Perforamnce Shaders (MPS)
    }

    default_options = {
        "shared": True,
        "fPIC": True,
        "build_binary": False,
        "build_test": False,
        "build_docs": False,
        "build_python": False,
        "cuda_arch_list": "",
        "cuda_version": None,
        "cudnn_version": None,
        "use_distributed": False,
        "use_mkl" : True,
        "use_openmp": True,
        "use_mps" : False,
    }

    @property
    def _mps_hacks(self):
        return self.options.use_mps and self.settings.os == "Macos" and tools.Version(self.settings.compiler.version) < "14.0"

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if self.settings.os != "Macos" or self.version < "1.12.1":
            del self.options.use_mps

    def configure(self):
        if "arm" in self.settings.arch:
            if self.options.use_mkl:
                raise ConanInvalidConfiguration("MKL does not work on ARM.")
            elif self.options.use_openmp:
                raise ConanInvalidConfiguration("OpenMP does not yet work on ARM.")
                
        if not self.options.cuda_version and self.options.cudnn_version:
            raise ConanInvalidConfiguration("cuda_version must be defined to be used with CuDNN")
        # Forward cuda_version to CuDNN
        if self.options.cuda_version and self.options.cudnn_version:
            self.options["CuDNN"].cuda_version = self.options.cuda_version

        # If not set, use the following defaults for cuda_arch_list
        # Note that debug builds have a limited set of achitectures supported
        # in order to limit the build sizes and avoid linking issues
        if not self.options.cuda_arch_list:
            if self.options.cuda_version == "10.1":
                if self.settings.build_type == "Release":
                    self.options.cuda_arch_list = "3.0;3.5;3.7;5.0;5.2;6.0;6.1;7.0;7.5+PTX"
                else:
                    self.options.cuda_arch_list = "6.0;6.1;7.0;7.5+PTX"
            elif self.options.cuda_version == "11.1":
                if self.settings.build_type == "Release":
                    self.options.cuda_arch_list = "3.5;3.7;5.0;5.2;6.0;6.1;7.0;7.5;8.6+PTX"
                else:
                    self.options.cuda_arch_list = "6.0;6.1;7.0;7.5;8.6+PTX"
        if not self.options.cuda_version:
            self.options.cuda_arch_list = None

    def requirements(self):
        if self.options.cuda_version == "10.1":
            self.requires("CUDA/10.1.2@foundry/stable")
        elif self.options.cuda_version == "11.1":
            self.requires("CUDA/11.1.1@thirdparty/development")

        if self.options.cudnn_version == "8.0.5":
            self.requires("CuDNN/8.0.5@thirdparty/development")
        elif self.options.cudnn_version == "8.4.1":
            self.requires("CuDNN/8.4.1@thirdparty/development")

        if self.options.use_mkl:
            if self.version >= "1.12.0":
                self.requires("MKL/2020.4")
            else:
                self.requires("MKL/2019.5.281@thirdparty/development")

    def build_requirements(self):
        if self.settings.os == "Macos" and self.options.use_mkl and self.options.use_openmp:
            # As Macos lacks omp.h it needs the OpenMP package for this
            self.build_requires("LLVM-OpenMP/5.0.0@thirdparty/development")

        if not self.options.use_mkl:
            # If not using mkl, use eigen for BLAS
            self.build_requires("eigen/3.4.0@")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")

    @staticmethod
    def _get_state_str(boolean):
        return "ON" if boolean else "OFF"

    def _configure_cmake(self):
        cmake = CMake(self)
        if self.settings.os == "Macos":
            if self.options.use_mkl:
                # LLVM and MKL have OMP dylibs in, and we want to ensure MKL is found
                cmake.definitions["CMAKE_PREFIX_PATH"] = self.deps_cpp_info["MKL"].rootpath
        else:
            cmake.definitions["CMAKE_PROJECT_Torch_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

        cmake.definitions["BUILD_BINARY"] = self._get_state_str(self.options.build_binary)
        cmake.definitions["BUILD_TEST"] = self._get_state_str(self.options.build_test)
        cmake.definitions["BUILD_DOCS"] = self._get_state_str(self.options.build_docs)
        cmake.definitions["BUILD_PYTHON"] = self._get_state_str(self.options.build_python)
        cmake.definitions["USE_CUDA"] = "ON" if self.options.cuda_version else "OFF"
        cmake.definitions["USE_CUDNN"] = "ON" if self.options.cudnn_version else "OFF"
        cmake.definitions["USE_OPENMP"] = self._get_state_str(self.options.use_openmp)
        cmake.definitions["USE_MKL"] = self._get_state_str(self.options.use_mkl)

        mps_enabled = tools.Version(self.version) >= "1.12.1" and self.settings.os == "Macos" and self.options.use_mps
        if mps_enabled:
            cmake.definitions["USE_MPS"] = "ON"
            cmake.definitions["USE_FBGEMM"] = "OFF"  # TODO Issue with FBGEMM failing to compile when using Xcode14, so disabling

        cmake.definitions["USE_DISTRIBUTED"] = self._get_state_str(self.options.use_distributed)
        if self.options.use_mkl:
            cmake.definitions["BLAS"] = "MKL"
        else:
            cmake.definitions["BLAS"] = "Eigen"

        if self.options.cuda_version:
            # Force the CUDA arch list (as the setup.py doesn't propagate this to cmake)
            cmake.definitions["TORCH_CUDA_ARCH_LIST"] = str(self.options.cuda_arch_list)

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        if self.settings.os == "Macos":
            if self.options.use_mkl and self.options.use_openmp:
                # Force LLVM-OpenMP oon Macos (as this isn't supported by default)
                cmake.definitions["OPENMP_FOUND"] = "TRUE"
                cmake.definitions["MKL_OPENMP_LIBRARY"] = os.path.join(self.deps_cpp_info["MKL"].rootpath, "lib","libiomp5.dylib")
                cmake.definitions["OpenMP_libomp_LIBRARY"] = cmake.definitions["MKL_OPENMP_LIBRARY"]
                cmake.definitions["OpenMP_C_LIB_NAMES"] = "libomp"
                cmake.definitions["OpenMP_CXX_LIB_NAMES"] = "libomp"
                # Add sources to include path so that omp.h is on the include path
                cmake.definitions["OpenMP_C_FLAGS"] = "-Xpreprocessor -fopenmp -I{}".format(self.deps_cpp_info["LLVM-OpenMP"].include_paths[0])
                cmake.definitions["OpenMP_CXX_FLAGS"] = "-Xpreprocessor -fopenmp -I{}".format(self.deps_cpp_info["LLVM-OpenMP"].include_paths[0])
                 # Force the DNNL library to use OMP threading runtime (as it defaults to sequential which causes performance problems)
                cmake.definitions["DNNL_CPU_THREADING_RUNTIME"] = "OMP"
                cmake.definitions["DNNL_CPU_RUNTIME"] = "OMP"

            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    @property
    def local_pip_dir(self):
        return os.path.join(self.build_folder, 'build_packages')

    @property
    def _env(self):
        env = {'PYTHONPATH': self.local_pip_dir}
        if self.options.cuda_version:
            if self.settings.os == "Windows":
                env["NVTOOLSEXT_PATH"] = self.deps_cpp_info["CUDA"].rootpath
        return env

    def build(self):
        # install the packages into a local directory
        # these packages are required during the configuration time.
        self.run(f'pip install --target {self.local_pip_dir} -r {self.source_folder}/requirements.txt')

        with tools.environment_append(self._env):
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        with tools.environment_append(self._env):
            cmake = self._configure_cmake()
            cmake.install()

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = ["PyTorch"]
