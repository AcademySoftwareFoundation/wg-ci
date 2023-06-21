# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools


class OpenTimelineIOConan(ConanFile):
    name = "OpenTimelineIO"
    license = "Apache-2.0"
    author = "Pixar"
    url = "https://github.com/PixarAnimationStudios/OpenTimelineIO.git"
    description = "An Open Source API and interchange format that facilitates collaboration and communication of editorial data and timeline information between a studio's Story, Editorial and Production departments all the way through Post-Production."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {"shared": False, "fPIC": True}
    revision_mode = "scm"
    short_paths = True
    generators = "cmake_paths"
    package_originator = "External"
    package_exportable = True

    def requirements(self):
        # Note: pybind is included in the source tree, but I don't see a way to look for an external build
        self.requires("Python/3.7.7@thirdparty/development")
        if tools.Version(self.version) >= "0.15.0":
            self.requires("imath/3.1.4")

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data['git_url'])
        git.checkout(version_data['git_hash'], submodule="recursive") # pybind11, any, optional-lite, RapidJSON

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_OpenTimelineIO_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["GIT_AUTOMATIC_SUBMODULES"] = "OFF" # because we control the source checkout in this recipe
        cmake.definitions["GIT_UPDATE_SUBMODULES"] = "OFF" # because we control the source checkout in this recipe
        cmake.definitions["OTIO_PYTHON_INSTALL"] = "ON"
        cmake.definitions["OTIO_CXX_INSTALL"] = "ON"
        cmake.definitions["OTIO_PYTHON_INSTALL_DIR_INITIALIZED_TO_DEFAULT"] = "ON"
        cmake.definitions["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = "ON"

        if tools.Version(self.version) >= "0.15.0":
            cmake.definitions["OTIO_FIND_IMATH"] = "ON"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        if self.options.shared:
            cmake.definitions["OTIO_SHARED_LIBS"] = "ON"
        else:
            cmake.definitions["OTIO_SHARED_LIBS"] = "OFF"

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        self._configure_cmake().build()

    def _copy_python_packages(self):
        # manually copy the Python packages, which aren't "installed" by CMake, since it's done by setup.py
        self.copy(
            "*.*",
            dst=os.path.join(self.package_folder, "python", "opentimelineio"),
            src=os.path.join(self.source_folder, self._source_subfolder, "src", "py-opentimelineio", "opentimelineio"),
            keep_path=True,
            excludes=("*__pycache__"),
        )
        self.copy(
            "*.*",
            dst=os.path.join(self.package_folder, "python", "opentimelineio_contrib"),
            src=os.path.join(self.source_folder, self._source_subfolder, "contrib", "opentimelineio_contrib"),
            keep_path=True,
            excludes=("*__pycache__", "*sample_data"),
        )
        self.copy(
            "*.*",
            dst=os.path.join(self.package_folder, "python", "opentimelineview"),
            src=os.path.join(self.source_folder, self._source_subfolder, "src", "opentimelineview"),
            keep_path=True,
            excludes=("*__pycache__"),
        )

    def package(self):
        self._configure_cmake().install()
        self._copy_python_packages()


    def package_id(self):
        python_dep = self.info.requires["Python"]
        python_dep.minor_mode()
