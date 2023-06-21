# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
from os import path
from jinja2 import Environment, FileSystemLoader
from semver import SemVer

class CUDAConan(ConanFile):
    name = "CUDA"
    settings = "os", "arch"
    description = "NVIDIA CUDA SDK"
    url = "https://developer.nvidia.com/cuda-toolkit-archive"
    license = "CUDA-Toolkit-EULA"
    author = "NVIDIA"
    revision_mode = "scm"

    exports_sources = "*.cmake.in"
    no_copy_source = True

    package_originator = "External"
    package_exportable = False

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    
    def configure(self):
        if not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Unsupported operating system!")

        return super().configure()


    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'])


    def build(self):
        self.output.info("Nothing to build, progress to packaging...")


    def _produce_config_files(self):
        if not path.exists(path.join(self.package_folder, "cmake")):
            os.makedirs(path.join(self.package_folder, "cmake"))

        postfix = "" if self.settings.os == "Macos" else "md"

        # this is only used on Linux
        libsuffix = ".dll" if self.settings.os == "Windows" else ".so"
        libprefix = "bin/" if self.settings.os == "Windows" else "lib64/lib"

        # Set the library name for nvrtc, which changes for different CUDA versions on Windows
        if self.settings.os == "Linux":
            nvrtc_lib_name = "libnvrtc.so"
        elif self.settings.os == "Windows":
            nvrtc_win_lib_name_dict = {
                "11.1.1": "nvrtc64_111_0.dll",
                "11.3.1": "nvrtc64_112_0.dll",
                "11.4.1": "nvrtc64_112_0.dll",
                "11.8.0": "nvrtc64_112_0.dll"
            }
            nvrtc_lib_name = nvrtc_win_lib_name_dict.get(self.version)
            if nvrtc_lib_name is None:
                raise ConanInvalidConfiguration(f"nvrtc library name for CUDA {self.version} not found in dictionary.")

        v = SemVer(self.version, False)
        data = {
            "version_major": v.major,
            "version_minor": v.minor,
            "version_patch": v.patch,
            "os": self.settings.os,
            "libsuffix": libsuffix,
            "libprefix": libprefix,
            "nvrtc_lib_name": nvrtc_lib_name
        }

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(file_name + ".in")
            template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))

        _config_file("CUDAConfig.cmake")
        _config_file("CUDAConfigVersion.cmake")
        _config_file("CUDA_Targets.cmake")


    def package(self):
        self._produce_config_files()

        libs = [
            'cublas', 'cublasLt',
            'cudart',
            'cufft',
            'curand',
            'cusparse',
            'cusolver',
            'nvrtc', 'nvrtc-builtins'
        ]

        if self.settings.os == "Linux":
            src_path = os.path.join(self.source_folder, self._source_subfolder, "linux-x64-x86-release")
            lib_path = os.path.realpath(os.path.join(src_path, "lib64"))
            self.copy(pattern="bin/*", src=src_path, keep_path=True, symlinks=True)
            for l in libs:
                self.copy(pattern=f"lib{l}.so*", dst="lib64", src=lib_path, keep_path=True, symlinks=True)
            self.copy(pattern=f"stubs/libcuda.so*", dst="lib64", src=lib_path, keep_path=True, symlinks=True)
            self.copy(pattern=f"libcudadevrt.a", dst="lib64", src=lib_path, keep_path=True, symlinks=True)
            self.copy(pattern=f"libcudart_static.a", dst="lib64", src=lib_path, keep_path=True, symlinks=True)
            self.copy(pattern=f"libnvToolsExt.so*", dst="lib64", src=lib_path, keep_path=True, symlinks=True)
        elif self.settings.os == "Windows":
            src_path = os.path.join(self.source_folder, self._source_subfolder, "win-x64-x86-release")
            self.copy(pattern="bin/*.exe", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="bin/nvcc.profile", src=src_path, keep_path=True, symlinks=True)
            for l in libs:
                self.copy(pattern=f"bin/{l}64*.dll", src=src_path, keep_path=True, symlinks=True)
                self.copy(pattern=f"lib/x64/{l}.lib", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="lib/x64/cuda.lib", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="lib/x64/cudadevrt.lib", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="lib/x64/cudart_static.lib", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="bin/nvToolsExt64_1.dll", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern="lib/x64/nvToolsExt64_1.lib", src=src_path, keep_path=True, symlinks=True)

        bin_path = os.path.join(src_path, "bin", "crt")
        self.copy(pattern="*", dst="bin/crt", src=bin_path, keep_path=True, symlinks=True)

        doc_path = os.path.join(src_path, "documentation")
        self.copy(pattern="*", dst="documentation", src=doc_path, keep_path=True, symlinks=True)

        inc_path = os.path.realpath(os.path.join(src_path, "include"))
        self.copy(pattern="*", dst="include", src=inc_path, keep_path=True, symlinks=True)
        
        nvvm_path = os.path.realpath(os.path.join(src_path, "nvvm"))
        self.copy(pattern="*", dst="nvvm", src=nvvm_path, keep_path=True, symlinks=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
