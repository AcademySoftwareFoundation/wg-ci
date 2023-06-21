# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os
from jinja2 import Environment, FileSystemLoader
from semver import SemVer


class OpenCLConan(ConanFile):
    name = "OpenCL"
    settings = "os", "arch"
    description = "Khronos OpenCL SDK"
    url = "https://github.com/KhronosGroup/OpenCL-SDK"
    license = "Apache-2.0"
    author = "The Khronos Group"
    revision_mode = "scm"

    exports_sources = "*.cmake.in"
    no_copy_source = True

    package_originator = "External"
    package_exportable = True
    short_paths = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def configure(self):
        if not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Unsupported operating system! No need to build OpenCL on MacOS.")

        return super().configure()

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'],)
        git.checkout(version_data['git_hash'])
        git.checkout_submodules(submodule="recursive")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _produce_config_files(self):
        if not os.path.exists(os.path.join(self.package_folder, "cmake")):
            os.makedirs(os.path.join(self.package_folder, "cmake"))

        postfix = "" if self.settings.os == "Macos" else "md"

        # this is only used on Linux
        libsuffix = ".dll" if self.settings.os == "Windows" else ".so"
        libprefix = "bin/" if self.settings.os == "Windows" else "lib64/lib"

        v = SemVer(self.version, False)
        data = {
            "version_major": v.major,
            "version_minor": v.minor,
            "version_patch": v.patch,
            "os": self.settings.os,
            "libsuffix": libsuffix,
            "libprefix": libprefix,
        }

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(file_name + ".in")
            template.stream(data).dump(os.path.join(self.package_folder, "cmake", file_name))

        _config_file("OpenCLConfig.cmake")
        _config_file("OpenCLConfigVersion.cmake")
        _config_file("OpenCL_Targets.cmake")


    def package(self):
        self._produce_config_files()

        cmake = self._configure_cmake()
        cmake.install()

        cl_headers_path = os.path.join(self.source_folder, self._source_subfolder, "external", "OpenCL-Headers")
        self.copy(pattern="CL/*", src=cl_headers_path, dst="include", keep_path=True, symlinks=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
