# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

# Comments:
# - BLAS/LAPACK is disabled as I could not get MKL 11.x to be recongnised as a
#   valid BLAS installation unless I hard-code the libraries
# - BLAS/LAPACK is needed by SuiteSparse (optional dependency of Ceres), which
#   is not automatically built and thus it is disabled
# - Lemon (src/third_party) looks for COIN which is build separately by the
#   project (src/dependencies/osi_clp), but I cannot get Lemon to link to it
#   Note that this seems to be the default behaviour.
# - OpenMVG builds shared libraries by default, but we force it to build static
# - Cannot get it to link properly with OpenMP, disabling it

class OpenMVGConan(ConanFile):
    name = "OpenMVG"
    description = "OpenMVG provides an end-to-end 3D reconstruction from images framework compounded of libraries, binaries, and pipelines."
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/openMVG/openMVG"
    author = "Pierre Moulon, Pascal Monasse, Romuald Perrot, and Renaud Marlet"
    license = "MPL-2.0"
    generators = "cmake_paths"
    revision_mode = "scm"
    package_originator = "External"
    package_exportable = True
    options = {"shared" : [False], "fPIC": [True, False]}
    default_options = {"shared" : False, "fPIC": True}

    requires = [
        "PNG/1.6.9@thirdparty/development",
        "JPEG/6b@thirdparty/development",
        "libtiff/3.9.4@thirdparty/development",
        "zlib/1.2.11@thirdparty/development",
        "Eigen/3.3.7@foundry/stable",
        "FLANN/1.8.5@thirdparty/development"
    ]

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["CMAKE_PROJECT_openMVG_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["LAPACK"] = "OFF"
        cmake.definitions["OpenMVG_USE_OCVSIFT"] = "OFF"
        cmake.definitions["OpenMVG_BUILD_SHARED"] = "OFF"
        cmake.definitions["OpenMVG_BUILD_SOFTWARES"] = "OFF"
        cmake.definitions["OpenMVG_BUILD_GUI_SOFTWARES"] = "OFF"
        cmake.definitions["OpenMVG_BUILD_TESTS"] = "OFF"
        cmake.definitions["OpenMVG_BUILD_OPENGL_EXAMPLES"] = "OFF"
        cmake.definitions["OpenMVG_BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["OpenMVG_BUILD_DOC"] = "OFF"
        cmake.definitions["OpenMVG_BUILD_COVERAGE"] = "OFF"
        cmake.definitions["OpenMVG_USE_OPENMP"] = "OFF"
        cmake.definitions["Boost_USE_STATIC_LIBS"] = "ON"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure(source_folder=os.path.join(self._source_subfolder, "src"))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
