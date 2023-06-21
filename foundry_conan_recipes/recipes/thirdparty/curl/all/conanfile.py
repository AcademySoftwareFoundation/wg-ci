# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, CMake, tools
from os import path, mkdir
from jinja2 import Environment, FileSystemLoader
from semver import SemVer

class Curl(ConanFile):
    name = "Curl"
    description = "command line tool and library for transferring data with URLs"
    author = "Daniel Stenberg"
    license = "curl"
    url = "https://www.openssl.org/"

    revision_mode = "scm"

    settings = "arch", "os", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "openssl_version": ["1.0", "1.1"]}
    default_options = {"shared": False, "fPIC": True, "openssl_version": "1.0"}

    exports_sources = "*.cmake.in"

    requires = [
        "zlib/[~1.2.11]@thirdparty/development",
    ]

    package_originator = "External"
    package_exportable = True

    generators = "cmake_paths"

    def requirements(self):
        if self.options.openssl_version == "1.1":
            if "arm" in self.settings.arch:
                self.requires("OpenSSL/[~1.1.1m]")
            else:
                self.requires("OpenSSL/[~1.1.1g]@thirdparty/development")
        else:
            self.requires("OpenSSL/[~1.0.2u]@thirdparty/development")

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    
    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC


    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    _cmake = None
    def _config_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["CMAKE_PROJECT_CURL_INCLUDE"] = path.join(self.install_folder, "conan_paths.cmake")
        self._cmake.definitions["BUILD_TESTING"] = "OFF"
        self._cmake.definitions["BUILD_CURL_EXE"] = "OFF"
        self._cmake.definitions["CURL_DISABLE_LDAP"] = "ON"
        self._cmake.definitions["CURL_STATICLIB"] = "OFF" if self.options.shared else "ON"
        self._cmake.definitions["CMAKE_DEBUG_POSTFIX"] = ""
        self._cmake.definitions["CMAKE_USE_LIBSSH2"] = "OFF"

        # all these options are exclusive. set just one of them
        # mac builds do not use cmake so don't even bother about darwin_ssl
        self._cmake.definitions["CMAKE_USE_WINSSL"] = "OFF"
        self._cmake.definitions["CMAKE_USE_OPENSSL"] = "ON"

        if self.settings.os != "Windows":
            self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        self._cmake.configure(source_folder=self._source_subfolder, args=["-U*_DIR"])
        return self._cmake


    def build(self):
        cmake = self._config_cmake()
        cmake.build()


    def _write_cmake_config_file(self):
        p = path.join(self.package_folder, "cmake")
        if not path.exists(p):
            mkdir(p)

        ver = SemVer(self.version, False)
        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {
                "version_major": str(ver.major),
                "version_minor": str(ver.minor),
                "version_patch": str(ver.patch),
                "os": self.settings.os,
                "bt": self.settings.build_type,
                "shared": self.options.shared,
            }

            data["libsuffix"] = ".a"
            if self.options.shared:
                data["libsuffix"] = ".dylib" if self.settings.os == "Macos" else ".so"
            
            interpreter_template = env.get_template(file_name + ".in")
            interpreter_template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))

        _configure("CURLConfig.cmake")
        _configure("CURLConfigVersion.cmake")


    def package(self):
        cmake = self._config_cmake()
        cmake.install()
        self._write_cmake_config_file()