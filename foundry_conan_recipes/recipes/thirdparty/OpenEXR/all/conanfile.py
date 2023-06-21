# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from jinja2 import Environment, FileSystemLoader
import os
from os import path
from semver import SemVer
import shutil


class OpenEXR(ConanFile):
    name = "OpenEXR"
    description = "OpenEXR provides the specification and reference implementation of the EXR file format, the professional-grade image storage format of the motion picture industry."
    author = "Academy Software Foundation"
    license = "BSD-3-Clause"
    url = "https://github.com/AcademySoftwareFoundation/openexr"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}

    generators = "cmake_paths"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    build_requires = ["zlib/1.2.11@thirdparty/development"]

    @property
    def _semanticVersion(self):
        return tools.Version(self.version)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def requirements(self):
        if self._semanticVersion >= "3.0.0":
            self.requires(f"imath/{self.version}")

    def configure(self):
        if self._semanticVersion >= "3.0.0":
            self.options["imath"].shared = self.options.shared

    def export_sources(self):
        if self._semanticVersion < "3.0.0":
            self.copy("*.cmake.in")

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _config_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_DEBUG_POSTFIX"] = ""
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        if self._semanticVersion < "2.4.0":
            cmake.definitions["CMAKE_PROJECT_OpenEXR_INCLUDE"] = path.join(
                self.install_folder, "conan_paths.cmake")
            cmake.definitions["OPENEXR_BUILD_STATIC"] = "OFF" if self.options.shared else "ON"
            cmake.definitions["OPENEXR_BUILD_SHARED"] = "ON" if self.options.shared else "OFF"
            cmake.definitions["OPENEXR_BUILD_TESTS"] = "OFF"
            cmake.definitions["OPENEXR_BUILD_PYTHON_LIBS"] = "OFF"
            cmake.definitions["OPENEXR_BUILD_VIEWERS"] = "OFF"
            # for consistency with 2.4.0+ versions
            cmake.definitions["OPENEXR_NAMESPACE_VERSIONING"] = "OFF"
        elif self._semanticVersion < "3.0.0":
            # avoid having extra symlinking
            cmake.definitions["ILMBASE_LIB_SUFFIX"] = ""
            # avoid having extra symlinking
            cmake.definitions["OPENEXR_LIB_SUFFIX"] = ""
            cmake.definitions["BUILD_TESTING"] = "OFF"
            cmake.definitions["PYILMBASE_ENABLE"] = "OFF"
            cmake.definitions["CMAKE_PROJECT_OpenEXRMetaProject_INCLUDE"] = path.join(
                self.install_folder, "conan_paths.cmake")
            cmake.definitions["OPENEXR_VIEWERS_ENABLE"] = "OFF"
        else:
            # avoid having extra symlinking
            cmake.definitions["OPENEXR_LIB_SUFFIX"] = ""
            cmake.definitions["BUILD_TESTING"] = "OFF"
            cmake.definitions["CMAKE_PROJECT_OpenEXR_INCLUDE"] = path.join(
                self.install_folder, "conan_paths.cmake")
            cmake.definitions["OPENEXR_VIEWERS_ENABLE"] = "OFF"

        cmake.configure(source_folder=path.join(self.source_folder, self._source_subfolder))
        return cmake

    def _produce_config_files(self):
        if not path.exists(path.join(self.package_folder, "cmake")):
            os.makedirs(path.join(self.package_folder, "cmake"))

        postfix = "{}{}".format(
            "_s" if not self.options.shared and self._semanticVersion < "2.4.0" else "",
            "_d" if self.settings.os == "Windows" and self._semanticVersion < "2.4.0"
            and self.settings.build_type == "Debug" else "",
        )

        # this is only used on Linux
        libsuffix = ".a"
        if self.options.shared:
            libsuffix = ".dylib" if self.settings.os == "Macos" else ".so"

        data = {
            "version_major": self._semanticVersion.major,
            "version_minor": self._semanticVersion.minor,
            "version_patch": self._semanticVersion.patch,
            "os": self.settings.os,
            "bt": self.settings.build_type,
            "shared": self.options.shared,
            "libsuffix": libsuffix,  # Only valid on Mac and Linux
            "platform_postfix": postfix,
        }

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(file_name + ".in")
            template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))

        _config_file("OpenEXRConfig.cmake")
        _config_file("OpenEXRConfigVersion.cmake")
        _config_file("OpenEXR_Targets.cmake")

    def build(self):
        cmake = self._config_cmake()
        cmake.build()

    def package(self):
        cmake = self._config_cmake()
        cmake.install()
        if self._semanticVersion < "3.0.0":
            if self._semanticVersion > "2.3.0":
                shutil.rmtree(path.join(self.package_folder, "lib", "cmake"))
            self._produce_config_files()
