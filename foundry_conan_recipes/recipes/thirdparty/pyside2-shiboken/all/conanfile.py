# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil

from conans import ConanFile, tools
from conans.errors import ConanException


class PySide2ShibokenConan(ConanFile):
    name = "pyside2-shiboken"
    license = "LGPL-3.0"
    author = "The Qt Company"
    url = "git://code.qt.io/pyside/pyside-setup.git"
    description = "Bindings generator for Qt for Python"
    settings = "os", "arch"
    options = {
        "shared": [True],
        "python_version": ["3.9", "3.10"]
    }
    default_options = {"shared": True, "python_version": "3.9"}
    revision_mode = "scm"
    short_paths = True

    package_originator = "External"
    package_exportable = True

    qt_libs = ("Core", "Network", "XmlPatterns")

    def build_requirements(self):
        self.build_requires("Qt/[~5.15.2]")
        self.build_requires("LLVM/[~13.0.1]")
        if self.options.python_version == "3.9":
            self.build_requires("Python/[~3.9.10]")
        elif self.options.python_version == "3.10":
            self.build_requires("Python/[~3.10.10]")

    @property
    def _checkout_folder(self):
        return f"{self.name}_src"

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")

    def _build_command(self, python_bin_path, src_dir, qmake_path, internal_build_type):
        args = (
            python_bin_path, os.path.join(src_dir, "setup.py"), "build",
            f"--internal-build-type={internal_build_type}",
            "--qmake", qmake_path,
            "--verbose-build",
            "--make-spec", "ninja",
            "--parallel", str(tools.cpu_count()),
            "--ignore-git",
            "--reuse-build",
        )
        return " ".join(args)

    def _build_windows(self, src_dir):
        qt_bin_path = self.deps_cpp_info["Qt"].bin_paths[0]
        qmake_path = os.path.join(qt_bin_path, "qmake.exe")
        llvm_root_path = self.deps_cpp_info["LLVM"].rootpath
        python_root_path = self.deps_cpp_info["Python"].rootpath
        python_bin_path = os.path.join(python_root_path, self.deps_user_info["Python"].interpreter)

        env = {
            "LLVM_INSTALL_DIR" : llvm_root_path,
            "CMAKE_PREFIX_PATH": python_root_path,
            "CC": "cl.exe", # pick up MSVC rather than clang from LLVM
            "CXX": "cl.exe",
        }
        with tools.environment_append(env):
            # see https://doc-snapshots.qt.io/qtforpython-5.15/shiboken2/gettingstarted.html for why there are
            # two commands here compared with earlier versions of PySide2
            build_cmd = self._build_command(python_bin_path, src_dir, qmake_path, "shiboken2")
            self.run(build_cmd)
            build_cmd = self._build_command(python_bin_path, src_dir, qmake_path, "shiboken2-generator")
            self.run(build_cmd)

            # Copy the DLLs that shiboken needs to be able to run
            # This package is used as an independent tool in different build types, so the consumers
            # own dependencies cannot necessarily be used to run shiboken2.exe.
            install_bin_dir = os.path.join(self._install_dir, "bin")
            for lib in PySide2ShibokenConan.qt_libs:
              shutil.copy(os.path.join(qt_bin_path, "Qt5%s.dll" % lib), install_bin_dir)
            shutil.copy(os.path.join(llvm_root_path, "bin", "libclang.dll"), install_bin_dir)

    def build(self):
        src_dir = os.path.join(self.source_folder, self._checkout_folder)
        if self.settings.os == "Windows":
            self._build_windows(src_dir)
        else:
            raise RuntimeError(f"Recipe not implemented for this OS, {self.settings.os}")

    @property
    def _install_dir(self):
        python_version = tools.Version(self.deps_cpp_info["Python"].version)
        qt_version = tools.Version(self.deps_cpp_info["Qt"].version)

        src_dir = os.path.join(self.source_folder, self._checkout_folder)
        install_dir = [item for item in os.listdir(src_dir) if item.endswith(f"{python_version.major}_install")]
        install_dir = os.path.join(src_dir, install_dir[0])

        if not os.path.isdir(install_dir):
            raise ConanException("Could not find the install directory")

        return f"{install_dir}/py{python_version.major}.{python_version.minor}-qt{qt_version}-64bit-release"

    def package(self):
        self.copy(pattern="*.exe", src=os.path.join(self._install_dir, "bin"), dst="bin")
        self.copy(pattern="Qt5*.dll", src=os.path.join(self._install_dir, "bin"), dst="bin")
        self.copy(pattern="libclang.dll", src=os.path.join(self._install_dir, "bin"), dst="bin")
