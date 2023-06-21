# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class PCRE2Conan(ConanFile):
    name = "pcre2"
    license = "BSD-3-Clause"
    author = "Philip Hazel"
    url = "https://github.com/PCRE2Project/pcre2"
    description = ("The PCRE2 library is a set of C functions that implement regular expression "
                   "pattern matching using the same syntax and semantics as Perl 5.")

    settings = "os", "compiler", "build_type", "arch"

    options = {"shared": [True, False], "fPIC": [True, False], "support_jit": [False, True]}
    default_options = {"shared": True, "fPIC": True, "support_jit": False}

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    @property
    def _run_unit_tests(self):
        return "PCRE2_RUN_UNITTESTS" in os.environ

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_STATIC_LIBS'] = not self.options.shared
        if self.settings.os != 'Windows':
            cmake.definitions['PCRE2_STATIC_PIC'] = self.options.fPIC
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        else:
            cmake.definitions['INSTALL_MSVC_PDB'] = True
        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
        cmake.definitions['PCRE2_BUILD_PCRE2_8'] = True
        cmake.definitions['PCRE2_BUILD_PCRE2_16'] = True
        cmake.definitions['PCRE2_BUILD_PCRE2_32'] = True
        cmake.definitions['PCRE2_SUPPORT_JIT'] = self.options.support_jit
        cmake.definitions['PCRE2_SUPPORT_LIBBZ2'] = False
        cmake.definitions['PCRE2_SUPPORT_LIBZ'] = False
        cmake.definitions['PCRE2_SUPPORT_LIBEDIT'] = False
        cmake.definitions['PCRE2_SUPPORT_LIBREADLINE'] = False
        cmake.definitions['PCRE2_BUILD_TESTS'] = self._run_unit_tests
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
