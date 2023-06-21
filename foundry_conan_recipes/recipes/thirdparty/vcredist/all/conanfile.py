# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from pathlib import Path
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class vcredist(ConanFile):
    name = "vcredist"
    author = "Microsoft"
    description = "Visual C++ Redistributable"
    license = "MSVC-2019"
    url = "https://learn.microsoft.com/en-gb/cpp/windows/latest-supported-vc-redist"
    settings = ["arch", "build_type"]
    revision_mode = "scm"
    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self) -> str:
        return f"{self.name}_src"

    def source(self):
        version_data = self.conan_data["sources"][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    @property
    def _copy_root(self) -> Path:
        copy_root = Path(self._source_subfolder)

        if self.settings.build_type == "Debug":
            copy_root = copy_root / "debug_nonredist"

        if self.settings.arch == "x86":
            raise ConanInvalidConfiguration(
                "We don't want to support 32-bit version of this package.")
        elif self.settings.arch == "x86_64":
            copy_root = copy_root / "x64"
        else:
            raise ConanInvalidConfiguration(
                f"We don't have sources of this Microsoft Visual C++ Redistributable for required "
                f"{self.settings.arch} architecture. Please consider visiting {self.url} "
                "and getting the latest-greatest Microsoft Visual C++ Redistributable...")

        return copy_root

    def package(self):
        self.copy(pattern="*", src=self._copy_root)

        # Copying vs_redist installers
        self.copy(pattern=f"vcredist_x64.exe", src=self._source_subfolder)
