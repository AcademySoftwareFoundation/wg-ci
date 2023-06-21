# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import path, symlink, unlink
import shutil

from conans import ConanFile, tools
from semver import SemVer


class PythonToolConan(ConanFile):
    name = "pythontool"
    version = "2.7.18-prebuilt"
    license = "PSF-2.0"
    author = "Guido van Rossum"
    url = "https://www.python.org/"
    description = "Python is an interpreted, object-oriented, high-level programming language with dynamic semantics."
    settings = "os", "arch"
    revision_mode = "scm"

    build_requires = ("Python/2.7.18@thirdparty/development")

    package_originator = "External"
    package_exportable = True

    def package(self):
        # cannot assume the dirs_exist_ok keyword for copytree is available yet (Python 3.8+)
        if path.exists(self.package_folder):
            shutil.rmtree(self.package_folder)

        # copy everything from the Python package, apart from the conaninfo.txt and conanmanifest.txt files
        shutil.copytree(
            self.deps_cpp_info["Python"].rootpath,
            self.package_folder,
            symlinks=True,
            ignore=shutil.ignore_patterns(("conan*.txt"))
        )

        if self.settings.os == "Macos":
            # need to fix broken symlinks
            symlinks = {
                "IDLE.app/Contents/MacOS/Python": "Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python",
            }
            for target, src in symlinks.items():
                with tools.chdir(self.package_folder):
                    unlink(target)
                    rel_path = path.relpath(src, path.dirname(target))
                    symlink(rel_path, target)

    @property
    def _exe_suffix(self):
        return ""

    @property
    def _abi_suffix(self):
        v = SemVer(self.version, False)
        if self.settings.os == "Windows":
            return f"{v.major}{v.minor}{self._exe_suffix}"
        else:
            return "{}.{}{}{}".format(
                v.major,
                v.minor,
                "",
                "m" if (v.major >= 3 and v.minor < 8) or v.major > 3 else ""
            )

    def package_info(self):
        pyver = SemVer(self.version, False)
        self.cpp_info.name = "pythontool"

        if self.settings.os == "Windows":
            self.cpp_info.bindirs = [""]  # On windows, the bindir == rootpath
            self.cpp_info.includedirs = ["include"]
            self.cpp_info.libs = [f"python{self._abi_suffix}.lib"]
            self.cpp_info.libdirs = ["libs"]
        elif self.settings.os == "Linux":
            self.cpp_info.bindirs = ["bin"]
            self.cpp_info.includedirs = [f"include/python{self._abi_suffix}"]
            self.cpp_info.libs = [f"libpython{self._abi_suffix}.so"]
            self.cpp_info.libdirs = ["lib"]
        elif self.settings.os == "Macos":
            internal_root = path.join("Python.framework", "Versions", f"{pyver.major}.{pyver.minor}")
            self.cpp_info.bindirs = [path.join(internal_root, "bin")]
            self.cpp_info.includedirs = [path.join(internal_root, "Headers")]
            self.cpp_info.libs = ["Python"] # In case someone needs it...
            self.cpp_info.libdirs = [path.join(internal_root)]
            self.cpp_info.frameworks = ["Python.framework"]

        interpreter_dir = "{}/".format(self.cpp_info.bindirs[0]) if self.cpp_info.bindirs[0] != "" else ""
        self.user_info.interpreter = "{}python{}{}{}".format(
            interpreter_dir,
            "",
            f"{pyver.major}.{pyver.minor}" if self.settings.os != "Windows" else "",
            ".exe" if self.settings.os == "Windows" else ""
        )

        self.user_info.pyhome = "Python.framework/Versions/Current" if self.settings.os == "Macos" else ""

    def package_id(self):
        if self.settings.os == "Macos":
             # no arch, so that Apple Silicon picks this up and runs it in Rosetta
             del self.info.settings.arch
             # no os.version so not tied to a minimum deployment target
             del self.info.settings.os.version
