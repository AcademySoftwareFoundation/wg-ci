# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, tools


class StbConan(ConanFile):
    name = "stb"
    license = "MIT"
    author = "Sean Barrett"
    url = "https://github.com/nothings/stb"
    description = \
        "single-file public domain (or MIT licensed) libraries for C/C++"

    exports_sources = "cmake*"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"], branch="master")
        git.checkout(version_data["git_hash"])

    def package(self):
        exclude_dirs = ("deprecated", "tests")
        self.copy("*.h", src=self._source_subfolder, dst="include/stb/", excludes=exclude_dirs)
        self.copy("*", src="cmake/", dst="cmake/")

    def package_id(self):
        self.info.header_only()
