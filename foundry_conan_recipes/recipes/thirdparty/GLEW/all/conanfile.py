# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os, shutil
from os import path
from conans import ConanFile, tools, CMake

class GlewConan(ConanFile):
    name = "GLEW"
    license = "MIT"
    author = "Nigel Stewart"
    url = "http://glew.sourceforge.net/"
    description = """The OpenGL Extension Wrangler Library (GLEW) is a cross-platform open-source C/C++ extension loading library, 
                     which provides efficient run-time mechanisms for determining which OpenGL extensions The OpenGL Extension Wrangler 
                     Library (GLEW) is a cross-platform open-source C/C++ extension loading library. GLEW provides efficient run-time 
                     mechanisms for determining which OpenGL extensions"""
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "GLBackend" : ["OpenGL" ,"FoundryGL"],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "GLBackend" : "OpenGL",
    }
    exports_sources = "*"
    no_copy_source = True
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _useFoundryGLBackend(self):
        return self.options.GLBackend == "FoundryGL"

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)


    def build_requirements(self):
        if self._useFoundryGLBackend:
            self.build_requires("foundrygl/0.1@common/development")


    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])


    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_UTILS"] = "OFF"

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.options.shared and self.settings.os == "Macos":
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"
            if self._useFoundryGLBackend:
                cmake.definitions["FoundryGL_DIR"] = os.path.join( self.deps_cpp_info["foundrygl"].rootpath, "cmake")
                cmake.definitions["FOUNDRYGL_USE"] = True

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder, "build", "cmake"))
        return cmake


    def build(self):
        cmake = self._configure_cmake()
        cmake.build()


    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        if not self._useFoundryGLBackend:
            # we need to use/supply our own cmake files as the CMake supplied one explicitly ask for OpenGL
            shutil.rmtree(path.join(self.package_folder, "lib", "cmake"))


    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = ["GLEW"]

        if not self.options.shared:
            self.cpp_info.defines = ["GLEW_STATIC"]
            
