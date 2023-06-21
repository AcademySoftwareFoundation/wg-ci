# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools


class RangeV3Conan(ConanFile):
    name = "range-v3"
    description = ("Range library for C++14/17/20. This code was the basis of a formal proposal to add range support to "
        "the C++ standard library. That proposal evolved through a Technical Specification, and finally into P0896R4 "
        "'The One Ranges Proposal' which was merged into the C++20 working drafts in November 2018.")
    url = "https://github.com/ericniebler/range-v3.git"
    license = "LicenseRef-range-v3"
    author = "Eric Niebler"

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    @property
    def _run_unit_tests(self):
        return "RANGE_V3_RUN_UNITTESTS" in os.environ

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["RANGE_V3_TESTS"] = "ON" if self._run_unit_tests else "OFF"
        cmake.definitions["RANGE_V3_EXAMPLES"] = "OFF"
        cmake.definitions["RANGE_V3_DOCS"] = "OFF"
        cmake.configure(source_folder=os.path.join(
            self.source_folder, self._source_subfolder))

        return cmake

    def source(self):
        version_data = self.conan_data["sources"][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        if self._run_unit_tests:
            cmake = self._configure_cmake()
            cmake.build()
            cmake.test(output_on_failure=True)

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        self.info.header_only()
