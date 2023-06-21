# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class SqliteConan(ConanFile):
    name = "SQLite"
    license = "blessing"
    author = "SQLite Consortium members"
    url = "https://www.sqlite.org"
    description = "Self-contained, serverless, in-process SQL database engine."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "*"
    no_copy_source = True
    short_paths = True  # some batch file "for loops" are too long
    revision_mode = "scm"

    build_requires = "Tcl/8.6.10@thirdparty/development"

    package_originator = "External"
    package_exportable = True

    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "SQLITE_RUN_UNITTESTS" in os.environ

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        self.options["Tcl"].shared = False

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        src_dir = os.path.join(
            os.path.normpath(self.source_folder), self._checkout_folder
        )
        if self.settings.os == "Windows":
            make_args = [
                "TOP={}".format(src_dir),
                "TCLDIR={}".format(
                    os.path.normpath(self.deps_cpp_info["Tcl"].rootpath)
                ),
                "DEBUG={}".format("3" if self.settings.build_type == "Debug" else "0"),
                "OPTIMIZATIONS={}".format(
                    "0" if self.settings.build_type == "Debug" else "2"
                ),
                "TCLSUFFIX={}".format(self.deps_user_info["Tcl"].Windows_Lib_Suffix),
                "USE_CRT_DLL=1",
                "DYNAMIC_SHELL={}".format("1" if self.options.shared else "0"),
            ]
            self.run(
                "nmake -f {} {}".format(
                    os.path.join(src_dir, "Makefile.msc"), " ".join(make_args)
                )
            )
            if self._run_unit_tests:
                if not self.options["TCL"].shared:
                    self.output.info(self.deps_cpp_info["zlib"])
                    self.output.info(self.deps_cpp_info["zlib"].lib_paths[0])
                    self.output.info(self.deps_cpp_info["zlib"].libs[0])
                    make_args.append("TEST_CCONV_OPTS=-DSTATIC_BUILD")
                    make_args.append(
                        'LDOPTS="User32.lib Netapi32.lib -LIBPATH:{} {}"'.format(
                            self.deps_cpp_info["zlib"].lib_paths[0],
                            self.deps_cpp_info["zlib"].libs[0],
                        )
                    )
                # quicktest rather than smoketest as it builds less
                self.run(
                    "nmake -f {} {} quicktest".format(
                        os.path.join(src_dir, "Makefile.msc"), " ".join(make_args)
                    )
                )
        else:
            config_args = [
                "--prefix={}".format(self.package_folder),
                "--disable-tcl",  # otherwise it installs into tcl
                "--disable-readline",  # readline is GPL
                "--disable-editline",  # seems related to readline
            ]
            if self.options.shared:
                config_args.append("--enable-shared")
                config_args.append("--disable-static")
            else:
                config_args.append("--disable-shared")
                config_args.append("--enable-static")
            config_args.append(
                "--enable-debug"
                if self.settings.build_type == "Debug"
                else "--disable-debug"
            )
            with tools.environment_append(
                {"PATH": [self.deps_cpp_info["Tcl"].bin_paths[0]]}
            ):
                autotools = AutoToolsBuildEnvironment(self)
                if not self.options.shared:
                    autotools.flags.append("-fvisibility=hidden")
                autotools.defines.append("SQLITE_ENABLE_COLUMN_METADATA")
                autotools.configure(configure_dir=src_dir, args=config_args)
                make_args = ["-j{}".format(tools.cpu_count())]
                autotools.make(args=make_args)
                if self._run_unit_tests:
                    # see https://www.sqlite.org/testing.html
                    if self.settings.os == "Macos" and not self.options["TCL"].shared:
                        with tools.environment_append(
                            {
                                "LIBS": "-framework {}".format(
                                    self.deps_cpp_info["TCL"].frameworks[0]
                                )
                            }
                        ):
                            autotools.make(args=["smoketest", "-j1"])
                    else:
                        autotools.make(args=["smoketest", "-j1"])
                autotools.install(args=["-j1"])

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"
        tokens = {}
        if self.options.shared:
            tokens["SQLITE_LIBTYPE"] = "SHARED"
            tokens["SQLITE_LIBRARY_SUBDIR"] = "bin" if is_windows else "lib"
            tokens["SQLITE_LIBPREFIX"] = "" if is_windows else "lib"
            tokens["SQLITE_LIBEXT"] = (
                ".dll" if is_windows else ".so" if is_linux else ".dylib"
            )
        else:
            tokens["SQLITE_LIBTYPE"] = "STATIC"
            tokens["SQLITE_LIBRARY_SUBDIR"] = "lib"
            tokens["SQLITE_LIBPREFIX"] = "lib"
            tokens["SQLITE_LIBEXT"] = ".lib" if is_windows else ".a"
        tokens["SQLITE_LIBNAME"] = "sqlite3"

        config_in_path = os.path.join(self.source_folder, "config.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(
            config_out_dir, "{}Config.cmake".format(self.name)
        )
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def _delete_la_file(self, major):
        # .la file from libtool has hard coded paths to the build machine
        libsqlite_la_path = os.path.join(
            self.package_folder, "lib", "libsqlite{}.la".format(major)
        )
        if os.path.isfile(libsqlite_la_path):
            os.unlink(libsqlite_la_path)

    def _delete_pkgconfig(self):
        # pkgconfig files have hard coded paths to the build machine
        libsqlite_pkgconfig_path = os.path.join(self.package_folder, "lib", "pkgconfig")
        if os.path.isdir(libsqlite_pkgconfig_path):
            shutil.rmtree(libsqlite_pkgconfig_path)

    def package(self):
        self._write_cmake_config_file()
        major, _, _ = self.version.split(".")
        if self.settings.os == "Windows":
            sqlite_v = "sqlite{}".format(major)
            self.copy("{}.h".format(sqlite_v), dst="include")
            self.copy("{}ext.h".format(sqlite_v), dst="include")
            if self.options.shared:
                self.copy("{}.dll".format(sqlite_v), dst="bin")
                self.copy("{}.lib".format(sqlite_v), dst="lib")
                self.copy("{}.pdb".format(sqlite_v), dst="bin")
            else:
                self.copy("lib{}.lib".format(sqlite_v), dst="lib")
            self.copy("{}.exe".format(sqlite_v), dst="bin")
            self.copy("{}sh.pdb".format(sqlite_v), dst="bin")
        elif self.settings.os == "Macos":
            if self.options.shared:
                # fixing dylib id names
                libsqlite_dylib_path = os.path.join(
                    self.package_folder, "lib", "libsqlite{}.0.dylib".format(major)
                )
                libsqlite_dylib_id = "@rpath/libsqlite{}.0.dylib".format(major)
                self.run(
                    "install_name_tool -id {} {}".format(
                        libsqlite_dylib_id, libsqlite_dylib_path
                    )
                )
            self._delete_la_file(major)
            self._delete_pkgconfig()
        elif self.settings.os == "Linux":
            self._delete_la_file(major)
            self._delete_pkgconfig()

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = (
                ["sqlite3.lib"] if self.options.shared else ["libsqlite3.lib"]
            )
        else:
            self.cpp_info.libs = ( ["sqlite3", "pthread", "dl"] )
