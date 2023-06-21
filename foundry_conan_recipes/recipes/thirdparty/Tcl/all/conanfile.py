# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
import stat
from types import SimpleNamespace
from conans import ConanFile, tools, AutoToolsBuildEnvironment

class TclConan(ConanFile):
    license = "TCL"
    author = "Tcl Core Team"
    url = "https://www.tcl.tk/"
    description = "Tcl (Tool Command Language) is a very powerful but easy to learn dynamic programming language, suitable for a very wide range of uses, including web and desktop applications, networking, administration, testing and many more."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "*"
    no_copy_source = False  # Windows builds in-source
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True


    def _configure_tokens(self):
        # TCL libs and binaries names vary significantly between versions,
        # platforms, debug, shared, etc. This function concentrates this
        # logic to reduce conditional logic elsewhere.
        if hasattr(self, 'names'):
            return

        self.names = SimpleNamespace()

        is_windows = self.settings.os == "Windows"
        ver = tools.Version(self.version)

        self.uses_zlib = ver >= "8.6.0"

        self.names.tclver = f'{ver.major}.{ver.minor}'
        self.names.libtype = 'SHARED' if self.options.shared else 'STATIC'
        self.names.libprefix = '' if is_windows else 'lib'

        extensions = {
            'SHARED': {
                        "Windows": '.dll',
                        "Linux": '.so',
                        "Macos": '.dylib'},
            'STATIC': {
                        "Windows": '.lib',
                        "Linux": '.a',
                        "Macos": '.a'}
        }
        self.names.libext = extensions[self.names.libtype][str(self.settings.os)]
        self.names.binext = '.exe' if is_windows else ''

        self.names.libdir = 'bin' if is_windows and self.options.shared else 'lib'

        # Windows builds add a non-trivial suffix to the library names
        # Linux and Mac only uses a suffix of 'g' for debug builds for old (8.4.x) versions
        tclib_suffix = ''
        tclsh_suffix = ''
        static = not self.options.shared
        debug = self.settings.build_type == "Debug"
        if is_windows:
            tclib_suffix += 't' if ver >= "8.6.0" else ''   # threading is enabled by default on versions >= 8.6
            tclib_suffix += 's' if static else ''
            tclib_suffix += 'g' if debug else ''
            tclib_suffix += 'x' if static else ''

            tclsh_suffix = tclib_suffix   # On Windows, the tclsh binary also uses this suffix
        else:
            # On unixy OSs, only add the g suffix for old (e.g. 8.4.x) versions
            tclib_suffix += 'g' if debug and ver < "8.6.0" else ''
        self.names.libsuffix = tclib_suffix

        tclshver = f'{ver.major}{ver.minor}' if is_windows else self.names.tclver    # On windows, tcl files with versions omit the .

        self.names.tclsh = 'tclsh' + tclshver + tclsh_suffix + self.names.binext     # Full filename of tclsh executable
        self.names.tcllib_name = 'tcl' + tclshver + tclib_suffix                     # Name known to the linker, e.g. tcl8.6g
        self.names.tcllib_basename = self.names.libprefix + self.names.tcllib_name   # Filename basename, e.g. libtcl8.6g (if the platform uses the lib_ prefix)
        self.names.tcllib = self.names.tcllib_basename + self.names.libext           # Full filename, e.g. libtcl8.6g.so

        self.names.tclimplib = self.names.tcllib_basename + ".lib" if is_windows and self.options.shared else None


    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name.lower())

    @property
    def _run_unit_tests(self):
        return "TCL_RUN_UNITTESTS" in os.environ

    def requirements(self):
        self._configure_tokens()
        if self.uses_zlib:
            self.requires("zlib/1.2.11@thirdparty/development")

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("patchelf/0.11@thirdparty/development")

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def configure(self):
        self._configure_tokens()
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.uses_zlib:
            self.options["zlib"].shared = False

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"], args="--no-checkout")  # Avoid issues with line-endings in master by not checking it out
        git.checkout(version_data["git_hash"])

    def build(self):
        self._configure_tokens()
        src_dir = os.path.join(self.source_folder, self._checkout_folder)
        if self.settings.os == "Windows":
            with tools.chdir(os.path.join(src_dir, "win")):
                make_opts = []
                if self.settings.build_type == "Debug":
                    make_opts.append("symbols")
                if not self.options.shared:
                    make_opts.append("static")
                    make_opts.append("msvcrt")

                make_args = [
                    "INSTALLDIR={}".format(self.package_folder),
                    "OPTS={}".format(",".join(make_opts)),
                    "MACHINE=AMD64",
                    "OUTDIR={}".format(self.build_folder),
                    "TMPDIR={}".format(self.build_folder)
                    ]

                if self.uses_zlib:
                    make_args.append("ZLIB_INCLUDE_DIR={}".format(self.deps_cpp_info["zlib"].include_paths[0]))
                    make_args.append("ZLIB_LIBRARY={}".format(os.path.join(self.deps_cpp_info["zlib"].lib_paths[0], self.deps_cpp_info["zlib"].libs[0])))

                self.run("nmake -f makefile.vc {}".format(" ".join(make_args)))

                if self._run_unit_tests:
                    self.run("nmake -f makefile.vc test {}".format(" ".join(make_args)))

                self.run("nmake -f makefile.vc install {}".format(" ".join(make_args)))

                # standard naming (copy from, e.g. tcl86tg.exe to plain tclsh.exe)
                shutil.copyfile(
                    os.path.join(self.package_folder, "bin", self.names.tclsh),
                    os.path.join(self.package_folder, "bin", "tclsh.exe"),
                )
        else:
            config_args = [
                "--prefix={}".format(self.package_folder),
                "--enable-shared" if self.options.shared else "--disable-shared",
                "--enable-symbols" if self.settings.build_type == "Debug" else "--disable-symbols"
            ]
            if self.settings.os == "Macos":
                config_args.append("--disable-framework")
                config_args.append("--enable-aqua")

            autotools = AutoToolsBuildEnvironment(self)
            if not self.options.shared:
                autotools.flags.append("-fvisibility=hidden")
            autotools.configure(configure_dir=os.path.join(src_dir, "unix"), args=config_args)

            autotools.make()
            if self._run_unit_tests:
                autotools.make(target="test")
            autotools.install(args=["-j1"])  # has to be single threaded

    def _write_cmake_config_file(self):
        self._configure_tokens()
        tokens = dict()
        tokens["TCL_DIR"] = self.names.libdir
        tokens["TCL_LIBNAME"] = self.names.tcllib_basename
        tokens["TCL_LIBEXT"] = self.names.libext
        tokens["TCL_LIBTYPE"] = self.names.libtype
        tokens["TCL_USE_ZLIB"] = "TRUE" if self.uses_zlib else "FALSE"

        config_in_path = os.path.join(self.source_folder, "config.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(
            config_out_dir, "TCLConfig.cmake"
        )
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def package(self):
        self._configure_tokens()
        def _make_path_writeable(path):
            mode = os.stat(path).st_mode
            mode = mode | stat.S_IWRITE
            os.chmod(path, mode)

        def _make_directory_writeable(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for dir_path in [os.path.join(root, d) for d in dirs]:
                    _make_path_writeable(dir_path)
                for file_path in [os.path.join(root, f) for f in files]:
                    _make_path_writeable(file_path)

        _make_directory_writeable(self.package_folder)
        self._write_cmake_config_file()
        if self.options.shared:
            tclsh_path = os.path.join(self.package_folder, "bin", self.names.tclsh)
            if self.settings.os == "Macos":
                # fix relative paths for the framework and shell application
                tcl_dylib_path = os.path.join(
                    self.package_folder,
                    "lib",
                    self.names.tcllib
                )
                tcl_dylib_id = f"@rpath/{self.names.tcllib}"
                self.run(
                    "install_name_tool -id {} {}".format(tcl_dylib_id, tcl_dylib_path)
                )

                self.run(
                    "install_name_tool -change {} {} {}".format(
                        tcl_dylib_path, tcl_dylib_id, tclsh_path
                    )
                )
                self.run(
                    "install_name_tool -add_rpath @executable_path/../lib {}".format(
                        tclsh_path
                    )
                )
            elif self.settings.os == "Linux":
                patchelf_path = os.path.join(
                    self.deps_cpp_info["patchelf"].bin_paths[0], "patchelf"
                )
                self.run(
                    r"{} --set-rpath \$ORIGIN/../lib {}".format(
                        patchelf_path, tclsh_path
                    )
                )
                tcl_so_path = os.path.join(self.package_folder, "lib", self.names.tcllib)
                self.run("{} --remove-rpath {}".format(patchelf_path, tcl_so_path))

    def package_info(self):
        self._configure_tokens()
        if self.settings.os == "Windows":
            if self.settings.os == "Windows":
                self.user_info.Windows_Lib_Suffix = self.names.libsuffix
            if self.options.shared:
                if self.settings.os == "Windows":
                    self.cpp_info.libs.append(self.names.tclimplib)
                elif self.settings.os in ("Linux", "Macos"):
                    self.cpp_info.libs.append(self.names.tcllib_name)
            else:
                if self.settings.os == "Windows":
                    self.cpp_info.defines.append("STATIC_BUILD")
                    self.cpp_info.libs.append(self.names.tcllib)
                else:
                    self.cpp_info.libs.append(self.names.tcllib_name)
                    if self.settings.os == "Macos":
                        self.cpp_info.frameworks.append("CoreFoundation")

