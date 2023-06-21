# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import stat
from conans import ConanFile, tools


class PerlConan(ConanFile):
    name = "Perl"
    license = "Artistic-1.0-Perl"
    author = "Larry Wall and others"
    url = "https://www.perl.org/"
    description = "The Perl language interpreter."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True],
        "fPIC": [True, False],
    }  # only shared builds supported for consistency across platforms
    default_options = {"shared": True, "fPIC": True}
    exports_sources = ("config.cmake.in")
    no_copy_source = (
        False  # this is because Windows doesn't support out of source builds
    )
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "PERL_RUN_UNITTESTS" in os.environ

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("patchelf/0.11@thirdparty/development")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")

    def build(self):
        src_dir = os.path.join(self.source_folder, self._checkout_folder)
        if self.settings.os == "Windows":
            # using BUILD_STATIC=define and ALL_STATIC=define result in multiply defined symbols errors, hence only shared builds
            args = ["INST_TOP={}".format(self.package_folder)]

            if self.settings.build_type == "Debug":
                args.append("CFG=DebugFull")

            if self.settings.compiler.version == "14":
                args.append("CCTYPE=MSVC140")
            elif self.settings.compiler.version == "15":
                args.append("CCTYPE=MSVC141")
            elif self.settings.compiler.version == "16":
                args.append("CCTYPE=MSVC142")
            elif self.settings.compiler.version == "17":
                args.append("CCTYPE=MSVC143")
            else:
                raise RuntimeError(
                    "Unsupported {} compiler version: {}".format(
                        self.settings.compiler, self.settings.compiler.version
                    )
                )

            # only in-source builds are supported
            with tools.chdir(os.path.join(src_dir, "win32")):
                # this only builds shared
                self.run("nmake.exe -f Makefile {}".format(" ".join(args)))
                if self._run_unit_tests:
                    self.run("nmake.exe test")
                self.run("nmake.exe -f Makefile install {}".format(" ".join(args)))
        else:
            args = []
            args.append("-d")  # use default answers (makes config step non-interactive)
            args.append("-e")  # don't ask for input at end of config step
            args.append("-Dprefix={}".format(self.package_folder))
            args.append("-Dmksymlinks")  # makes out of source builds work
            args.append(
                "-Duserelocatableinc"
            )  # always make the distribution relocatable
            if self.options.shared:
                # in vanilla source drops, this is incompatible with relocatable
                # for the reasons of rpaths
                # but since we fix these up ourselves, a patch in the code skips the intended error
                args.append("-Duseshrplib")
            if self.settings.build_type == "Debug":
                args.append("-DEBUGGING=both") # adds debug symbol generation
                args.append("-Doptimize=' '") # disable optimisations
            self.run("sh {}/Configure {}".format(src_dir, " ".join(args)))
            self.run("make -j{}".format(tools.cpu_count()))
            if self._run_unit_tests:
                self.run("make test")
            self.run("make install")

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"
        os_subdir = "x86_64-linux" if is_linux else "darwin-2level"
        versioned_lib_dir = os.path.join(
            "lib", "perl5", self.version, os_subdir, "CORE"
        )
        tokens = {}
        tokens["PERL_LIBTYPE"] = "SHARED"
        tokens["PERL_INCLUDEDIR"] = "lib/CORE" if is_windows else versioned_lib_dir
        tokens["PERL_LIBDIR"] = "bin" if is_windows else versioned_lib_dir
        tokens["PERL_LIBPREFIX"] = "" if is_windows else "lib"
        tokens["PERL_LIBEXT"] = (
            ".dll" if is_windows else ".so" if is_linux else ".dylib"
        )
        major, minor, _ = self.version.split(".")
        tokens["PERL_LIBNAME"] = (
            "perl{}{}".format(major, minor) if is_windows else "perl"
        )

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

    def package(self):
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
            perl_interpreter_path = os.path.join(self.package_folder, "bin", "perl")
            is_windows = self.settings.os == "Windows"
            is_linux = self.settings.os == "Linux"
            os_subdir = (
                "windows"
                if is_windows
                else "x86_64-linux"
                if is_linux
                else "darwin-2level"
            )
            versioned_lib_dir = os.path.join(
                "lib", "perl5", self.version, os_subdir, "CORE"
            )
            if self.settings.os == "Macos":
                perl_dylib_path = os.path.join(
                    self.package_folder, versioned_lib_dir, "libperl.dylib"
                )
                perl_dylib_install_name = os.path.join(
                    "@rpath",
                    "perl5",
                    self.version,
                    "darwin-2level",
                    "CORE",
                    "libperl.dylib",
                )
                self.run(
                    "install_name_tool -id {} {}".format(
                        perl_dylib_install_name, perl_dylib_path
                    )
                )

                # don't need to do the versioned interpreter, as it's a hard link
                self.run(
                    "install_name_tool -change {} {} {}".format(
                        perl_dylib_path, perl_dylib_install_name, perl_interpreter_path
                    )
                )
                self.run(
                    "install_name_tool -add_rpath @executable_path/../lib {}".format(
                        perl_interpreter_path
                    )
                )
            elif self.settings.os == "Linux":
                patchelf_path = os.path.join(
                    self.deps_cpp_info["patchelf"].bin_paths[0], "patchelf"
                )
                self.run(
                    r"{} --set-rpath \$ORIGIN/../{} {}".format(
                        patchelf_path, versioned_lib_dir, perl_interpreter_path
                    )
                )

    def package_info(self):
        # TODO
        pass
