# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.scm import Git
import os


class UUIDConan(ConanFile):
    name = "UUID"
    description = "Portable uuid C library"
    url = "https://sourceforge.net/projects/libuuid/"
    license = "BSD-3-Clause"
    author = "Theodore Ts'o <tytso@mit.edu>"
    settings = "os", "arch", "compiler", "build_type"

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.info.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on Windows")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = Git(self, folder=self.source_folder)
        git.clone(url=version_data["git_url"], target=".")
        git.checkout(commit=version_data["git_hash"])

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-shared")
        tc.configure_args.append("--disable-static")
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["uuid"]
