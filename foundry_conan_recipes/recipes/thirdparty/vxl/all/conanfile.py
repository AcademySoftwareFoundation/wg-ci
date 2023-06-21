# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os, shutil
from conans import ConanFile, CMake, tools
from semver import SemVer
from os import path

class VXLConan(ConanFile):
    name = "VXL"
    license = "BSD-3-Clause"
    author = "https://vxl.github.io/developers.html"
    url = "https://a_gitlab_url/libraries/conan/thirdparty/vxl"
    description = "VXL (the Vision-something-Libraries) is a collection of C++ libraries designed for computer vision research and implementation."
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = { "shared": False, "fPIC": True }
    exports_sources = "*.cmake.in"
    generators = "cmake_paths"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    @property
    def _run_unit_tests(self):
        return "VXL_RUN_UNITTESTS" in os.environ

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_CONTRIB"] = "OFF"
        cmake.definitions["BUILD_CORE_SERIALISATION"] = "OFF"
        cmake.definitions["BUILD_CORE_IMAGING"] = "OFF"

        cmake.definitions["CMAKE_CXX_STANDARD"] = "11"
        cmake.definitions["CMAKE_CXX_STANDARD_REQUIRED"] = "ON"

        if not self.options.shared:
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        cmake.definitions["CMAKE_PROJECT_VXL_INCLUDE"] = path.join(
            self.install_folder, "conan_paths.cmake"
        )
        cmake.definitions["SOURCE_DIR"] = path.join(self.source_folder, self._source_subfolder)
        cmake.definitions["RUN_UNITTESTS"] = "ON" if self._run_unit_tests else "OFF"

        if self.settings.build_type is "Release":
            if self.settings.os is "Windows":
                cmake.definitions["CMAKE_C_FLAGS"] = "/O2"
            elif self.settings.os is "Linux":
                cmake.definitions["CMAKE_C_FLAGS"] = " -ffast-math"
            cmake.definitions["CMAKE_CXX_FLAGS"] = cmake.definitions["CMAKE_C_FLAGS"]

        # disable all RPATHs so that build machine paths do not appear in binaries
        cmake.definitions["CMAKE_SKIP_RPATH"] = "1"

        cmake.configure(
            source_folder=path.join(self.source_folder, self._source_subfolder)
        )
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test()

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        ver = SemVer(self.version, False)
        tokens = {
            "version_major": str(ver.major),
            "version_minor": str(ver.minor),
            "version_patch": str(ver.patch),
            "min_cxx_std": "cxx_std_11"
        }
        tokens["VXLLIB_LIBEXT"] = ".lib" if is_windows else ".a"

        config_in_path = os.path.join(self.source_folder, "config.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "VXLConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

        version_config_in_path = os.path.join(self.source_folder, "config_version.cmake.in")
        with open(version_config_in_path, "r") as cmake_version_config:
            cmake_version_config_contents = cmake_version_config.read()
        version_config_out_path = os.path.join(config_out_dir, "VXLConfigVersion.cmake")
        with open(version_config_out_path, "wt") as cmake_version_config:
            cmake_version_config.write(cmake_version_config_contents.format(**tokens))

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        # Remove the config files as it brings in targets it shouldn't, use the handrolled for now
        shutil.rmtree(os.path.join(self.package_folder, "share"))
        # For some reason on Windows the build produces a z.lib which really shouldn't use but gets
        # picked up by FindZLIB
        if self.settings.os == "Windows":
            os.remove(os.path.join(self.package_folder, "lib", "z.lib"))
        self._write_cmake_config_file()

    def package_info(self):
        self.cpp_info.libs = ["vxl"] # TODO: depends if it's debug or not
        self.cpp_info.includedirs = ['include']
        self.cpp_info.libdirs = ['lib']
