# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os

from conans import ConanFile, CMake, tools


class SentryConan(ConanFile):
    name = "sentry"
    license = "MIT"
    author = "Sentry"
    url = "https://sentry.io"
    description = "The Sentry Native SDK is an error and crash reporting client for native applications, optimized for C and C++"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake_paths"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _checkout_folder(self):
        return f"{self.name}_src"

    def requirements(self):
        if self.settings.os != "Windows":
            self.requires("OpenSSL/1.1.1m")
            self.requires("Curl/7.72.0@thirdparty/development")
        self.requires("zlib/1.2.11@thirdparty/development")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")

    def _configure_cmake(self):
        cmake = CMake(self)
        
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        # multiple CMake projects need to inspect the Conan local cache
        cmake.definitions["CMAKE_PROJECT_Sentry-Native_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["CMAKE_PROJECT_crashpad_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True
        cmake.definitions["CRASHPAD_ZLIB_SYSTEM"] = True

        # crashpad is out of process, breakpad is in process
        # crashpad is forced across all platforms
        cmake.definitions["SENTRY_BACKEND"] = "crashpad"
        if self.settings.os == "Windows":
            cmake.definitions["SENTRY_TRANSPORT"] = "winhttp"
        else:
            cmake.definitions["SENTRY_TRANSPORT"] = "curl"
            
        cmake.definitions["SENTRY_BUILD_TESTS"] = False
        cmake.definitions["SENTRY_BUILD_EXAMPLES"] = False
        cmake.definitions["SENTRY_PIC"] = False if self.settings.os == "Windows" else self.options.fPIC
        
        if not self.options.shared:
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = True

        cmake.configure(source_folder=os.path.join(self.source_folder, self._checkout_folder))
        return cmake

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self._configure_cmake().install()
