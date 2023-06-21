# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import sys
import shutil

from conans import ConanFile, tools
from conans.errors import ConanException


class PySide6ShibokenConan(ConanFile):
    name = "pyside6-shiboken"
    license = "LGPL-3.0"
    author = "The Qt Company"
    url = "git://code.qt.io/pyside/pyside-setup.git"
    description = "Bindings generator for Qt for Python"
    settings = "os", "arch"
    options = {
        "shared": [True],
        "python_version": [3.9]
    }
    default_options = {"shared": True, "python_version": 3.9}
    revision_mode = "scm"
    short_paths = True

    package_originator = "External"
    package_exportable = True

    qt_libs = ("Core", "Network")

    def build_requirements(self):
        self.build_requires("Qt/[~6.3.1]")
        self.build_requires("LLVM/[~13.0.1]")
        if self.options.python_version == 3.9:
            self.build_requires("Python/[~3.9.10]")

    def configure(self):
        self.options["Qt"].with_vulkan = True

    @property
    def _checkout_folder(self):
        return f"{self.name}_src"

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")

    def _build_command(self, python_bin_path, src_dir, qmake_path, internal_build_type):
        self.run(f"{python_bin_path} -m ensurepip")

        # see https://bugreports.qt.io/browse/PYSIDE-1385 for the version choice of wheel
        index_url = "https://an_artifactory_url/artifactory/api/pypi/PyPI_Virtual/simple"
        self.run(f"{python_bin_path} -m pip install -qq wheel==0.34.2 packaging==21.3 --index-url {index_url}")

        args = (
            python_bin_path, os.path.join(src_dir, "setup.py"), "build",
            f"--internal-build-type={internal_build_type}",
            "--qtpaths", qmake_path,
            "--verbose-build",
            "--make-spec", "ninja",
            "--parallel", str(tools.cpu_count()),
            "--ignore-git",
            "--reuse-build",
        )
        return " ".join(args)

    def _build_windows(self, src_dir):
        qt_bin_path = self.deps_cpp_info["Qt"].bin_paths[0]
        qmake_path = os.path.join(qt_bin_path, "qtpaths.exe")
        llvm_root_path = self.deps_cpp_info["LLVM"].rootpath
        python_root_path = self.deps_cpp_info["Python"].rootpath
        python_bin_path = os.path.join(python_root_path, self.deps_user_info["Python"].interpreter)

        env = {
            "LLVM_INSTALL_DIR" : llvm_root_path,
            "CMAKE_PREFIX_PATH": python_root_path,
            "CC": "cl.exe", # pick up MSVC rather than clang from LLVM
            "CXX": "cl.exe",
            "PATH": [qt_bin_path]
        }
        with tools.environment_append(env):
            # see https://doc.qt.io/qtforpython/gettingstarted.html for why there are
            # two commands here compared with earlier versions of PySide6
            build_cmd = self._build_command(python_bin_path, src_dir, qmake_path, f"shiboken6")
            self.run(build_cmd)
            build_cmd = self._build_command(python_bin_path, src_dir, qmake_path, f"shiboken6-generator")
            self.run(build_cmd)

            # Copy the DLLs that shiboken needs to be able to run
            # This package is used as an independent tool in different build types, so the consumers
            # own dependencies cannot necessarily be used to run shiboken6.exe.
            install_bin_dir = os.path.join(self._install_dir, "bin")
            qt_version = tools.Version(self.version).major
            for lib in PySide6ShibokenConan.qt_libs:
              shutil.copy(os.path.join(qt_bin_path, f"Qt6{lib}.dll"), install_bin_dir)
            shutil.copy(os.path.join(llvm_root_path, "bin", "libclang.dll"), install_bin_dir)

    def build(self):
        src_dir = os.path.join(self.source_folder, self._checkout_folder)
        if self.settings.os == "Windows":
            self._build_windows(src_dir)
        else:
            raise RuntimeError(f"Recipe not implemented for this OS, {self.settings.os}")

    @property
    def _install_dir(self):
        # pyside/shiboken are using the venv name to contain the install dir.
        # see https://a_gitlab_url/libraries/conan/thirdparty/pyside/pyside/-/commit/0a40ebb1
        venv_dir = os.path.basename(sys.prefix)
        install_dir = os.path.join(self.source_folder, self._checkout_folder, "build")
        install_dir = os.path.join(install_dir, venv_dir, "install")

        if not os.path.isdir(install_dir):
            raise ConanException(f"Could not find the install directory {install_dir}")

        return install_dir

    def package(self):
        self.copy(pattern="*.exe", src=os.path.join(self._install_dir, "bin"), dst="bin")
        self.copy(pattern=f"Qt6*.dll", src=os.path.join(self._install_dir, "bin"), dst="bin")
        self.copy(pattern="libclang.dll", src=os.path.join(self._install_dir, "bin"), dst="bin")
