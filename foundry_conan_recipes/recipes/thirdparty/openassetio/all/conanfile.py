# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class OpenAssetIOConan(ConanFile):
    name = "openassetio"
    license = "Apache-2.0"
    author = "Contributors to the OpenAssetIO project"
    url = "https://github.com/OpenAssetIO/OpenAssetIO"
    description = (
        "An open-source interoperability standard for tools"
        " and content management systems used in media production."
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        # Not strictly necessary, since OpenAssetIO sets CMake's
        # POSITION_INDEPENDENT_CODE target property to ON by default
        # regardless of library type, but adding this here
        # keeps things consistent with other recipes and is more
        # future-proof.
        "fPIC": [True, False],
        # We need the `python_version` option (rather than using a
        # version range in `requires`) to use in the `variants` list in
        # `config.yml`, which drives CI builds.
        "python_version": ["3.9", None],
    }
    default_options = {"shared": True, "python_version": None, "fPIC": True}
    generators = "cmake_paths"
    revision_mode = "scm"

    # Foundry-specific
    package_originator = "External"
    package_exportable = True  # Since FOSS.

    build_requires = [
        "tomlplusplus/3.2.0"
    ]

    def build_requirements(self):
        if self.options.python_version:
            self.build_requires("pybind11/[2.9]")

    def configure(self):
        if self.options.python_version:
            self.options['pybind11'].python_version = self.options.python_version

    def requirements(self):
        if self.options.python_version:
            # Note that OpenAssetIO requires the `Development.Module`
            # component from Python's CMake package, which is currently
            # unsupported by Foundry's `PythonConfig.cmake` package
            # config file. So we rely on CMake's built-in
            # `FindPython.cmake` module being used instead. Luckily,
            # OpenAssetIO uses the basic signature of `find_package`, so
            # MODULE mode (FindPython) has priority over CONFIG mode
            # (PythonConfig), by default. However, this does mean we
            # have to provide additional hints to help the FindPython
            # module locate the correct Python.
            self.requires(f"Python/[~{self.options.python_version}]")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def _configure_cmake(self):
        cmake = CMake(self)
        # Use the generated toolchain file to augment dependency search
        # paths for CMake's `find_package` calls.
        cmake.definitions["CMAKE_PROJECT_OpenAssetIO_INCLUDE"] = os.path.join(
            self.install_folder, "conan_paths.cmake"
        )
        # C++ ABI for GCC. VFX <= CY2022 uses old ABI.
        # Note must `get_safe`, since other toolchains (e.g. Windows)
        # don't have this setting.
        libcxx = self.settings.get_safe("compiler.libcxx")
        if libcxx is not None:
            if libcxx == "libstdc++11":
                cmake.definitions["OPENASSETIO_GLIBCXX_USE_CXX11_ABI"] = "ON"
            else:
                cmake.definitions["OPENASSETIO_GLIBCXX_USE_CXX11_ABI"] = "OFF"

        # Python bindings.
        if not self.options.python_version:
            cmake.definitions["OPENASSETIO_ENABLE_PYTHON"] = "OFF"
        else:
            cmake.definitions["OPENASSETIO_ENABLE_PYTHON"] = "ON"
            # Ensure the Python discovered by OpenAssetIO is the correct
            # one. This is particularly an issue when building from a
            # venv where, by default, the venv's Python version is
            # preferred by CMake's FindPython.cmake module.
            cmake.definitions["Python_ROOT_DIR"] = self.deps_cpp_info["Python"].rootpath
            # CMake's FindPython module can find a library that is not
            # part of the same distribution as the executable, so we
            # must specify this as well. Note this is only required
            # for Windows - Linux/OSX only require headers.
            if self.settings.os == "Windows":
                cmake.definitions["Python_LIBRARY"] = self._python_lib

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    @property
    def _python_lib(self):
        return os.path.join(
            self.deps_cpp_info["Python"].rootpath,
            self.deps_cpp_info["Python"].libdirs[0], self.deps_cpp_info["Python"].libs[0])

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self._configure_cmake().install()

    def package_id(self):
        # Ensure package_id changes on Python semver minor version.
        # Technically unnecessary due to the `python_version` option
        # also affecting package id, but good practice.
        if self.options.python_version:
            python_dep = self.info.requires["Python"]
            python_dep.minor_mode()
