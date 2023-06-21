# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, tools
import os

class OpenColorIOConfigsConan(ConanFile):
    name = "OpenColorIOConfigs"
    license = "Unclear-FOSS"
    author = "colour-science"
    description = "OpenColorIO default configurations"
    url = "https://github.com/colour-science/OpenColorIO-Configs"
    generators = "cmake_paths"

    package_originator = "External"
    package_exportable = True
    revision_mode = "scm"

    options = {"acesVersion": "ANY"}
    default_options = {"acesVersion": "1.2"}

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"], branch="foundry/v{}".format(self.options.acesVersion), shallow=True)
        git.checkout(version_data["git_hash"])

    def package(self):
        excludes = [
            ".git",
            ".gitignore",
            "*baked*",
            "aces_0.1.1",
            "aces_0.7.1",
            "aces_1.0.1",
            "aces_1.0.2",
            "nuke-default",
            "spi-anim",
            "spi-vfx",
            "ChangeLog"
        ]
        self.src_dir = os.path.join(self.source_folder, self._source_subfolder)
        self.copy("*", src=self.src_dir, dst="configs", excludes=excludes)
