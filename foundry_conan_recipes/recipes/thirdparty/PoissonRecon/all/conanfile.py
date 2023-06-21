# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, CMake


class PoissonReconConan(ConanFile):
    name = "PoissonRecon"
    settings = "os", "compiler", "build_type", "arch"
    description = "Adaptive Multigrid Solvers."
    license = "MIT"
    author = "Michael Kazhdan"
    url = "https://github.com/mkazhdan/PoissonRecon"
    revision_mode = "scm"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    package_originator = "External"
    package_exportable = True
    exports_sources = ("PoissonReconConfig.cmake.in")

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        
        if self.options.shared:
            cmake.definitions["POISSON_RECON_SHARED"] = 'ON'
            if self.settings.os == "Macos":
                cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"
        else:
            cmake.definitions['CMAKE_C_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_CXX_VISIBILITY_PRESET'] = 'hidden'
            cmake.definitions['CMAKE_VISIBILITY_INLINES_HIDDEN'] = 'ON'

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        env = {"CXXFLAGS_STD" : "c++17" }
        with tools.environment_append(env):
            cmake = self._configure_cmake()
            cmake.build()
            cmake.install()
