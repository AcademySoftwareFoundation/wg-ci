# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class TechnocraneConan(ConanFile):
    name = "Technocrane"
    version = "20210828"
    license = "BSD-3-Clause"
    author = "Technocrane s.r.o."
    url = "https://www.supertechno.com/"
    description = "An API to read data from a robotic crane produced by Technocrane s.r.o"
    settings = "os", "compiler", "arch"
    generators = "cmake_paths"
    revision_mode = "scm"
    package_originator = "External"
    package_exportable = False
    exports_sources = "TechnocraneConfig.cmake"

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Technocrane SDK is only available on Windows")

    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        version_data = self.conan_data["sources"][self.version]
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def package(self):
        sdk_path = os.path.join(self._source_subfolder, "Source", "ThirdParty", "TechnocraneSDK")
        self.copy("*.h", dst="include", src=os.path.join(sdk_path, "include"))
        lib_path = os.path.join(sdk_path, "lib", "Win64")
        self.copy("*.lib", dst="lib", src=lib_path, keep_path=False)
        self.copy("*.dll", dst="bin", src=lib_path, keep_path=False)
        self.copy("TechnocraneConfig.cmake", dst="cmake", src = self.source_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["TechnocraneLib.lib"]

