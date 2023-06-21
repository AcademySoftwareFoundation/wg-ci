# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
import stat
from conans import ConanFile, tools


class OpensslConan(ConanFile):
    name = "OpenSSL"
    license = "OpenSSL"
    author = "Eric Andrew Young and Tim Hudson (SSLeay) / Mark Cox, Ralf Engelschall, Stephen Henson, Ben Laurie, and Paul Sutton"
    url = "https://www.openssl.org/"
    description = "A toolkit for the Transport Layer Security (TLS) and Secure Sockets Layer (SSL) protocols"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "*"
    no_copy_source = False  # only in-source builds are supported
    revision_mode = "scm"

    build_requires = "Perl/[~5]"

    package_originator = "External"
    package_exportable = True

    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "OPENSSL_RUN_UNITTESTS" in os.environ

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("nasm/2.14.02@thirdparty/development")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        src_dir = os.path.join(self.source_folder, self._checkout_folder)
        perl_dir = os.path.join(self.deps_cpp_info["Perl"].rootpath, "bin")
        perl = os.path.join(perl_dir, "perl")
        config_args = [
            "--prefix={}".format(self.package_folder),
            "--openssldir={}".format(self.package_folder),
            "no-comp",  # see https://stackoverflow.com/questions/23772816/when-do-i-need-zlib-in-openssl/23829863 (Compression leaks information in protocols like HTTPS and SPDY, so you should not use it.)
            "no-asm", # see https://a_gitlab_url/libraries/conan/recipes/-/issues/68
        ]
        config_args.append("shared" if self.options.shared else "no-shared")
        if self.settings.os == "Windows":
            perl += ".exe"
            config_args.append(
                "debug-VC-WIN64A"
                if self.settings.build_type == "Debug"
                else "VC-WIN64A"
            )
            if not self.options.shared:
                # static builds wanting to use -MT[d] (makes for noisy build though)
                config_args.append(
                    "-MDd" if self.settings.build_type == "Debug" else "-MD"
                )
            nasm_path = self.deps_cpp_info["nasm"].rootpath
            # in-source builds only
            with tools.chdir(src_dir):
                self.run(
                    "{} {}/Configure {}".format(perl, src_dir, " ".join(config_args))
                )
                ms_makefile = r"ms\ntdll.mak" if self.options.shared else r"ms\nt.mak"
                with tools.environment_append({"PATH": [nasm_path, perl_dir]}):
                    self.run(r"ms\do_win64a")
                    self.run("nmake -f {}".format(ms_makefile))
                    if self._run_unit_tests:
                        self.run("nmake -f {} tests".format(ms_makefile))
                    self.run("nmake -f {} install".format(ms_makefile))
        else:
            if self.settings.os == "Macos":
                config_args.append(
                    "debug-darwin64-x86_64-cc"
                    if self.settings.build_type == "Debug"
                    else "darwin64-x86_64-cc"
                )
            elif self.settings.os == "Linux":
                config_args.append(
                    "debug-linux-x86_64"
                    if self.settings.build_type == "Debug"
                    else "linux-x86_64"
                )
            if not self.options.shared:
                config_args.append("-fvisibility=hidden")

            if self.options.fPIC:
                config_args.append("-fPIC")

            # in-source builds only
            with tools.chdir(src_dir):
                self.run(
                    "{} {}/Configure {}".format(perl, src_dir, " ".join(config_args))
                )
                self.run("make depend")
                # note, saw failure on the make call once, resolved by changing to single threaded
                self.run("make -j{}".format(tools.cpu_count()))
                if self._run_unit_tests:
                    self.run("make tests")
                self.run("make install_sw -j1")

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"
        tokens = {}
        if self.options.shared:
            tokens["OPENSSL_LIBTYPE"] = "SHARED"
            tokens["OPENSSL_LIBDIR"] = "bin" if is_windows else "lib"
            tokens["OPENSSL_LIBEXT"] = (
                ".dll" if is_windows else ".so" if is_linux else ".dylib"
            )
            tokens["OPENSSL_CRYPTO_LIBNAME"] = "libeay32" if is_windows else "libcrypto"
            tokens["OPENSSL_SSL_LIBNAME"] = "ssleay32" if is_windows else "libssl"
        else:
            tokens["OPENSSL_LIBTYPE"] = "STATIC"
            tokens["OPENSSL_LIBDIR"] = "lib"
            tokens["OPENSSL_LIBEXT"] = ".lib" if is_windows else ".a"
            tokens["OPENSSL_CRYPTO_LIBNAME"] = "libeay32" if is_windows else "libcrypto"
            tokens["OPENSSL_SSL_LIBNAME"] = "ssleay32" if is_windows else "libssl"

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

    def _delete_pkgconfig(self):
        # pkgconfig files have hard coded paths to the build machine
        pkgconfig_path = os.path.join(self.package_folder, "lib", "pkgconfig")
        if os.path.isdir(pkgconfig_path):
            shutil.rmtree(pkgconfig_path)

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

        if self.settings.os == "Macos" and self.settings.build_type == "Debug":
            # man page symbolic links are broken as they assume a case sensitive file system
            # see https://openssl-dev.openssl.narkive.com/o8qswtVS/openssl-org-2820-man-pages-case-in-sensitivity
            manpage_dir = os.path.join(self.package_folder, "man")
            if os.path.isdir(manpage_dir):

                def handle_error(func, path, exc_info):
                    if not os.access(path, os.W_OK):
                        os.chmod(path, stat.S_IWUSR)
                        func(path)

                shutil.rmtree(manpage_dir, onerror=handle_error)

        _make_directory_writeable(self.package_folder)

        self._write_cmake_config_file()

        self._delete_pkgconfig()

        if self.options.shared:
            if self.settings.os == "Macos":
                ssl_static_lib = os.path.join(self.package_folder, "lib", "libssl.a")
                if os.path.isfile(ssl_static_lib):
                    os.unlink(ssl_static_lib)
                crypto_static_lib = os.path.join(
                    self.package_folder, "lib", "libcrypto.a"
                )
                if os.path.isfile(crypto_static_lib):
                    os.unlink(crypto_static_lib)

                major, minor, _ = self.version.split(".")

                crypto_dynamic_lib = os.path.join(
                    self.package_folder,
                    "lib",
                    "libcrypto.{}.{}.0.dylib".format(major, minor),
                )
                crypto_install_name = "@rpath/libcrypto.{}.{}.0.dylib".format(
                    major, minor
                )
                self.run(
                    "install_name_tool -id {} {}".format(
                        crypto_install_name, crypto_dynamic_lib
                    )
                )

                ssl_dynamic_lib = os.path.join(
                    self.package_folder,
                    "lib",
                    "libssl.{}.{}.0.dylib".format(major, minor),
                )
                ssl_install_name = "@rpath/libssl.{}.{}.0.dylib".format(major, minor)
                self.run(
                    "install_name_tool -id {} {}".format(
                        ssl_install_name, ssl_dynamic_lib
                    )
                )
                self.run(
                    "install_name_tool -change {} {} {}".format(
                        crypto_dynamic_lib, crypto_install_name, ssl_dynamic_lib
                    )
                )

                def _fix_engine_dylib(engine_name):
                    engine_dynamic_lib = os.path.join(
                        self.package_folder,
                        "lib",
                        "engines",
                        "lib{}.dylib".format(engine_name),
                    )
                    self.run(
                        "install_name_tool -change {} {} {}".format(
                            crypto_dynamic_lib, crypto_install_name, engine_dynamic_lib
                        )
                    )

                _fix_engine_dylib("4758cca")
                _fix_engine_dylib("aep")
                _fix_engine_dylib("atalla")
                _fix_engine_dylib("capi")
                _fix_engine_dylib("chil")
                _fix_engine_dylib("cswift")
                _fix_engine_dylib("gmp")
                _fix_engine_dylib("gost")
                _fix_engine_dylib("nuron")
                _fix_engine_dylib("padlock")
                _fix_engine_dylib("sureware")
                _fix_engine_dylib("ubsec")

                ssl_app = os.path.join(self.package_folder, "bin", "openssl")
                self.run(
                    "install_name_tool -change {} {} {}".format(
                        crypto_dynamic_lib, crypto_install_name, ssl_app
                    )
                )
                self.run(
                    "install_name_tool -change {} {} {}".format(
                        ssl_dynamic_lib, ssl_install_name, ssl_app
                    )
                )
                self.run(
                    "install_name_tool -add_rpath @executable_path/../lib {}".format(
                        ssl_app
                    )
                )

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["libeay32.lib", "ssleay32.lib", "Advapi32.lib", "Crypt32.lib", "User32.lib", "Ws2_32.lib"]
        else:
            self.cpp_info.libs = ["ssl", "crypto", "dl", "pthread"]
