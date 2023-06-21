# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class WixConan(ConanFile):
    name = "WIX"
    license = "MS-RL"
    author = ".NET Foundation and contributors"
    url = "https://wixtoolset.org/"
    description = "The most powerful set of tools available to create your Windows installation experience."
    settings = "os"
    revision_mode = "scm"

    no_copy_source = True

    package_originator = "External"
    package_exportable = True

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("WIX is only applicable on Windows")

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        self.output.info("Nothing to build, progress to packaging...")

    def package(self):
        src_path = os.path.join(self.source_folder, self._source_subfolder)
        self.copy(pattern="*", src=src_path, keep_path=True)

    def package_info(self):
        self.env_info.path.append(self.package_folder)
