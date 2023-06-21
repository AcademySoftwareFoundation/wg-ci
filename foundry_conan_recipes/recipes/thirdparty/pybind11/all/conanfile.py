# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, tools


class Pybind11Conan(ConanFile):
    name = "pybind11"
    license = "BSD-3-Clause"
    author = "Wenzel Jakob"
    url = "https://github.com/pybind/pybind11"
    description = "Seamless operability between C++11 and Python"

    options = {"python_version": ["2", "3", "3.9", "3.10"]}
    default_options = {"python_version": "3"}

    exports_sources = "*"
    no_copy_source = True
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def requirements(self):
        if self.options.python_version == "2":
            self.requires("Python/2.7.18@thirdparty/development")
        elif self.options.python_version == "3":
            self.requires("Python/3.7.7@thirdparty/development")
        elif self.options.python_version == "3.9":
            self.requires("Python/3.9.10")
        else:
            self.requires("Python/3.10.10")

    def source(self):
        version_data = self.conan_data["sources"][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _write_cmake_config_file(self):
        tokens = {}
        tokens["PYTHON_VERSION"] = self.deps_cpp_info["Python"].version
        tokens["PYBIND11_VERSION"] = self.version

        config_in_path = os.path.join(self.source_folder, "pybind11Config.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)

        config_out_path = os.path.join(config_out_dir, "pybind11Config.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def package(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        self.copy("CMakeLists.txt", src=src_dir, dst=self.package_folder)
        self.copy("include/*", src=src_dir, dst=self.package_folder)
        self.copy("tools/*", src=src_dir, dst=self.package_folder)

        self._write_cmake_config_file()

    def package_id(self):
        self.info.header_only()
