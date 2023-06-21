# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools
from semver import SemVer
from jinja2 import Environment, FileSystemLoader

# Adapted from the conanfile provided by the project itself
class CbloscConan(ConanFile):
    name = "Blosc"
    version = "1.14.3"
    description = "An extremely fast, multi-threaded, meta-compressor library"
    license = "BSD-3-Clause"
    url = "https://github.com/Blosc/c-blosc"
    author = "Blosc Development Team"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": False}
    generators = "cmake_paths"
    exports_sources = "*.cmake.in"
    revision_mode = "scm"
    package_originator = "External"
    package_exportable = True

    def requirements(self):
        if not self.options.shared:
            self.requires("zlib/1.2.11@thirdparty/development")

    def build_requirements(self):
        if self.options.shared:
            self.build_requires("zlib/1.2.11@thirdparty/development")

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        self.options["zlib"].shared = False

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["CMAKE_PROJECT_blosc_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON" if self.options.fPIC else "OFF"
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.definitions["BUILD_BENCHMARKS"] = "OFF"
        cmake.definitions["BUILD_SHARED"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["BUILD_STATIC"] = "OFF" if self.options.shared else "ON"
        cmake.definitions["PREFER_EXTERNAL_ZLIB"] = "ON"
        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _produce_config_files(self):
        if not os.path.exists(os.path.join(self.package_folder, "cmake")):
            os.makedirs(os.path.join(self.package_folder, "cmake"))

        v = SemVer(self.version, True)
        data = {
            "version_major": v.major,
            "version_minor": v.minor,
            "version_patch": v.patch,
            "win" : self.settings.os == "Windows",
            "shared" : self.options.shared,
            "shsuffix": ".dylib" if self.settings.os == "Macos" else ".so",
        }

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(file_name + ".in")
            template.stream(data).dump(os.path.join(self.package_folder, "cmake", file_name))

        _config_file("BloscConfig.cmake")
        _config_file("BloscConfigVersion.cmake")

    def package(self):
        self._produce_config_files()

        # Files end up in the wrong directories using:
        #   cmake = self._configure_cmake()
        #   cmake.install()
        # Instead, the Blosc developers provided the following:

        self.copy("blosc.h", dst="include", src=self._source_subfolder+"/blosc")
        self.copy("blosc-export.h", dst="include", src=self._source_subfolder+"/blosc")
        self.copy("*libblosc.a", dst="lib", keep_path=False)


        if self.options.shared:
            self.copy("*/blosc.lib", dst="lib", keep_path=False)
            self.copy("*blosc.dll", dst="bin", keep_path=False)
            self.copy("*blosc.*dylib*", dst="lib", keep_path=False, symlinks=True)
            self.copy("*blosc.so*", dst="lib", keep_path=False, symlinks=True)
            self.copy("*libblosc.dll.a", dst="lib", keep_path=False) # Mingw
        else:
            self.copy("*libblosc.lib", dst="lib", src="", keep_path=False)

    def package_info(self):
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            self.cpp_info.libs = ["libblosc"]
        else:
            self.cpp_info.libs = ["blosc"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

