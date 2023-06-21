# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, CMake, tools


class GrpcConan(ConanFile):
    name = "grpc"
    license = "Apache-2.0"
    author = "Google"
    url = "https://github.com/grpc/grpc"
    description = "gRPC is a modern, open source, high-performance remote procedure call (RPC) framework that can run anywhere."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [False], # see https://github.com/grpc/grpc/blob/master/BUILDING.md#build-from-source for why shared builds are not recommended
        "fPIC": [True, False]
    }
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake_paths"

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    # these are runtime requirements because gRPC's CMake config file does a find on all of them
    requires = [
        "abseil/20211102.0",
        "c-ares/[~1]",
        "OpenSSL/[~1.1.1m]",
        "protobuf/[~3]@thirdparty/development",
        "re2/2022-02-01",
        "zlib/[~1.2.11]@thirdparty/development",
    ]

    @property
    def _run_unit_tests(self):
        # note that this does add a lot more to the build
        return "GRPC_RUN_UNITTESTS" in os.environ

    def build_requirements(self):
        if self._run_unit_tests:
            self.build_requires("GoogleBenchmark/1.3.0@thirdparty/development")

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.options["abseil"].shared = False
        self.options["c-ares"].shared = False
        self.options["OpenSSL"].shared = False
        self.options["protobuf"].shared = False
        self.options["re2"].shared = False
        self.options["zlib"].shared = False
        if self._run_unit_tests:
            self.options["GoogleBenchmark"].shared = False

    def source(self):
        # Note, the build docs, https://github.com/grpc/grpc/blob/master/BUILDING.md#clone-the-repository-including-submodules, do
        # recommend using submodules to get thirdparty dependencies, but we can provide them all in Conan
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        if self._run_unit_tests:
            git.checkout(version_data["git_hash"], submodule="recursive") # needing some actual code from Google Test to build tests
        else:
            git.checkout(version_data["git_hash"])

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_PROJECT_grpc_INCLUDE"] = os.path.join(self.install_folder, "conan_paths.cmake")

        cmake.definitions["gRPC_BUILD_CSHARP_EXT"] = "OFF"
        cmake.definitions["gRPC_BACKWARDS_COMPATIBILITY_MODE"] = "OFF"
        # these use find_package rather than via a submodule
        cmake.definitions["gRPC_ZLIB_PROVIDER"] = "package"
        cmake.definitions["gRPC_CARES_PROVIDER"] = "package"
        cmake.definitions["gRPC_RE2_PROVIDER"] = "package"
        cmake.definitions["gRPC_SSL_PROVIDER"] = "package"
        cmake.definitions["gRPC_PROTOBUF_PROVIDER"] = "package"
        cmake.definitions["Protobuf_USE_STATIC_LIBS"] = "ON"
        cmake.definitions["gRPC_ABSL_PROVIDER"] = "package"

        if self._run_unit_tests:
            cmake.definitions["gRPC_BUILD_TESTS"] = "ON"
            cmake.definitions["gRPC_BENCHMARK_PROVIDER"] = "package"
        else:
            cmake.definitions["gRPC_BUILD_TESTS"] = "OFF"

        if not self.options.shared:
            cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        return cmake

    def build(self):
        self.configure_cmake().build()
        if self._run_unit_tests:
            src_dir = os.path.join(self.source_folder, self._source_subfolder)
            # This requires a revisit, as it's not done via CTest, and always seems to want to build code again
            # https://github.com/grpc/grpc/blob/master/CONTRIBUTING.md#building--running-tests
            self.run(f"python {src_dir}/tools/run_tests/run_tests.py -l c++")

    def package(self):
        self.configure_cmake().install()

    def package_info(self):
        # TODO: needed if consumers other than CMake are used (but aren't currently tested)
        pass
