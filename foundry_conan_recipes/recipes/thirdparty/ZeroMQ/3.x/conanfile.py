# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os, shutil
from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild

class ZeroMQConan(ConanFile):
    name = "ZeroMQ"
    license = "LGPL-3.0-or-later"
    author = "Pieter Hintjens"
    url = "https://github.com/zeromq/libzmq"
    description = """The ZeroMQ lightweight messaging kernel is a library which extends the standard socket interfaces 
                     with features traditionally provided by specialised messaging middleware products"""
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True], "fPIC": [True]}
    default_options = {"shared": True, "fPIC": True}
    exports_sources = "*"
    no_copy_source = True
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    @property
    def _get_library_name(self):
        debug = "_d" if self.settings.build_type == "Debug" and self.settings.os == "Windows" else ""
        return "libzmq{}".format(debug)

    @property
    def _get_msbuild_solution(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        return os.path.join(src_dir, "builds", "msvc", "msvc10.sln")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

        if self.settings.os == "Windows":
            self._upgrade_ms_build_scripts()

    def _upgrade_ms_build_scripts(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        msbuild = MSBuild(self)
        try:
            msbuild.build(self._get_msbuild_solution, targets=None, upgrade_project=True)
        except Exception as e:
            self.output.warn("There was an upgrade exception, but continuing:\n{}".format(e))

        # Need to retarget solution for latest SDK if using visual Studio 2017 (as a bug means this isn't done as part of upgrade)
        if self.settings.compiler.version == "15":
            sdk_version = "10.0.17763.0"
            tools.replace_in_file(
                os.path.join(src_dir, "builds", "msvc", "libzmq", "libzmq.vcxproj"),
                "<PropertyGroup Label=\"Globals\">",
                "<PropertyGroup Label=\"Globals\"><WindowsTargetPlatformVersion>{}</WindowsTargetPlatformVersion>".format(sdk_version),
                False
            )

    def build(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        if self.settings.os == "Windows":
            msbuild_platforms = {"x86": "Win32", "x86_64": "x64"}
            msbuild = MSBuild(self)
            msbuild.build(
                self._get_msbuild_solution,
                targets=["libzmq"],
                upgrade_project=True,
                platforms=msbuild_platforms,
                build_type=self.settings.build_type
            )
        else:
            autotools = AutoToolsBuildEnvironment(self)
            autotools_vars = autotools.vars

            #enforce debug build, as the built in --enable-debug does not create debug files
            if self.settings.build_type == "Debug":
                autotools_vars['CFLAGS'] += ' -g -O0'
                autotools_vars['CXXFLAGS'] += ' -g -O0'

            with tools.environment_append(autotools_vars):
                autotools.configure(configure_dir=src_dir, args=["--disable-static"])
                autotools.make()

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"

        tokens = {}
        tokens["ZEROMQ_LIBTYPE"] = "SHARED"
        tokens["ZEROMQ_LIBEXT"] = ".dll" if is_windows else ".so" if is_linux else ".dylib"
        tokens["ZEROMQ_LIBDIR"] = "bin" if is_windows else "lib"
        tokens["ZEROMQ_LIBNAME"] = self._get_library_name

        config_in_path = os.path.join(self.source_folder, "ZeroMQConfig.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "ZeroMQConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def package(self):
        if self.settings.os == "Windows":
            src_dir = os.path.join(self.source_folder, self._source_subfolder)
            bin_dir = os.path.join(src_dir, "bin")
            lib_dir = os.path.join(src_dir, "lib")
            include_dir = os.path.join(src_dir, "include")
            self.copy("*.dll", "bin", "{}".format(bin_dir), keep_path=False)
            self.copy("*.lib", "lib", "{}".format(lib_dir), keep_path=False)
            self.copy("*.h", "include", "{}".format(include_dir), keep_path=True)
            self.copy("*.pdb", "bin", "{}".format(bin_dir), keep_path=False)
        else:
            autotools = AutoToolsBuildEnvironment(self)
            autotools_vars = autotools.vars
            with tools.environment_append(autotools_vars):
                autotools.install()

                # remove pkgconfig folder
                lib_path = os.path.join(self.package_folder, "lib")
                pkgfolder = os.path.join(lib_path, "pkgconfig")
                if os.path.isdir(pkgfolder):
                    shutil.rmtree(pkgfolder)

                # Make the dylib's relocatable
                if self.settings.os == "Macos":
                    dylib_path = os.path.join(lib_path, "{}.dylib".format(self._get_library_name))
                    args = ["install_name_tool", "-id", "@rpath/{}.dylib".format(self._get_library_name), dylib_path]
                    self.run(" ".join(args))

        self._write_cmake_config_file()

    def package_info(self):
        # TODO as need to verify in something Jenkins can reproduce
        self.cpp_info.libs = [self._get_library_name]

