# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import glob
import os
import time

from conans import ConanFile, tools, AutoToolsBuildEnvironment


class Libxml2Conan(ConanFile):
    name = "libxml2"
    url = "https://github.com/bincrafters/conan-libxml2"
    description = "libxml2 is a software library for parsing XML documents"
    author = "The Foundry"
    topics = "XML", "parser", "validation"
    homepage = "https://xmlsoft.org"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    revision_mode = "scm"
    options = {"shared": [True, False], "fPIC": [True, False], "iconv": [True, False], "lzma": [True, False],
               "zlib": [True, False]}
    default_options = {'shared': True, 'fPIC': True, "iconv": False, "lzma": False, "zlib": True}
    _source_subfolder = "git"

    package_originator = "External"
    package_exportable = True

    def requirements(self):
        if self.options.zlib:
            self.requires("zlib/1.2.11@thirdparty/development", "private")
        if self.options.lzma:
            self.requires("lzma/5.2.4@foundry/stable")
        if self.options.iconv:
            self.requires("libiconv/1.15@foundry/stable")

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

        # Files written by Git may present slightly different timestamps.
        # docs will attempt to be rebuilt if the modification dates are slightly off
        # This presents a problem, as makeinfo might not be on the build machines
        # We'll touch every file after checkout, so they all share the same modification time.
        timestamp = time.time()
        with tools.chdir(self._source_subfolder):
            for file_path in tools.relative_dirs('.'):
                tools.touch(file_path, (timestamp, timestamp))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        if self.options.shared:
            self.options["zlib"].shared = False

    def build(self):
        if self._is_msvc:
            self._build_windows()
        else:
            self._build_with_configure()

    def _build_windows(self):
        with tools.chdir(os.path.join(self._source_subfolder, 'win32')):
            debug = "yes" if self.settings.build_type == "Debug" else "no"
            static = "no" if self.options.shared else "yes"

            configure_command = "cscript configure.js " \
                                "zlib=%d lzma=%d iconv=%d compiler=msvc prefix=%s cruntime=/%s debug=%s static=%s include=\"%s\" lib=\"%s\"" % (
                                    1 if self.options.zlib else 0,
                                    1 if self.options.lzma else 0,
                                    1 if self.options.iconv else 0,
                                    self.package_folder,
                                    self.settings.compiler.runtime,
                                    debug,
                                    static,
                                    ";".join(self.deps_cpp_info.include_paths),
                                    ";".join(self.deps_cpp_info.lib_paths))
            self.output.info(configure_command)
            self.run(configure_command)

            # Fix library names because they can be not just zlib.lib
            if self.options.zlib:
                libname = self.deps_cpp_info['zlib'].libs[0]
                if not libname.endswith('.lib'):
                    libname += '.lib'
                tools.replace_in_file("Makefile.msvc",
                                      "LIBS = $(LIBS) zlib.lib",
                                      "LIBS = $(LIBS) %s" % libname)
            if self.options.lzma:
                libname = self.deps_cpp_info['lzma'].libs[0]
                if not libname.endswith('.lib'):
                    libname += '.lib'
                tools.replace_in_file("Makefile.msvc",
                                      "LIBS = $(LIBS) liblzma.lib",
                                      "LIBS = $(LIBS) %s" % libname)
            if self.options.iconv:
                libname = self.deps_cpp_info['libiconv'].libs[0]
                if not libname.endswith('.lib'):
                    libname += '.lib'
                tools.replace_in_file("Makefile.msvc",
                                      "LIBS = $(LIBS) iconv.lib",
                                      "LIBS = $(LIBS) %s" % libname)

            self.run("nmake /f Makefile.msvc install")

    def _build_with_configure(self):
        in_win = self.settings.os == "Windows"
        env_build = AutoToolsBuildEnvironment(self, win_bash=in_win)
        if not in_win:
            env_build.fpic = self.options.fPIC
        full_install_subfolder = self.build_folder + "/local-package"
        with tools.environment_append(env_build.vars):
            with tools.chdir(self._source_subfolder):
                # fix rpath
                if self.settings.os == "Macos":
                    tools.replace_in_file("configure", r"-install_name \$rpath/", "-install_name ")
                configure_args = ['--with-python=no', '--prefix=%s' % full_install_subfolder]
                if env_build.fpic:
                    configure_args.extend(['--with-pic'])
                if self.options.shared:
                    configure_args.extend(['--enable-shared', '--disable-static'])
                else:
                    configure_args.extend(['--enable-static', '--disable-shared'])
                configure_args.extend([('--with-zlib=%s' % self.deps_cpp_info[
                    "zlib"].rootpath) if self.options.zlib else '--without-zlib'])
                configure_args.extend(['--with-lzma' if self.options.lzma else '--without-lzma'])
                configure_args.extend(['--with-iconv' if self.options.iconv else '--without-iconv'])

                # Disable --build when building for iPhoneSimulator. The configure script halts on
                # not knowing if it should cross-compile.
                build = None
                if self.settings.os == "iOS" and self.settings.arch == "x86_64":
                    build = False

                env_build.configure(args=configure_args, build=build)
                env_build.make(args=["install"])

    def package(self):
        self.copy(pattern="*.h", dst="include", src="local-package/include", symlinks=True)
        self.copy(pattern="*.so*", dst="lib", src="local-package/lib", symlinks=True, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="local-package/lib", symlinks=True, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="local-package/lib", keep_path=False)
        self.copy(pattern="*.dll", dst="lib", src="local-package/lib", keep_path=False)

        # copy package license
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        if self.settings.os == "Windows":
            # There is no way to avoid building the tests, but at least we don't want them in the package
            for prefix in ["run", "test"]:
                for test in glob.glob("%s/bin/%s*" % (self.package_folder, prefix)):
                    os.remove(test)
        for header in ["win32config.h", "wsockcompat.h"]:
            self.copy(pattern=header, src=os.path.join(self._source_subfolder, "include"),
                      dst=os.path.join("include", "libxml2"), keep_path=False)
        if self._is_msvc:
            # remove redundant libraries to avoid confusion
            os.unlink(os.path.join(self.package_folder, 'lib', 'libxml2_a_dll.lib'))
            os.unlink(os.path.join(self.package_folder, 'lib',
                                   'libxml2_a.lib' if self.options.shared else 'libxml2.lib'))

    def package_info(self):
        if self._is_msvc:
            self.cpp_info.libs = ['libxml2' if self.options.shared else 'libxml2_a']
        else:
            self.cpp_info.libs = ['xml2']
        self.cpp_info.includedirs = [os.path.join("include", "libxml2")]
        if not self.options.shared:
            self.cpp_info.defines = ["LIBXML_STATIC"]
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            self.cpp_info.libs.append('m')
        if self.settings.os == "Windows":
            self.cpp_info.libs.append('ws2_32')
