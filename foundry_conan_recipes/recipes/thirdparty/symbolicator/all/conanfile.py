# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from jinja2 import Environment, FileSystemLoader
import os, stat


class SymbolicatorConan(ConanFile):
    name = "symbolicator"
    settings = "os", "arch"
    description = "Native Symbolication as a Service"
    url = "https://github.com/getsentry/symbolicator"
    license = "MIT"
    author = "sentry.io"
    revision_mode = "scm"

    exports_sources = "*.cmake.in"
    no_copy_source = True

    package_originator = "External"
    package_exportable = False

    @property
    def _executables(self):
        if self.settings.os == "Linux":
            suffix = "Linux-x86_64-GLIBC-2-17"
        elif self.settings.os == "Windows":
            suffix = "Windows-x86_64.exe"
        elif self.settings.os == "Macos":
            suffix = "Darwin-universal"
        else:
            raise ConanInvalidConfiguration("Unsupported OS: " + str(self.settings.os))

        executables = {
            "symbolicator": f"symbolicator-{suffix}",
            "symsorter": f"symsorter-{suffix}"
        }

        return executables

    def source(self):
        version_data = self.conan_data['sources'][self.version]
        baseurl = version_data["git_url"]

        def make_exec(filename):
            st = os.stat(filename)
            os.chmod(filename, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        for exe in self._executables.values():
            osfolder = str(self.settings.os).lower()
            url = f"{baseurl}/{osfolder}/{exe}"
            tools.download(url=url, filename=exe)
            if self.settings.os != "Windows":
                make_exec(exe)

    def _config_file(self):
        os.makedirs(os.path.join(self.package_folder, "cmake"), exist_ok=True)
        data = self._executables

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(file_name + ".in")
            template.stream(data).dump(os.path.join(self.package_folder, "cmake", file_name))

        _config_file("SymbolicatorConfig.cmake")

    def package(self):
        self._config_file()
        for exe in self._executables.values():
            self.copy(exe, dst="bin", src=".")
