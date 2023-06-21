# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools, CMake
from jinja2 import Environment, FileSystemLoader
from semver import SemVer


class clFFTConan(ConanFile):
    name = "clFFT"
    settings = "os", "build_type", "arch"
    description = "Open-source OpenCL library for discrete Fast Fourier Transforms"
    url = "https://github.com/clMathLibraries/clFFT"
    license = "Apache-2.0"
    author = "AMD originally, open-source nowadays"
    revision_mode = "scm"

    exports_sources = ["*.cmake.in"]
    generators = "cmake_paths"
    no_copy_source = True

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def requirements(self):
        if self.settings.os != "Macos":
            self.requires("OpenCL/2021.7.1@thirdparty/development")

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'],)
        git.checkout(version_data['git_hash'])

    def _configure_cmake(self):
        cmake = CMake(self)
        if self.settings.os == "Windows":
            cmake.definitions["CMAKE_CXX_FLAGS"] = "/DCL_TARGET_OPENCL_VERSION=120"
        elif self.settings.os == "Linux":
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-DCL_TARGET_OPENCL_VERSION=120"
        cmake.definitions["CMAKE_PROJECT_clFFT_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        cmake.definitions["BUILD64"] = "ON"
        cmake.definitions["BUILD_TEST"] = "OFF"
        cmake.definitions["BUILD_CLIENT"] = "OFF"
        cmake.definitions["BUILD_CALLBACK_CLIENT"] = "OFF"
        cmake.definitions["BUILD_LOADLIBRARIES"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder, "src"))
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
        
        _config_file("clFFTConfig.cmake")
        _config_file("clFFTConfigVersion.cmake")
        _config_file("clFFT_Targets.cmake")


    def package(self):
        self._produce_config_files()

        src_include_path = os.path.join(self.source_folder, self._source_subfolder, "src", "include")
        build_include_path = os.path.join(self.build_folder, "include")
        build_staging_path = os.path.join(self.build_folder, "staging")
        build_library_path = os.path.join(self.build_folder, "library")

        self.copy(pattern="clFFT.h", src=src_include_path, dst="include", keep_path=True, symlinks=True)
        self.copy(pattern="clFFT.version.h", src=build_include_path, dst="include", keep_path=True, symlinks=True)
        self.copy(pattern="libclFFT.so*", src=build_library_path, dst="lib64", keep_path=True, symlinks=True)
        self.copy(pattern="libclFFT*.dylib", src=build_library_path, dst="lib64", keep_path=True, symlinks=True)
        self.copy(pattern="clFFT.lib", src=build_library_path, dst="lib64", keep_path=True, symlinks=True)
        self.copy(pattern="clFFT.dll", src=build_staging_path, dst="bin", keep_path=True, symlinks=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
