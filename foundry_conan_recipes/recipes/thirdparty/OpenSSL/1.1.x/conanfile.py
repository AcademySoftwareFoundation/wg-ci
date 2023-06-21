# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
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
    no_copy_source = True
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
        perl = os.path.join(self.deps_cpp_info["Perl"].rootpath, "bin", "perl")
        config_args = [
            "--prefix={}".format(self.package_folder),
            "--openssldir={}".format(self.package_folder),
            "no-comp",  # see https://stackoverflow.com/questions/23772816/when-do-i-need-zlib-in-openssl/23829863 (Compression leaks information in protocols like HTTPS and SPDY, so you should not use it.)
            "no-asm",   # avoids leaking symbols introduced from inline assembly (generated from Perl scripts) in static library builds, when linked into shared libraries (e.g. Qt5Network)
        ]
        config_args.append(
            "--debug" if self.settings.build_type == "Debug" else "--release"
        )
        config_args.append("shared" if self.options.shared else "no-shared")
        if self.settings.os == "Windows":
            perl += ".exe"
            config_args.append("VC-WIN64A")
            if not self.options.shared:
                # static builds wanting to use -MT[d]
                config_args.append(
                    "-MDd" if self.settings.build_type == "Debug" else "-MD"
                )
            nasm_path = self.deps_cpp_info["nasm"].rootpath
            with tools.environment_append({"PATH": [nasm_path]}):
                self.run(
                    "{} {}/Configure {}".format(perl, src_dir, " ".join(config_args))
                )
                self.run("nmake")
            if self._run_unit_tests:
                self.run("nmake tests")
            self.run("nmake install_sw")
        else:
            if not self.options.shared:
                config_args.append("-fvisibility=hidden")

            if self.options.fPIC:
                config_args.append("-fPIC")

            with tools.environment_append({"PERL": perl}):
                self.run("{}/config {}".format(src_dir, " ".join(config_args)))
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
            major, minor, _ = self.version.split(".")
            tokens["OPENSSL_CRYPTO_LIBNAME"] = (
                "libcrypto-{}_{}-x64".format(major, minor)
                if is_windows
                else "libcrypto"
            )
            tokens["OPENSSL_SSL_LIBNAME"] = (
                "libssl-{}_{}-x64".format(major, minor) if is_windows else "libssl"
            )
        else:
            tokens["OPENSSL_LIBTYPE"] = "STATIC"
            tokens["OPENSSL_LIBDIR"] = "lib"
            tokens["OPENSSL_LIBEXT"] = ".lib" if is_windows else ".a"
            tokens["OPENSSL_CRYPTO_LIBNAME"] = "libcrypto"
            tokens["OPENSSL_SSL_LIBNAME"] = "libssl"

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
                    "libcrypto.{}.{}.dylib".format(major, minor),
                )
                crypto_install_name = "@rpath/libcrypto.{}.{}.dylib".format(
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
                    "libssl.{}.{}.dylib".format(major, minor),
                )
                ssl_install_name = "@rpath/libssl.{}.{}.dylib".format(major, minor)
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

                padlock_dynamic_lib = os.path.join(
                    self.package_folder,
                    "lib",
                    "engines-{}.{}".format(major, minor),
                    "padlock.dylib",
                )
                self.run(
                    "install_name_tool -change {} {} {}".format(
                        crypto_dynamic_lib, crypto_install_name, padlock_dynamic_lib
                    )
                )

                capi_dynamic_lib = os.path.join(
                    self.package_folder,
                    "lib",
                    "engines-{}.{}".format(major, minor),
                    "capi.dylib",
                )
                self.run(
                    "install_name_tool -change {} {} {}".format(
                        crypto_dynamic_lib, crypto_install_name, capi_dynamic_lib
                    )
                )

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
            self.cpp_info.libs = ["libcrypto.lib", "libssl.lib", "Advapi32.lib", "Crypt32.lib", "User32.lib", "Ws2_32.lib"]
        else:
            self.cpp_info.libs = ["ssl", "crypto", "dl", "pthread"]
