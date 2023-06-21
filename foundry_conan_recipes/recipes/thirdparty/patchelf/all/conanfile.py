# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class PatchelfConan(ConanFile):
    name = "patchelf"
    license = "GPL-3.0-only"
    author = "Eelco Dolstra"
    url = "https://github.com/NixOS/patchelf"
    description = "A small utility to modify the dynamic linker and RPATH of ELF executables"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "*"
    no_copy_source = False # must bootstrap in sources
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "PATCHELF_RUN_UNITTESTS" in os.environ

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("patchelf is only applicable on Linux")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        src_dir = os.path.join(self.source_folder, self._checkout_folder)
        with tools.chdir(src_dir):
            self.run("./bootstrap.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            if self._run_unit_tests:
                autotools.make(args=["check", "-j1"])
            autotools.install()
