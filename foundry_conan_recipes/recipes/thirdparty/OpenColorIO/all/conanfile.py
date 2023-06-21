# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import glob
import os
import shutil
from os import path

from conans import ConanFile, CMake, tools
from jinja2 import Template
from semver import SemVer


class OpenColorIO(ConanFile):
    name = "OpenColorIO"
    license = "BSD-3-Clause"
    author = "AcademySoftwareFoundation"
    url = "https://github.com/AcademySoftwareFoundation/OpenColorIO"
    description = "OpenColorIO (OCIO) is a complete color management solution geared towards motion picture production with an emphasis on visual effects and computer animation."
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths"
    options = {
        "shared": [True],
        "python_version": ["2", "3", "3.9", "3.10", None],
        "library_suffix": "ANY",
    }
    default_options = {"shared": True, "python_version": "2", "library_suffix": ""}
    revision_mode = "scm"
    short_paths = True

    exports_sources = ["OpenColorIOConfig.cmake.in", "OpenColorIOConfigVersion.cmake.in"]

    package_originator = "External"
    package_exportable = True

    def build_requirements(self):
        if self.version >= "2.2":
            self.build_requires("minizip-ng/3.0.9")
            self.build_requires("zlib/1.2.13")

    def requirements(self):
        if self.options.python_version:
            if self.options.python_version == "3":
                self.requires("Python/3.7.7@thirdparty/development")
            elif self.options.python_version == "3.9":
                self.requires("Python/3.9.10")
            else:
                self.requires("Python/3.10.10")

            if self.version < "2.2":
                self.requires("pybind11/2.6.1@thirdparty/development")
            else:
                self.requires("pybind11/2.9.2")

    @property
    def _python_interpreter(self):
        return path.join(self.deps_cpp_info["Python"].rootpath, self.deps_user_info["Python"].interpreter)

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _python_paths(self):
        lib_path = path.join(self.deps_cpp_info["Python"].lib_paths[0], self.deps_cpp_info["Python"].libs[0])
        inc_path = self.deps_cpp_info["Python"].include_paths[0]
        bin_path = self._python_interpreter
        self.output.info(f"python path: {bin_path}")
        return bin_path, lib_path, inc_path

    def _configurePython(self, cmake):
        if not self.options.python_version:
            self.output.info("Building without Python Bindings.")
            cmake.definitions["OCIO_BUILD_PYTHON"] = "OFF"
            return

        bin_path, lib_path, inc_path = self._python_paths()
        bin_path = bin_path.replace('\\', '/')
        lib_path = lib_path.replace('\\', '/')
        inc_path = inc_path.replace('\\', '/')

        cmake.definitions["OCIO_BUILD_PYTHON"] = "ON"
        cmake.definitions["Python_ROOT_DIR"] = self.deps_cpp_info["Python"].bin_paths[0].replace('\\', '/')
        cmake.definitions["Python_LIBRARY"] = lib_path
        cmake.definitions["Python_EXECUTABLE"] = bin_path
        cmake.definitions["PYTHON_EXECUTABLE"] = bin_path
        cmake.definitions["Python_INCLUDE_DIR"] = inc_path

        cmake.definitions["pybind11_ROOT"] = self.deps_cpp_info["pybind11"].rootpath
        if self.settings.build_type == "Debug":
            cmake.definitions["USE_PYTHON_DEBUG"] = "ON"  # This is used by a custom patch of the OpenColorIO source

    def _cmake_configure(self):
        cmake = CMake(self)
        conan_paths = path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["OCIO_BUILD_GPU_TESTS"] = "OFF"
        cmake.definitions["CMAKE_PROJECT_OpenColorIO_INCLUDE"] = conan_paths
        cmake.definitions["OCIO_BUILD_APPS"] = "OFF"
        cmake.definitions["OCIO_BUILD_TESTS"] = "OFF"
        cmake.definitions["OCIO_BUILD_NUKE"] = "OFF"
        cmake.definitions["OCIO_BUILD_STATIC"] = "OFF" if self.options.shared else "ON"
        cmake.definitions["OCIO_INLINES_HIDDEN"] = "ON"
        # Library suffix is not supported in OCIO 1.1.1, therefore we must not
        # namespace OCIO (which is supported), otherwise our default library
        # name will confuse external clients.
        if self.options.library_suffix:
            cmake.definitions["OCIO_NAMESPACE"] = "FnOpenColorIO"
        cmake.definitions["OCIO_LIBNAME_SUFFIX"] = self.options.library_suffix
        self._configurePython(cmake)
        if self.settings.os == 'Linux':
            # external dependencies such as expat are installed in "lib64" but searched in "lib".
            cmake.definitions["CMAKE_INSTALL_LIBDIR"] = "lib64"
        cmake.configure(source_folder=self._source_subfolder, args=["-U*_DIR"])
        return cmake

    def build(self):
        cmake = self._cmake_configure()
        cmake.build()

    def _produce_config_files(self):
        p = path.join(self.package_folder, "cmake")
        if not path.exists(p):
            os.mkdir(p)

        ver = SemVer(self.version, False)

        def _configure(file_name):
            data = {
                "version_major": ver.major,
                "version_minor": ver.minor,
                "version_patch": ver.patch,
                "os": self.settings.os,
                "bt": self.settings.build_type,
                "prerelease": ver.prerelease[0] if len(ver.prerelease) > 0 else "",
                "library_suffix": self.options.library_suffix
            }

            with open(path.join(self.source_folder, file_name + ".in")) as file_:
                f = file_.read()
                template = Template(f)
            template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))

        _configure("OpenColorIOConfig.cmake")
        _configure("OpenColorIOConfigVersion.cmake")

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()

        self._produce_config_files()

        if self.settings.os == "Macos":
            self.output.info("Correcting the library IDs to use @rpath prefix")

            mac_lib_name = f"libOpenColorIO{self.options.library_suffix}"

            v = SemVer(self.version, True)
            baseline_version = f"{v.major}.{v.minor}.{v.patch}"
            shlib_path = path.join(self.package_folder, "lib", f"{mac_lib_name}.{baseline_version}.dylib")

            shlib_file_name = f"{mac_lib_name}.{baseline_version}.dylib"
            self.run(f"install_name_tool -id '@rpath/{shlib_file_name}' '{shlib_path}'")

            if self.options.python_version:
                py_module_path = next(
                    glob.iglob(path.join(self.package_folder, "**", "PyOpenColorIO.so"), recursive=True))
                self.run("install_name_tool -change {0} '@rpath/{0}' '{1}'".format(shlib_file_name, py_module_path))
        elif self.settings.os == "Windows":
            if self.settings.build_type == "Debug" and self.options.python_version:
                filepath = next(
                    glob.iglob(path.join(self.package_folder, "**", "PyOpenColorIO*.pyd"), recursive=True))
                os.rename(filepath, filepath.replace(".pyd", "_d.pyd"))

