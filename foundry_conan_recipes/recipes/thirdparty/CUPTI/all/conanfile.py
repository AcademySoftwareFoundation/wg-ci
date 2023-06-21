# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from os import makedirs, path
from jinja2 import Environment, FileSystemLoader
from semver import SemVer

class CUPTIConan(ConanFile):
    name = "CUPTI"
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

    def requirements(self):
        self.requires("CUDA/{}@thirdparty/development".format(self.version))

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def configure(self):
        if self.settings.os not in ["Windows", "Linux"]:
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
            makedirs(path.join(self.package_folder, "cmake"))

        # the cupti shared library on windows is suffixed with a yearly version, this
        # maps helps us to go from cuda semver to these yearly versions making easier
        # to support the cmake templates.
        version_mapping = {
            "11.3.1": "2021.1.1",
            "11.4.1": "2021.2.1",
        }

        v = SemVer(self.version, False)
        data = {
            "version_major": v.major,
            "version_minor": v.minor,
            "version_patch": v.patch,
            "version_year": version_mapping.get(self.version, ""),
            "os": self.settings.os,
        }

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(file_name + ".in")
            template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))

        _config_file("CUPTIConfig.cmake")
        _config_file("CUPTIConfigVersion.cmake")
        _config_file("CUPTI_Targets.cmake")

    def package(self):
        self._produce_config_files()

        os_token = "linux" if self.settings.os == "Linux" else "win"
        src_path = path.join(self.source_folder, self._source_subfolder,
                             f"{os_token}-x64-x86-release", "extras", "CUPTI")
        self.copy(pattern="lib64/*", src=src_path, keep_path=True, symlinks=True)

        self.copy(pattern="doc/*", src=src_path, keep_path=True, symlinks=True)
        self.copy(pattern="include/*", src=src_path, keep_path=True, symlinks=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
