# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.model.version import Version

class zlib4cudnn(ConanFile):
    name = "zlib4cudnn"
    settings = "os", "arch", "compiler", "build_type"
    author = "Jean-loup Gailly and Mark Adler"
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library (Also Free, Not to Mention Unencumbered by Patents)"
    url = "https://zlib.net/"
    license = "Zlib"

    options = {
        "shared": [True],
    }
    default_options = { "shared": True }

    no_copy_source = False # some builds are in-source
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True


    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)


    @property
    def _run_unit_tests(self):
        return "ZLIB_RUN_UNITTESTS" in os.environ


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
        build_dir = self.build_folder
        with tools.chdir(build_dir):
            if self.settings.os == "Windows":
                make_args = [
                    "-f",
                    os.path.join(src_dir, "win32", "Makefile.msc"),
                    "TOP={}".format(src_dir)
                ]
                if self.settings.build_type == "Debug":
                    make_args.append("LOC={}".format("\"-Od -MDd -DZLIB_WINAPI\""))
                else:
                    make_args.append("LOC={}".format("\"-DZLIB_WINAPI\""))
                self.run("nmake {}".format(" ".join(make_args)))
                if self._run_unit_tests:
                    self.run("nmake {} {}".format(" ".join(make_args), "testdll"))
            else:
                autotools = AutoToolsBuildEnvironment(self)
                config_args = ["--shared"]
                if self.settings.build_type == "Debug": config_args.append("--debug")
                autotools.configure(configure_dir=src_dir, args=config_args)
                autotools.make()
                if self._run_unit_tests:
                    autotools.make(args=["test", "-j1"])
                autotools.install(args=["-j1"])


    def package(self):
        # no install step in Makefiles, so do it manually
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        build_dir = self.build_folder
        if self.settings.os == "Windows":
            # Rename zlib1.dll to zlibwapi.dll - ignore implib since deployment only.
            shutil.copyfile(os.path.join(build_dir, "zlib1.dll"), os.path.join(self.package_folder, "zlibwapi.dll"))
        else:
            if self.settings.os == "Macos":
                # make dylib relocatable
                dylib_path = os.path.join(self.package_folder, "lib", "libz.{}.dylib".format(self.version))
                self.run("install_name_tool -id @rpath/libz.dylib {}".format(dylib_path))
            elif self.settings.os == "Linux":
                self.copy("libz.so", src=build_dir, dst=self.package_folder)


    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["zlibwapi.dll"]
        else:
            self.cpp_info.libs = ["z"]
