# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class GnumakeforwindowsConan(ConanFile):
    name = "gnumakeforwindows"
    version = "3.81"
    settings = "os", "arch"
    description = "GNU make for Windows"
    author = "Paul D. Smith"
    url = "http://gnuwin32.sourceforge.net/packages/make.htm"
    license = "GPL-3.0-or-later"
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
            raise ConanInvalidConfiguration("gnumakeforwindows is only applicable on Windows")

    def build(self):
        source_dir = os.path.join(self.source_folder, self._checkout_folder)
        tools.unzip(os.path.join(source_dir, "bin.zip"), destination="dist")
        tools.unzip(os.path.join(source_dir, "dep.zip"), destination="dist")
        # naming convention used by some packages
        with tools.chdir(os.path.join("dist", "bin")):
            self.run("copy make.exe gmake.exe")

    def package(self):
        self.copy("*", src="dist")
