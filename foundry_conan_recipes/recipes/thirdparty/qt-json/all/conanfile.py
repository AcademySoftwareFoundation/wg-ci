# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake, tools

class QTJSONConan(ConanFile):
    name = "QtJSON"
    license = "BSD-2-Clause-FreeBSD"
    author = "Eeli Reilin"
    url = "https://github.com/qt-json/qt-json"
    description = "The qt-json project is a simple collection of functions for parsing and serializing JSON data to and from QVariant hierarchies."
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = { "shared": False, "fPIC": True }
    generators = "cmake_paths"
    revision_mode = "scm"
   
    package_originator = "External"
    package_exportable = True
    exports_sources = "*"

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.version == "20121115":
            # See the Nuke conanfile for an explanation of why we're the Linux build
            # is using a different version
            if self.settings.os == "Linux" and self.settings.build_type == "Release":
                self.requires("Qt/5.12.1-fn.6@foundry/centos74")
            else:
                self.requires("Qt/5.12.1-fn.5@foundry/stable")
        elif self.version == "20180212":
            self.requires("Qt/5.15.2")

    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        version_data = self.conan_data["sources"][self.version]
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["CMAKE_PROJECT_QtJSON_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        # disable all RPATHs so that build machine paths do not appear in binaries
        cmake.definitions["CMAKE_SKIP_RPATH"] = "1"
        source_folder = path.join(self.source_folder,
            self._source_subfolder).replace("\\","/")
        cmake.definitions["QtJSON_SRC_PREFIX"] = source_folder

        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
  
    def package_info(self):
        self.cpp_info.libs = [ "QtJSON" ] 
