# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools

class OpenColorIOConfigACESConan(ConanFile):
    name = "OpenColorIOConfigACES"
    license = "BSD-3-Clause"
    author = "AcademySoftwareFoundation"
    description = "OpenColorIO ACES default configurations"
    url = "https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES"

    package_originator = "External"
    package_exportable = True
    revision_mode = "scm"

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def package(self):
        excludes = [
            ".gitattributes"
        ]
        self.src_dir = os.path.join(self.source_folder, self._source_subfolder)
        self.copy("*", src=self.src_dir, dst="configs", excludes=excludes)
