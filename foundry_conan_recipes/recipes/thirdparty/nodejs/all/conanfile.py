# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanException


class NodeJSConan(ConanFile):
    name = "nodejs"
    description = "Node.js® is a JavaScript runtime built on Chrome's V8 JavaScript engine."
    url = "https://nodejs.org"
    license = "LicenceRef-MIT-nodejs"
    author = "Ryan Dahl and many collaborators https://github.com/nodejs/node#current-project-team-members"

    settings = "os", "arch", "compiler" # note that the compiler is removed in package_id but used in the recipe logic

    # shared builds are not officially supported
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    short_paths = True

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_autotools(self):
        # Note that the Linux build scripts hardcode
        # _GLIBCXX_USE_CXX11_ABI=1
        # https://github.com/nodejs/node/blob/5fad0b93667ffc6e4def52996b9529ac99b26319/common.gypi#L262
        # This is ok while we're only using the node executable, but would need to be changed if there was a consuming
        # usage of this into products
        autotools = AutoToolsBuildEnvironment(self)
        autotools.fpic = self.options.fPIC
        with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
            config_args = [
                "--ninja",
                "--verbose",
                "--without-npm",
                "--without-corepack",
            ]
            config_args.append("--enable-static")
            autotools.configure(args=config_args)
        return autotools

    def _windows_cmd(self):
        cmd_args = [
            "vcbuild.bat",
            "openssl-no-asm", # avoids needing NASM
            "nonpm",
            "nocorepack",
        ]
        cmd_args.append("release")
        cmd_args.append("dll" if self.options.shared else "static")
        if self.settings.compiler.version == "16":
            cmd_args.append("vs2019")
        else:
            raise ConanException(f"Unsupported compiler version, {self.settings.compiler_version}")
        return cmd_args

    def build(self):
        if self.settings.os == "Windows":
            self.run(" ".join(self._windows_cmd()), cwd=os.path.join(self.source_folder, self._source_subfolder))
        else:
            with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
                self._configure_autotools().make()

    def package(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        if self.settings.os == "Windows":
            # cannot use the 'package' flag to vcbuild.bat, since it requires 7zip, but it does show what is needed in the final package
            # look for the :stage_package label in vcbuild.bat
            self.copy("CHANGELOG.md", src=src_dir)
            self.copy("LICENSE", src=src_dir)
            self.copy("README.md", src=src_dir)
            self.copy("install_tools.bat", src=os.path.join(src_dir, "tools", "msvs", "install_tools"))
            self.copy("nodevars.bat", src=os.path.join(src_dir, "tools", "msvs"))
            self.copy("node_etw_provider.man", src=os.path.join(src_dir, "src", "res"))
            build_dir = os.path.join(src_dir, "out", "Release")
            self.copy("node.exe", src=build_dir)
        else:
            with tools.chdir(src_dir):
                self._configure_autotools().install()

    def package_id(self):
        # to be compiler agnostic, as we're only using the node executable currently
        del self.info.settings.compiler
        if self.settings.os == "Macos":
            # no os.version so not tied to a minimum deployment target
            del self.info.settings.os.version
