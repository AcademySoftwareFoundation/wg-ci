# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from pathlib import Path
from shutil import rmtree
from conans import ConanFile, CMake, tools
from jinja2 import Environment, FileSystemLoader
from os import path


class GPerfToolsConan(ConanFile):
    name = "gperftools"
    license = "BSD-3-Clause"
    author = "google-perftools@googlegroups.com"
    url = "https://github.com/gperftools/gperftools"
    description = "TC Malloc fast allocator."
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True]}
    default_options = {"shared": True}
    generators = "cmake_paths"
    revision_mode = "scm"
    exports_sources = "cmake/*.cmake.in"

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

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions['gperftools_build_minimal'] = "ON"
        cmake.definitions['GPERFTOOLS_BUILD_CPU_PROFILER'] = "OFF"
        cmake.definitions['GPERFTOOLS_BUILD_DEBUGALLOC'] = "OFF"
        cmake.definitions['GPERFTOOLS_BUILD_HEAP_CHECKER'] = "OFF"
        cmake.definitions['GPERFTOOLS_BUILD_HEAP_PROFILER'] = "OFF"
        cmake.definitions['GPERFTOOLS_BUILD_STATIC'] = "OFF" if self.options.shared else "ON"
        cmake.definitions['BUILD_TESTING'] = "OFF"
        cmake.definitions['gperftools_build_benchmark'] = "OFF"
        cmake.definitions['gperftools_enable_libunwind'] = "OFF"

        cmake.configure(source_dir=path.join(self.source_folder, self._source_subfolder))

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        # remove pkgconfig we are use our .cmake configs instead
        rmtree(Path(self.package_folder, "lib", "pkgconfig"))

        self._cmake_config()

    def _cmake_config(self):
        """use a config to allow conan and cmake to find the packages we need on other machines"""

        Path(self.package_folder, 'cmake').mkdir(exist_ok=True)

        loader = FileSystemLoader(Path(self.source_folder, 'cmake'))
        env = Environment(loader=loader)

        def _configure(file_name):
            data = {'version': self.version, 'os': self.settings.os}
            template = env.get_template(file_name + '.in')
            template.stream(data).dump(path.join(self.package_folder, 'cmake', file_name))

        _configure("GPerfToolsConfig.cmake")
        _configure("GPerfToolsConfigVersion.cmake")

    def package_info(self):
        self.cpp_info.libs = [self.name] 
