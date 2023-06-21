# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
from conans import ConanFile, tools, CMake
from conans.tools import Version

from jinja2 import Template


class OpenJPEGConan(ConanFile):
    name = "OpenJPEG"
    license = "BSD-2-Clause"
    author = "David Janssens"
    url = "https://www.openjpeg.org/"
    description = "OpenJPEG is an open-source JPEG 2000 codec written in C language"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    exports_sources = "*"
    no_copy_source = False
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _library_name(self):
        if self.settings.os == 'Windows':
            return "openjpeg"
        else:
            return "libopenjpeg"

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)

        # Don't build the CODEC executables (means the third party libs are
        # not required)
        cmake.definitions["BUILD_CODEC"] = "OFF"

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.options.shared and self.settings.os == "Macos":
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _write_cmake_config_file(self):
        p = os.path.join(self.package_folder, "cmake")
        os.makedirs(p, exist_ok=True)

        def _configure(file_name):
            is_windows = self.settings.os == "Windows"
            is_linux = self.settings.os == "Linux"
            tokens = {}
            tokens["os"] = self.settings.os
            tokens["ver"] = Version(self.version)
            tokens["libtype"] = "SHARED" if self.options.shared else "STATIC"
            if self.options.shared:
                tokens["libext"] = ".dll" if is_windows else ".so" if is_linux else ".dylib"
            else:
                tokens["libext"] = ".lib" if is_windows else ".a"

            tokens["libname"] = self._library_name

            with open(os.path.join(self.source_folder, file_name + ".in")) as file_:
                f = file_.read()
                template = Template(f)

            template.stream(tokens).dump(os.path.join(self.package_folder, "cmake", file_name))

        _configure("OpenJPEGConfig.cmake")


    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        if Version(self.version) < Version("2.1.1"):
            bin_path = os.path.join(self.package_folder, "bin")
            share_path = os.path.join(self.package_folder, "share")

            # remove pkgconfig folder
            pkgfolder = os.path.join(share_path, "pkgconfig")
            if os.path.isdir(pkgfolder):
                shutil.rmtree(pkgfolder)

            # remove the packaged CRT dll's that get installed under
            # windows
            if self.settings.os == "Windows":
                for binary in os.listdir(bin_path):
                    if binary != "{}.dll".format(self._library_name):
                        os.remove(os.path.join(bin_path, binary))

            self._write_cmake_config_file()

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = ["OpenJPEG"]

        if not self.options.shared:
            self.cpp_info.defines = ["OPJ_STATIC"]
