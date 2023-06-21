# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, AutoToolsBuildEnvironment, tools, errors
from os import path

class LibusbConan(ConanFile):
    name = "Libusb"
    settings = ["os", "compiler", "build_type", "arch"]
    description = "A unix library to access USB devices"
    author = "libusb"
    url = "https://libusb.info"
    license = "LGPL-2.1"

    generators = "cmake"
    exports_sources = "cmake*"
    no_copy_source = True
    revision_mode = "scm"
    options = {'shared': [True]}
    default_options = {'shared': True}

    package_originator = "External"
    package_exportable = True

    def validate(self):
        if self.settings.os != "Linux" :
            raise errors.ConanInvalidConfiguration(f"This Library does not support {self.settings.os}!")

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build(self):
        # Need to run the bootstrap for configure then build
        source_folder = path.join(self.source_folder, self._source_subfolder)
        self.run(path.join(source_folder, "bootstrap.sh"))

        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=source_folder,
                            args=[
                                "--enable-udev=false",
                                "--enable-shared",
                                "--disable-static",
                            ])
        autotools.make()

    def package(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.install()

        self.copy("*", src="cmake/", dst="cmake/")
