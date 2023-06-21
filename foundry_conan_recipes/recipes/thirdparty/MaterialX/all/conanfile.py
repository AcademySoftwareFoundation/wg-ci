# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
from conans import ConanFile, tools, CMake

class MaterialXIOConan(ConanFile):
    name = "MaterialX"
    license = "Apache-2.0"
    author = "LucasFilm Ltd"
    url = "https://www.materialx.org/"
    description = "MaterialX is an open standard for transfer of rich material and look-development content between applications and renderers."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [False], "fPIC": [True, False],
               "python_version": [None, "3.9", "3.10"],
               "aces_version": [None, "1.1", "1.2", "1.3"]}
    default_options = {"shared": False, "fPIC": True, "python_version": None, "aces_version": None}
    generators = "cmake_paths"
    exports_sources = "*"
    no_copy_source = False
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _get_python_executable(self):
        return os.path.join(
            os.path.normpath(self.deps_cpp_info['Python'].rootpath),
            os.path.normpath(self.deps_user_info['Python'].interpreter)
        )

    @property
    def _run_unit_tests(self):
        return "MATERIALX_RUN_UNITTESTS" in os.environ

    @property
    def _ocio_config_dir(self):
        return os.path.join(self.source_folder, "ocio_config")

    def requirements(self):
        if self.options.python_version:
            if self.options.python_version == "3.9":
                self.requires("Python/3.9.10")
                self.requires("OpenColorIO/2.1.2@")
            else:
                self.requires("Python/3.10.10")
                self.requires("OpenColorIO/2.2.1@")
            self.requires("pybind11/2.9.2")

            if self.options.aces_version:
                if self.options.aces_version in ["1.1", "1.2"]:
                    self.requires("OpenColorIOConfigs/1.0.3@thirdparty/development")
                elif self.options.aces_version == "1.3":
                    self.requires("OpenColorIOConfigACES/1.3@")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.python_version:
            self.options["OpenColorIO"].python_version = self.options.python_version

    def _copy_ocio_config(self):
        if not self.options.aces_version:
            return

        if self.options.aces_version == '1.3':
            ocio_config_dir = os.path.join(
                self.deps_cpp_info["OpenColorIOConfigACES"].rootpath, "configs")
            ocio_config_filename = "cg-config-v1.0.0_aces-v1.3_ocio-v2.1.ocio"
        elif self.options.aces_version in ['1.1', '1.2']:
            ocio_config_dir = os.path.join(
                self.deps_cpp_info["OpenColorIOConfigs"].rootpath, "configs", f"aces_{self.options.aces_version}")
            ocio_config_filename = "config.ocio"

        os.makedirs(self._ocio_config_dir, exist_ok=True)
        shutil.copy2(os.path.join(ocio_config_dir, ocio_config_filename),
             os.path.join(self._ocio_config_dir, 'config.ocio'))

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

        self._copy_ocio_config()

    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.python_version:
            cmake.definitions["MATERIALX_BUILD_PYTHON"] = "ON"
            cmake.definitions["MATERIALX_PYTHON_EXECUTABLE"] = self._get_python_executable
            cmake.definitions["MATERIALX_PYTHON_VERSION"] = self.options.python_version
            cmake.definitions["PYBIND11_PYTHON_VERSION"] = self.options.python_version
            cmake.definitions["CMAKE_PROJECT_MaterialX_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

            if self.options.aces_version is not None:
                cmake.definitions["MATERIALX_PYTHON_OCIO_DIR"] = self._ocio_config_dir

        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.options.shared and self.settings.os == "Macos":
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

        if self._run_unit_tests:
            cmake.build(target="test")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = ["MaterialX"]

