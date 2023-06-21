# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, CMake
from jinja2 import Environment, FileSystemLoader


class PartioConan(ConanFile):
    name = "Partio"
    settings = "os", "compiler", "build_type", "arch"
    description = "Partio is an open source C++ library for reading, writing and manipulating a variety of standard particle formats."
    license = "BSD-3-Clause"
    author = "Walt Disney Animation Studios"
    url = "http://partio.us"
    revision_mode = "scm"
    generators = "cmake_paths"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    package_originator = "External"
    package_exportable = True
    exports_sources = ("PartioConfig.cmake.in")

    requires = [
        "zlib/[~1.2.11]@thirdparty/development",
    ]

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
        
        if not self.options.shared:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = 'ON'

        cmake.definitions["PARTIO_BUILD_SHARED_LIBS"] = self.options.shared
        
        # We patched CMakeLists.txt with this option to avoid building the tools needing OpenGL+GLUT.
        cmake.definitions["PARTIO_BUILD_TOOLS"] = False

        # We patched CMakeLists.txt with this option so we can avoid needing python + swig deps.
        cmake.definitions["PARTIO_BUILD_SWIG_PYTHON_BINDINGS"] = False

        cmake.definitions["CMAKE_PROJECT_partio_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    @property
    def _cxx_standard(self):
        return "17"

    def build(self):
        env = {"CXXFLAGS_STD" : "c++"+self._cxx_standard }
        with tools.environment_append(env):
            cmake = self._configure_cmake()
            cmake.build()
            cmake.install()

    @property
    def _library_filename(self):
        prefix = "" if self.settings.os == "Windows" else "lib"
        ext = "lib" if self.settings.os == "Windows" else "a"
        return f"{prefix}partio.{ext}"

    def _produce_config_files(self):
        os.makedirs(os.path.join(self.package_folder, "cmake"), exist_ok=True)

        data = {
            "os": self.settings.os,
            "cxx_std": "cxx_std_" + self._cxx_standard,
            "library_filename": self._library_filename
        }

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(file_name + ".in")
            template.stream(data).dump(os.path.join(self.package_folder, "cmake", file_name))

        _config_file("PartioConfig.cmake")

    def package(self):
        self._produce_config_files()
