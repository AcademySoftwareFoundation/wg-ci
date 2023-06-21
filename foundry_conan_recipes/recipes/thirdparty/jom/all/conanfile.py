# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class JomConan(ConanFile):
    name = "jom"
    license = "GPL-3.0-only"
    author = "The Qt Company Ltd"
    url = "https://wiki.qt.io/Jom"
    description = "jom is a clone of nmake to support the execution of multiple independent commands in parallel."
    settings = "os", "arch", "compiler", "build_type"
    revision_mode = "scm"
    generators = "cmake_paths"

    package_originator = "External"
    package_exportable = True

    build_requires = "Qt/5.12.1-fn.5@foundry/stable"

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("jom is only applicable on Windows")

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_jom_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        # deferred until build to do this check, when the dependency graph has been fully evaluated
        if self.settings.build_type != "Release":
            raise ConanInvalidConfiguration("jom should only be built in Release")
        self._configure_cmake().build()

    def package(self):
        self._configure_cmake().install()

    def package_id(self):
        # consumers shouldn't care what jom was built with
        del self.info.settings.compiler
        del self.info.settings.build_type

    def package_info(self):
        # helper to get the jom executable (note jomd.exe in Debug, but we disallow Debug)
        self.user_info.jom_exe = os.path.join(self.cpp_info.bindirs[0], "jom.exe")
