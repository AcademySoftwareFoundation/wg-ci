# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import time
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration


class GperfConan(ConanFile):
    name = "gperf"
    license = "GPL-3.0-only"
    author = "Douglas C. Schmidt and Bruno Haible"
    url = "https://www.gnu.org/software/gperf/"
    description = "GNU gperf is a perfect hash function generator."
    settings = "os", "compiler", "build_type", "arch"

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _run_unit_tests(self):
        return "GPERF_RUN_UNITTESTS" in os.environ

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _real_source_dir(self):
        return os.path.join(self.source_folder, self._source_subfolder)

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("gperf is only applicable on Linux")

    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        version_data = self.conan_data["sources"][self.version]
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

        # Files written by Git may present slightly different timestamps.
        # docs will attempt to be rebuilt if the modification dates are slightly off
        # This presents a problem, as makeinfo might not be on the build machines
        # We'll touch every file after checkout, so they all share the same modification time.
        timestamp = time.time()
        with tools.chdir(self._source_subfolder):
            for file_path in tools.relative_dirs('.'):
                tools.touch(file_path, (timestamp, timestamp))

    def _configure(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure()
        return autotools

    def build(self):
        with tools.chdir(self._real_source_dir):
            autotools = self._configure()
            autotools.make()
            if self._run_unit_tests:
                autotools.make(args=["check"])

    def package(self):
        with tools.chdir(self._real_source_dir):
            self._configure().install()

    def package_info(self):
        # bindirs defaults to "bin"
        self.user_info.gperfexe = "gperf"
        # and there is only an executable generated from this build, so clear other paths
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.libs = []
