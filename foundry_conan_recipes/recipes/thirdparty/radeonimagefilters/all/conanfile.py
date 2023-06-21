# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools
from jinja2 import Environment, FileSystemLoader


class RadeonImageFilters(ConanFile):
    name = "radeonimagefilters"
    description = "Radeon Image Filters is a library for image filtering and post processing provided by AMD which makes the most of the hardware."
    url = "https://github.com/GPUOpen-LibrariesAndSDKs/RadeonImageFilter/"
    license = "Apache-2.0"
    author = "Advanced Micro Devices, Inc."
    settings = "os", "arch"

    exports_sources = "*.cmake.in"
    no_copy_source = True
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = False

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _platform_path(self):
        if self.settings.os == "Windows":
            return os.path.join("Windows", "Dynamic")
        elif self.settings.os == "Macos":
            if "arm" in self.settings.arch:
                return os.path.join("MacOS_ARM", "Dynamic")
            else:
                return os.path.join("OSX", "Dynamic")
        elif self.settings.os == "Linux":
            return os.path.join("CentOS7", "Dynamic")
        else:
            raise RuntimeError(f"Unsupported platform {self.settings.os}")

    @property
    def _lib_path(self):
        return os.path.join(self._source_subfolder, self._platform_path)

    def package(self):
        self.copy("RadeonImageFiltersConfig.cmake", "cmake", "cmake")

        self.copy(
            pattern="include/*",
            src=self._source_subfolder,
            keep_path=True,
            symlinks=True,
        )

        self.copy("*.dll", "bin", self._lib_path, keep_path=False)
        self.copy("*.pdb", "bin", self._lib_path, keep_path=False)
        self.copy("*.so*", "lib", self._lib_path,
                  keep_path=False, symlinks=True)
        self.copy("*.dylib", "lib", self._lib_path,
                  keep_path=False, symlinks=True)
        self.copy("*.lib", "lib", self._lib_path,
                  keep_path=False, symlinks=True)

        self.copy(
            pattern="models/*",
            src=self._source_subfolder,
            keep_path=True,
            symlinks=True,
        )

        self._write_cmake_config_file()

    def _write_cmake_config_file(self):
        os.makedirs(os.path.join(self.package_folder, "cmake"), exist_ok=True)

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            v = tools.Version(self.version)
            data = {
                "version_major": v.major,
                "version_minor": v.minor,
                "version_patch": v.patch,
                "os": self.settings.os,
                "libsuffix": "dylib" if self.settings.os == "Macos" else "so",
            }

            interpreter_template = env.get_template(file_name + ".in")
            interpreter_template.stream(data).dump(
                os.path.join(self.package_folder, "cmake", file_name)
            )

        _configure("RadeonImageFiltersConfig.cmake")
        _configure("RadeonImageFiltersConfigVersion.cmake")
        _configure("RadeonImageFilters_Targets.cmake")
