# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class GlfwConan(ConanFile):
    name = "glfw"
    license = "Zlib"
    author = "Camilla Löwy"
    url = "https://github.com/glfw/glfw"
    description = \
        "GLFW is an Open Source, multi-platform library for OpenGL, OpenGL ES " \
        "and Vulkan application development. It provides a simple, platform-" \
        "independent API for creating windows, contexts and surfaces, reading " \
        "input, handling events, etc."

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "cmake*"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"], branch="master")
        git.checkout(version_data["git_hash"])

    def build(self):
        cmake = CMake(self)

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        cmake_src_path = os.path.join(self.source_folder, "cmake", "glfwConfig.cmake.in")
        file_content = open(cmake_src_path, "r").read()

        tokens = {}
        tokens["GLFW_LIBTYPE"] = "SHARED" if self.options.shared else "STATIC"
        tokens["GLFW_APPLE_SUFFIX"] = "dylib" if self.options.shared else "a"
        tokens["GLFW_UNIX_SUFFIX"] = "so" if self.options.shared else "a"
        tokens["GLFW_WIN32_SUFFIX"] = "lib"

        file_content = file_content.format(**tokens)

        cmake_dst_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(cmake_dst_dir):
            os.makedirs(cmake_dst_dir)

        cmake_dst_path = os.path.join(cmake_dst_dir, "glfwConfig.cmake")
        with open(cmake_dst_path, "w") as dst_file:
            dst_file.write(file_content)

    def package_info(self):
        self.cpp_info.libs = ["glfw"]
