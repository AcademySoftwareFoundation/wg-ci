# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from os import path
from conans import ConanFile, CMake, tools
from contextlib import contextmanager

@contextmanager
def change_cwd(newDir):
    curdir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(curdir)


class TbbConan(ConanFile):
    name = "tbb"
    license = "Apache-2.0"
    author = "Intel"
    url = "https://github.com/oneapi-src/oneTBB"
    description = "Intel Threading Building Blocks (Intel TBB) lets you easily write parallel C++ programs that take full advantage of multicore performance, that are portable and composable, and that have future-proof scalability"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True], "fPIC": [True]}
    default_options = {"shared": True, "fPIC": True}
    exports_sources = "*"
    no_copy_source = True
    generators = "cmake_paths"
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "TBB_RUN_UNITTESTS" in os.environ

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("gnumakeforwindows/3.81@thirdparty/development")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_tbb_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["SOURCE_DIR"] = path.join(self.source_folder, self._checkout_folder)
        cmake.definitions["RUN_UNITTESTS"] = "ON" if self._run_unit_tests else "OFF"
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def fix_linux_symlinks(self):
        libDir = path.join(self.package_folder, "lib")
        badSymlinks = [item for item in os.listdir(libDir) if item.endswith(".so")]
        with change_cwd(libDir):
            for symlink in badSymlinks:
                os.remove(symlink)
                os.symlink(symlink + ".2", symlink)

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.os == "Linux":
            self.fix_linux_symlinks()

    def package_info(self):
        self.cpp_info.libs = ["tbb"] # TODO: depends if it's debug or not
