# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, CMake
import shutil

class LibpngConan(ConanFile):
    name = "PNG"
    license = "Libpng"
    author = "Guy Eric Schalnat"
    url = "http://www.libpng.org/pub/png/libpng.html"
    description = "PNG provides support for the Portable Network Graphics format (PNG), a format for storing bitmapped (raster) images on computers."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake_paths"
    exports_sources = "*"
    no_copy_source = True
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    requires = ["zlib/[~1.2.11]@thirdparty/development"]

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _library_name(self):
        if self.settings.os == "Windows":
            major, minor, _ = self.version.split('.')
            debug = "d" if self.settings.build_type == "Debug" else ""
            lib_name = "libpng{}{}_static{}".format(major, minor, debug)
            return [lib_name, lib_name + ".lib"]
        else:
            # Note that the second name, used for linkage must not be "lib"-prefixed as Mac & Linux prepend "lib" implicitly.
            return ["libpng", "png"]

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_libpng_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["PNG_SHARED"] = "OFF"
        cmake.definitions["PNG_STATIC"] = "ON"
        cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"

        if self.settings.build_type == "Debug":
            cmake.definitions["PNG_DEBUG"] = "ON"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        if "arm" in self.settings.arch:
            cmake.definitions["PNG_ARM_NEON"] = "on"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"

        tokens = {}
        tokens["LIBPNG_LIBTYPE"] = "STATIC"
        tokens["LIBPNG_LIBEXT"] = ".lib" if is_windows else ".a"
        tokens["LIBPNG_LIBNAME"] = self._library_name[0]

        tokens["LIBPNG_LINUX_LNK_LIBS"] = "" if self.version < "1.6" else "m"

        config_in_path = os.path.join(self.source_folder, "PNGConfig.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "PNGConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        lib_path = os.path.join(self.package_folder, "lib")

        # remove pkgconfig folder
        pkgfolder = os.path.join(lib_path, "pkgconfig")
        if os.path.isdir(pkgfolder):
            shutil.rmtree(pkgfolder)

        self._write_cmake_config_file()

    def package_info(self):
        self.cpp_info.libs = [self._library_name[1]] + self.deps_cpp_info["zlib"].libs
