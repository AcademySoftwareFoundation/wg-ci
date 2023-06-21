# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools
from os import path
import shutil, os, platform
from semver import SemVer
import semver
from jinja2 import Environment, FileSystemLoader

class MKLConan(ConanFile):
    name = "MKL"
    settings = "os", "arch"
    description = "Intel MKL"
    url = "None"
    author = "Intel Corporation"
    license = "Intel-Simplified-Feb2020"

    options = {
        "shared": [True, False],
    }
    default_options = { "shared": True }

    exports_sources = "*.cmake.in"
    no_copy_source = True
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _platform_path(self):
        if self.settings.os == "Linux":
            return "linux"
        elif self.settings.os == "Macos":
            return "mac"
        elif self.settings.os == "Windows":
            return "windows"
        else:
            raise RuntimeError(f'Unknown platform {self.settings.os}')

    @property
    def _binaries_version(self):
        #
        # For some reason MKL 2018 and 2020 are using different patch versions
        # for each platform
        #
        binary_versions = {
            "2018.4": {
                "Linux": "2018.5.274",
                "Macos": "2018.5.231",
                "Windows": "2018.5.274"
            },
            "2020.4": {
                "Linux": "2020.4.304",
                "Macos": "2020.4.301",
                "Windows": "2020.4.311"
            }
        }
        if self.version in binary_versions.keys():
            return binary_versions[self.version][str(self.settings.os)]

        return self.version

    def _produce_config_files(self):
        if not path.exists(path.join(self.package_folder, "cmake")):
            os.makedirs(path.join(self.package_folder, "cmake"))

        postfix = "" if self.settings.os == "Macos" else "md"

        # this is only used on Linux
        libsuffix = ".a"
        if self.options.shared:
            libsuffix = ".dylib" if self.settings.os == "Macos" else ".so"

        v = SemVer(self._binaries_version, False)
        data = {
            "version_major": v.major,
            "version_minor": v.minor,
            "version_patch": v.patch,
            "os": self.settings.os,
            "shared": self.options.shared,
            "libsuffix": libsuffix, # Only valid on Mac and Linux
            "platform_postfix": postfix,
        }

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(file_name + ".in")
            template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))

        _config_file("MKLConfig.cmake")
        _config_file("MKLConfigVersion.cmake")
        _config_file("MKL_Targets.cmake")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        print("Nothing to build, progress to packaging...")

    def package(self):
        self._produce_config_files()

        self.copy("*.h", "include", path.join(self._source_subfolder, self._platform_path, f"compilers_and_libraries_{self._binaries_version}", self._platform_path, "mkl", "include"))

        libsuffix = "*.a"
        if self.options.shared:
            libsuffix = "*.dylib" if self.settings.os == "Macos" else "*.so"

        mkl_path = path.join(self._source_subfolder, self._platform_path, f"compilers_and_libraries_{self._binaries_version}")
        mkl_libs_path = path.join(mkl_path, self._platform_path, "mkl", "lib")
        compiler_libs_path = path.join(mkl_path, self._platform_path, "compiler", "lib")
        if self.settings.os == "Linux":
            mkl_libs_path = path.join(mkl_libs_path, "intel64")
            compiler_libs_path = path.join(compiler_libs_path, "intel64")

        if self.settings.os == "Windows":
            self.copy("*.dll", "bin", mkl_path, keep_path=False)
            self.copy("*.lib", "lib", mkl_path, keep_path=False)
        else:
            self.copy(libsuffix, "lib", compiler_libs_path, keep_path=False)
            self.copy(libsuffix, "lib", mkl_libs_path, keep_path=False)

