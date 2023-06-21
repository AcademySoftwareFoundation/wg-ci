# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools

class LibExifConan(ConanFile):
    name = "libexif"
    license = "LGPL-2.1"
    author = """Lutz Mueller <urc8@rz.uni-karlsruhe.de>,
                Jan Patera <patera@users.sourceforge.net>,
                Hubert Figuiere <hub@figuiere.net>,
                Dan Fandrich <dan@coneharvesters.com>,
                Marcus Meissner <marcus@jet.franken.de>"""
    url = "https://libexif.github.io/"
    description = """libexif is a library for parsing, editing, and saving EXIF data. It is
                     intended to replace lots of redundant implementations in command-line
                     utilities and programs with GUIs."""
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True]}
    default_options = {"shared": True}
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.licxx

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def configure_cmake(self):
        cmake = CMake(self)

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        self.configure_cmake().build()

    def package(self):
        self.configure_cmake().install()

    def package_info(self):
        self.cpp_info.libs = ["exif"]

