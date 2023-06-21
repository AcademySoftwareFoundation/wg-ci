# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.model.version import Version

class zlib(ConanFile):
    name = "zlib"
    settings = "os", "arch", "compiler", "build_type"
    author = "Jean-loup Gailly and Mark Adler"
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library (Also Free, Not to Mention Unencumbered by Patents)"
    url = "https://zlib.net/"
    license = "Zlib"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = { "shared": False, "fPIC": True }

    exports_sources = ("zlibConfig.cmake.in")
    no_copy_source = False # some builds are in-source
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True


    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)


    @property
    def _is_atleast_zlib129(self):
        # v1.2.9 changed the build such that
        # * you can build out of source
        # * -debug was added to configure
        version = Version(self.version)
        return version >= Version("1.2.9")


    @property
    def _run_unit_tests(self):
        return "ZLIB_RUN_UNITTESTS" in os.environ


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC


    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd


    def source(self):
        version_data = self.conan_data["sources"][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])


    def build(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        build_dir = self.build_folder if self._is_atleast_zlib129 else src_dir
        with tools.chdir(build_dir):
            if self.settings.os == "Windows":
                make_args = [
                    "-f",
                    os.path.join(src_dir, "win32", "Makefile.msc"),
                    "TOP={}".format(src_dir)
                ]
                if self.settings.build_type == "Debug":
                    make_args.append("LOC={}".format("\"-Od -MDd\""))
                self.run("nmake {}".format(" ".join(make_args)))
                if self._run_unit_tests:
                    self.run("nmake {} {}".format(" ".join(make_args), "testdll" if self.options.shared else "test"))
            else:
                autotools = AutoToolsBuildEnvironment(self)
                config_args = [
                    "--shared" if self.options.shared else "--static"
                ]
                if self._is_atleast_zlib129:
                    if self.settings.build_type == "Debug": config_args.append("--debug")
                else:
                    autotools.defines = ['ZLIB_DEBUG']
                if not self.options.shared:
                    autotools.flags.append("-fvisibility=hidden")
                autotools.configure(configure_dir=src_dir, args=config_args)
                autotools.make()
                if self._run_unit_tests:
                    autotools.make(args=["test", "-j1"])
                autotools.install(args=["-j1"])


    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"
        tokens = {}
        if self.options.shared:
            tokens["ZLIB_LIBTYPE"] = "SHARED"
            tokens["ZLIB_LIBEXT"] = ".dll" if is_windows else ".so" if is_linux else ".dylib"
        else:
            tokens["ZLIB_LIBTYPE"] = "STATIC"
            tokens["ZLIB_LIBEXT"] = ".lib" if is_windows else ".a"
        tokens["ZLIB_LIBNAME"] = "zlib" if is_windows else "libz"

        config_in_path = os.path.join(self.source_folder, "zlibConfig.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "zlibConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))


    def package(self):
        if self.settings.os == "Windows":
            # no install step in Makefiles, so do it manually
            src_dir = os.path.join(self.source_folder, self._source_subfolder)
            include_dir = os.path.join(self.package_folder, "include")
            self.copy("zlib.h", src=src_dir, dst=include_dir)
            self.copy("zconf.h", src=src_dir, dst=include_dir)
            lib_dir = os.path.join(self.package_folder, "lib")
            build_dir = self.build_folder if self._is_atleast_zlib129 else src_dir
            if self.options.shared:
                self.copy("zlib1.dll", src=build_dir, dst=lib_dir)
                self.copy("zdll.lib", src=build_dir, dst=lib_dir)
            else:
                self.copy("zlib.lib", src=build_dir, dst=lib_dir)
        else:
            lib_path = os.path.join(self.package_folder, "lib")
            if self.options.shared:
                # both static and dynamic libs are built, but we only want dynamic
                staticlib_path = os.path.join(lib_path, "libz.a")
                if os.path.isfile(staticlib_path):
                    os.unlink(staticlib_path)
                if self.settings.os == "Macos":
                    # make dylib relocatable
                    dylib_path = os.path.join(lib_path, "libz.{}.dylib".format(self.version))
                    self.run("install_name_tool -id @rpath/libz.dylib {}".format(dylib_path))
        self._write_cmake_config_file()


    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["zdll.lib"] if self.options.shared else ["zlib.lib"]
        else:
            self.cpp_info.libs = ["z"]
