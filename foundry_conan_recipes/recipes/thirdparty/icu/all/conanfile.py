# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import glob
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class IcuConan(ConanFile):
    name = "icu"
    license = "LicenseRef-Unicode-DFS-2020"
    author = "Unicode, Inc. and others"
    url = "https://icu.unicode.org/"
    description = "ICU is a mature, widely used set of C/C++ and Java libraries providing Unicode and Globalization support for software applications."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake_paths"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    def build_requirements(self):
        if self.options.shared:
            self.build_requires("patchelf/0.11@thirdparty/development")

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("icu is only applicable on Linux currently")

    def _autotools_configure(self):
        autotools = AutoToolsBuildEnvironment(self)
        args = []
        if self.options.shared:
            args.extend([
                "--enable-shared", "--disable-static"
            ])
        else:
            args.extend([
                "--enable-static", "--disable-shared"
            ])
            autotools.defines.append("U_STATIC_IMPLEMENTATION")
        autotools.flags.append("-fvisibility=hidden")
        autotools.cxx_flags.append("-fvisibility-inlines-hidden")
        autotools.configure(args=args, configure_dir=os.path.join(self.source_folder, self._source_subfolder, "icu4c", "source"))
        return autotools

    def build(self):
        self._autotools_configure().make()

    def _add_runpaths_to_libs(self):
        """
        For GCC builds using new dtags (RUNPATHS), each shared library is responsible for finding
        its dependents, so must have their own RUNPATHs.
        For older builds, an RPATH from the calling executable takes precedence over RUNPATH.
        """
        if self.options.shared:
            patchelf_path = os.path.join(self.deps_cpp_info["patchelf"].bin_paths[0], "patchelf")
            for symlink in glob.glob(os.path.join(self.package_folder, "lib", "*.so")):
                self.run(f'"{patchelf_path}" --set-rpath \$ORIGIN "{symlink}"')

    def package(self):
        self._autotools_configure().install()
        self._add_runpaths_to_libs()

    def package_info(self):
        libs=["icui18n", "icuio", "icutest", "icutu", "icuuc", "icudata"] # note order matters
        self.cpp_info.libs.extend(libs)
