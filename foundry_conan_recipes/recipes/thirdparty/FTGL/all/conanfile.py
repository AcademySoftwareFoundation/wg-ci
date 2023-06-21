# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path
from conans import ConanFile, CMake, tools

class FTGLConan(ConanFile):
    name = "FTGL"
    license = "MIT"
    url = "https://sourceforge.net/projects/ftgl/"
    author = "https://a_gitlab_url/libraries/conan/thirdparty/ftgl/-/blob/master/AUTHORS"
    description = "FTGL is a free open source library to enable developers to use arbitrary fonts in their OpenGL (www.opengl.org) applications."
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [False], "fPIC": [True, False], "GLBackend": ["OpenGL", "FoundryGL"]}
    default_options = {"shared": False, "fPIC": True, "GLBackend": "OpenGL"}
    generators = "cmake_paths"
    revision_mode = "scm"
   
    package_originator = "External"
    package_exportable = True
    exports_sources = "*"

    requires = [
        "Freetype/2.10.4@thirdparty/development"
    ]

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def useFoundryGLBackend(self):
        return self.options.GLBackend == "FoundryGL"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        version_data = self.conan_data["sources"][self.version]
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def requirements(self):
        if self.useFoundryGLBackend():
            self.requires("foundrygl/0.1@common/development")

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["CMAKE_PROJECT_FTGL_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        # Disable all RPATHs so that build machine paths do not appear in binaries.
        cmake.definitions["CMAKE_SKIP_RPATH"] = "1"

        source_folder = path.join(self.source_folder,
            self._source_subfolder).replace("\\","/")
        cmake.definitions["FTGL_SRC_PREFIX"] = source_folder

        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
  
    def package_info(self):
        self.cpp_info.libs = [ "FTGL" ] 
