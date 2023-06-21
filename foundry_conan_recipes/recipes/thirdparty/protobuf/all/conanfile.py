# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools


class ProtobufConan(ConanFile):
    name = "protobuf"
    license = "BSD-3-Clause"
    author = "Google"
    url = "https://developers.google.com/protocol-buffers"
    description = "Protocol buffers are a language-neutral, platform-neutral extensible mechanism for serializing structured data."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    generators = "cmake_paths"
    revision_mode = "scm"
    package_originator = "External"
    package_exportable = True
    short_paths = True # some rather long paths in the source tree

    # zlib is referenced in a public header
    requires = ("zlib/[~1.2.11]@thirdparty/development")

    @property
    def _run_unit_tests(self):
        # currently requires a googletest submodule, instead of a separate find
        return "PROTOBUF_RUN_UNITTESTS" in os.environ

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_protobuf_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")
        cmake.definitions["protobuf_VERBOSE"] = "ON"
        cmake.definitions["protobuf_BUILD_PROTOC_BINARIES"] = "ON"
        cmake.definitions["protobuf_BUILD_LIBPROTOC"] = "ON"
        cmake.definitions["protobuf_DISABLE_RTTI"] = "ON"
        cmake.definitions["protobuf_WITH_ZLIB"] = "ON"
        cmake.definitions["protobuf_BUILD_TESTS"] = "ON" if self._run_unit_tests else "OFF"
        cmake.definitions["protobuf_BUILD_CONFORMANCE"] = "OFF"
        cmake.definitions["protobuf_BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "OFF" # always want dynamic runtime
        if not self.options.shared:
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder, "cmake"))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self._run_unit_tests:
            cmake.test()

    def package(self):
        self._configure_cmake().install()

    def package_info(self):
        # TODO:
        pass
