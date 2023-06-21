# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from os import path, makedirs
from jinja2 import Environment, FileSystemLoader
from semver import SemVer

class cuDNNConan(ConanFile):
    name = "CuDNN"
    settings = "os", "arch"
    description = "The NVIDIA CUDA® Deep Neural Network library (cuDNN) is a GPU-accelerated library of primitives for deep neural networks."
    url = "https://developer.nvidia.com/cudnn"
    license = "NVIDIA-CuDNN-SLA"
    author = "NVIDIA"
    revision_mode = "scm"

    options = {"cuda_version": ["10.1", "11.1", "11.x"]}

    exports_sources = "*.cmake.in"
    no_copy_source = True

    package_originator = "External"
    package_exportable = False

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)


    def requirements(self):
        if self.options.cuda_version == "10.1":
            self.requires("CUDA/10.1.2@foundry/stable")
        elif self.options.cuda_version == "11.1" or self.options.cuda_version =="11.x":
            self.requires("CUDA/11.1.1@thirdparty/development")

    
    def configure(self):
        if not self.settings.os in ["Linux", "Windows"]:
            raise ConanInvalidConfiguration("Unsupported operating system!")
        
        if not self.options.cuda_version:
            raise ConanInvalidConfiguration("Unspecified 'cuda_version' option!")

        cuda_versions = self.conan_data["sources"][self.version]
        if f"cuda{self.options.cuda_version}" not in cuda_versions:
            raise ConanInvalidConfiguration(f"cuDNN version {self.version} does not have CUDA {self.options.cuda_version} compatible binaries!")

        return super().configure()


    def source(self):
        version_data = self.conan_data["sources"][self.version][f"cuda{self.options.cuda_version}"]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])


    def build(self):
        self.output.info("Nothing to build, progress to packaging...")


    def _produce_config_files(self):
        if not path.exists(path.join(self.package_folder, "cmake")):
            makedirs(path.join(self.package_folder, "cmake"))

        v = SemVer(self.version, False)
        data = {
            "version_major": v.major,
            "version_minor": v.minor,
            "version_patch": v.patch,
            "os": self.settings.os,
        }

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(file_name + ".in")
            template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))

        _config_file("cuDNNConfig.cmake")
        _config_file("cuDNNConfigVersion.cmake")
        _config_file("cuDNN_Targets.cmake")


    def package(self):
        self._produce_config_files()

        libs = [
            "cudnn",
            "cudnn_adv_infer", "cudnn_adv_train",
            "cudnn_cnn_infer", "cudnn_cnn_train",
            "cudnn_ops_infer", "cudnn_ops_train",
        ]

        src_path = path.join(self.source_folder, self._source_subfolder,
            "win" if self.settings.os == "Windows" else "linux"
        )

        for l in libs:
            self.copy(pattern=f"bin/{l}64*.dll", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern=f"lib/x64/{l}*.lib", src=src_path, keep_path=True, symlinks=True)
            self.copy(pattern=f"lib64/lib{l}.so*", src=src_path, keep_path=True, symlinks=True)

        self.copy(pattern="include/*", src=src_path, keep_path=True, symlinks=True)



    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
