# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class NasmConan(ConanFile):
    name = "nasm"
    license = "BSD-2-Clause"
    author = "The NASM development team"
    url = "https://www.nasm.us/"
    description = "Netwide Assembler (NASM), an assembler for the x86 CPU architecture portable to nearly every modern platform"
    settings = "os", "arch"
    exports_sources = "*"
    no_copy_source = True
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def configure(self):
        if self.settings.os != "Windows":
            # not entirely true, as there are mac binaries, but I've only ever tested Windows
            raise ConanInvalidConfiguration("nasm is only applicable on Windows")

    def build(self):
        source_dir = os.path.join(self.source_folder, self._checkout_folder)
        tools.unzip(os.path.join(source_dir, "win64", "nasm.zip"), destination="dist")

    def package(self):
        self.copy("*", src=os.path.join("dist", "nasm-{}".format(self.version)))
