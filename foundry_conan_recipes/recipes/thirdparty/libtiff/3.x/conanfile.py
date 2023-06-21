# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment

class LibtiffConan(ConanFile):
    name = "libtiff"
    license = "libtiff"
    author = "Sam Leffler"
    url = "http://www.simplesystems.org/libtiff/"
    description = "TIFF provides support for the Tag Image File Format (TIFF), a widely used format for storing image data."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    exports_sources = "*"
    no_copy_source = True
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    requires = [("zlib/1.2.11@thirdparty/development"),
               ("JPEG/6b@thirdparty/development")]

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        if self.settings.os == "Windows":
            build_args = []

            build_args.append("ZIP_SUPPORT=1")
            build_args.append("ZLIB_INCLUDE=-I{}".format(self.deps_cpp_info["zlib"].include_paths[0]))
            build_args.append("ZLIB_LIB={}\\zlib.lib".format(self.deps_cpp_info["zlib"].lib_paths[0]))

            build_args.append("JPEG_SUPPORT=1")
            build_args.append("JPEG_INCLUDE=-I{}".format(self.deps_cpp_info["JPEG"].include_paths[0]))
            build_args.append("JPEG_LIB={}\\libjpeg.lib".format(self.deps_cpp_info["JPEG"].lib_paths[0]))

            if self.settings.build_type == "Debug":
                build_args.append("DEBUG_BUILD=1")

            self.run("nmake -f Makefile.vc {}".format(" ".join(build_args)), cwd=src_dir)
        else:
            autotools = AutoToolsBuildEnvironment(self)
            autotools_vars = autotools.vars

            config_args = []
            if self.settings.build_type == "Debug":
                autotools_vars['CFLAGS'] += ' -g -O0'
                autotools_vars['CXXFLAGS'] += ' -g -O0'

            zlib_package_folder =  self.deps_cpp_info["zlib"].rootpath
            config_args.append("--with-zlib-include-dir={}".format(os.path.join(zlib_package_folder, "include")))
            config_args.append("--with-zlib-lib-dir={}".format(os.path.join(zlib_package_folder, "lib")))

            JPEG_package_folder =  self.deps_cpp_info["JPEG"].rootpath
            config_args.append("--with-jpeg-include-dir={}".format(os.path.join(JPEG_package_folder, "include")))
            config_args.append("--with-jpeg-lib-dir={}".format(os.path.join(JPEG_package_folder, "lib")))

            if not self.options.shared:
                autotools_vars['CFLAGS'] += ' -fvisibility=hidden'
                autotools_vars['CXXFLAGS'] += ' -fvisibility=hidden -fvisibility-inlines-hidden'
                config_args.append("--disable-shared")

            with tools.environment_append(autotools_vars):
                autotools.configure(configure_dir=src_dir, args=config_args)
                autotools.make()
                autotools.make(target="check")
                autotools.install(args=["-j1"])

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"
        is_linux = self.settings.os == "Linux"
        tokens = {}
        if self.options.shared:
            tokens["LIBTIFF_LIBTYPE"] = "SHARED"
            tokens["LIBTIFF_LIBEXT"] = ".dll" if is_windows else ".so" if is_linux else ".dylib"
        else:
            tokens["LIBTIFF_LIBTYPE"] = "STATIC"
            tokens["LIBTIFF_LIBEXT"] = ".lib" if is_windows else ".a"

        tokens["LIBTIFF_LIBNAME"] = "libtiff"

        config_in_path = os.path.join(self.source_folder, "TIFFConfig.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "TIFFConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def _mac_change_lib_loader_path(self, lib_path, libs, input):
        for lib in libs:
            dylib_path = os.path.join(lib_path, lib)
            args = ["install_name_tool", "-change", dylib_path, "@rpath/{}.dylib".format(lib.split('.')[0]), input]
            self.run(" ".join(args))

    def package(self):
        if self.settings.os == "Windows":
            # no install step in Windows, so do it manually
            src_dir = os.path.join(self.source_folder, self._source_subfolder)

            bin_dir = os.path.join(self.package_folder, "bin")
            self.copy("*.exe", src=os.path.join(src_dir, "tools"), dst=bin_dir)

            libtiff_dir = os.path.join(src_dir, "libtiff")
            include_dir = os.path.join(self.package_folder, "include")
            package_include_files = ["tiff.h", "tiffconf.h", "tiffio.h", "tiffio.hxx", "tiffvers.h"]
            for include in package_include_files:
                self.copy(include, src=libtiff_dir, dst=include_dir)

            lib_dir = os.path.join(self.package_folder, "lib")
            self.copy("libtiff.lib", src=libtiff_dir, dst=lib_dir)
            if self.options.shared:
                self.copy("libtiff.dll", src=libtiff_dir, dst=lib_dir)

        else:
            lib_path = os.path.join(self.package_folder, "lib")
            bin_path = os.path.join(self.package_folder, "bin")

            if self.options.shared:
                # both static and dynamic libs are built, but we only want dynamic
                package_static_libs = ["libtiff.a", "libtiffxx.a"]
                for lib in package_static_libs:
                    staticlib_path = os.path.join(lib_path, lib)
                    if os.path.isfile(staticlib_path):
                        os.unlink(staticlib_path)

                if self.settings.os == "Macos":
                    # Make the dylib's relocatable
                    major = self.version.split('.')[0]
                    package_dynamic_libs = ["libtiff.{}.dylib".format(major), "libtiffxx.{}.dylib".format(major)]
                    for lib in package_dynamic_libs:
                        dylib_path = os.path.join(lib_path, lib)
                        args = ["install_name_tool", "-id", "@rpath/{}.dylib".format(lib.split('.')[0]), dylib_path]
                        self.run(" ".join(args))
                        self._mac_change_lib_loader_path(lib_path, package_dynamic_libs, dylib_path)

                    # Make the binaries relocatable
                    package_binaries = os.listdir(bin_path)
                    for binary in package_binaries:
                        binary_path = os.path.join(bin_path, binary)
                        self._mac_change_lib_loader_path(lib_path, package_dynamic_libs, binary_path)

        self._write_cmake_config_file()

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["libtiff.lib"]
        else:
            self.cpp_info.libs = ["tiff"]
