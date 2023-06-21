# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment

class JpegConan(ConanFile):
    name = "JPEG"
    license = "IJG"
    author = "Richard M. Stallman"
    url = "http://www.ijg.org/"
    description = "This package contains C software to implement JPEG image compression and decompression"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "*"
    no_copy_source = False
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def build(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        if self.settings.os == "Windows":
            args = []
            if self.settings.build_type == "Release":
                args.append('nodebug=1')

            # setup-jconfig is required to create the jconfig.h file
            self.run("nmake -f Makefile.vc {}".format(" ".join(args)), cwd=src_dir)
        else:
            autotools = AutoToolsBuildEnvironment(self)
            autotools_vars = autotools.vars

            # override the libtool definition as the makefile defaults to ./libtool
            autotools_vars['LIBTOOL'] = 'libtool'

            if self.settings.build_type == "Debug":
                autotools_vars['CFLAGS'] += ' -g -O0'

            # add the build folder to the includepath so that jconfig.h can be picked up
            autotools_vars['CFLAGS'] += ' -fvisibility=hidden'

            with tools.environment_append(autotools_vars):
                autotools.configure(configure_dir=src_dir, args=['--disable-shared'])
                autotools.make()

                # setup the install folder structure (not done by the makefile) before running install
                os.makedirs(os.path.join(self.package_folder, 'bin'))
                os.makedirs(os.path.join(self.package_folder, 'include'))
                os.makedirs(os.path.join(self.package_folder, 'lib'))
                os.makedirs(os.path.join(self.package_folder, 'man/man1'))

                # install installs the binaries and manuals, while install-lib installs the library
                # and include files
                autotools.make(target="install")

                if self.version == '6b':
                    autotools.make(target="install-lib")

    def _write_cmake_config_file(self):
        is_windows = self.settings.os == "Windows"

        tokens = {}
        tokens["JPEG_LIBTYPE"] = "STATIC"
        tokens["JPEG_LIBEXT"] = ".lib" if is_windows else ".a"
        tokens["JPEG_LIBNAME"] = "libjpeg" if is_windows else "libjpeg"

        config_in_path = os.path.join(self.source_folder, "JPEGConfig.cmake.in")
        with open(config_in_path, "r") as cmake_config:
            cmake_config_contents = cmake_config.read()

        config_out_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(config_out_dir):
            os.makedirs(config_out_dir)
        config_out_path = os.path.join(config_out_dir, "JPEGConfig.cmake")
        with open(config_out_path, "wt") as cmake_config:
            cmake_config.write(cmake_config_contents.format(**tokens))

    def package(self):
        if self.settings.os == "Windows":
            # no install step in Windows, so do it manually
            src_dir = os.path.join(self.source_folder, self._source_subfolder)

            bin_dir = os.path.join(self.package_folder, "bin")
            self.copy("*.exe", src=src_dir, dst=bin_dir)

            include_dir = os.path.join(self.package_folder, "include")
            package_include_files = ["jconfig.h", "jerror.h", "jmorecfg.h", "jpeglib.h"]
            for include in package_include_files:
                self.copy(include, src=src_dir, dst=include_dir)

            lib_dir = os.path.join(self.package_folder, "lib")
            self.copy("libjpeg.lib", src=src_dir, dst=lib_dir)

        self._write_cmake_config_file()

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["libjpeg.lib"]
        else:
            self.cpp_info.libs = ["jpeg"]

