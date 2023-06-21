# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools

class FontconfigConan(ConanFile):
    name = "Fontconfig"
    license = "HPND"
    url = "https://www.freedesktop.org/wiki/Software/fontconfig/"
    description = "Fontconfig is a library for configuring and customizing font access."
    author = "Keith Packard et al"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { "shared": False, "fPIC": True }
    revision_mode = "scm"
    exports_sources = "cmake/*"

    package_originator = "External"
    package_exportable = True

    requires = [
        "Expat/2.2.0@thirdparty/development", # needed as runtime dependency to satisfy the transient link behaviour
        "Freetype/2.10.4@thirdparty/development",
    ]

    build_requires = [
        "gperf/3.1@thirdparty/development",
    ]

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @property
    def _run_unit_tests(self):
        return "FONTCONFIG_RUN_UNITTESTS" in os.environ

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

    def _configure(self):
        autotools = AutoToolsBuildEnvironment(self)
        args = [
            "--disable-libxml2", # force using expat
            "--with-expat={}".format(self.deps_cpp_info["Expat"].rootpath),
            "--sysconfdir=/etc",
            "--localstatedir=/var",
        ]
        if not self.options.shared:
            args.extend([
                "--enable-static", "--disable-shared"
            ])
            autotools.flags.append("-fvisibility=hidden")

        autotools.configure(args=args)
        return autotools

    def _environment(self):
        # see http://bio.gsi.de/DOCS/SOFTWARE/fontconfig.html
        freetype = self.deps_cpp_info["Freetype"]
        expat = self.deps_cpp_info["Expat"]

        freetype_cflags = f'-I{freetype.include_paths[0]} -I{freetype.include_paths[0]}/freetype2'
        freetype_cflags += ' '.join([f'-D{d}' for d in expat.defines])

        freetype_libs = ' '.join([f'-L{lib_path}' for lib_path in freetype.lib_paths])
        freetype_libs = ' '.join([f'-l{lib}' for lib in freetype.libs])
        env = {
            # second include search path is for ft2build.h which is included without the freetype namespace
            "FREETYPE_CFLAGS": freetype_cflags,
            "FREETYPE_LIBS": freetype_libs,
            "PATH": [self.deps_cpp_info["gperf"].bin_paths[0]],
        }
        return env

    def build(self):
        with tools.environment_append(self._environment()):
            src_dir = os.path.join(self.source_folder, self._source_subfolder)
            with tools.chdir(src_dir):
                self.run("./autogen.sh --noconf") # don't run the configure script automatically, so there is control of it with AutoToolsBuildEnvironment
                autotools = self._configure()
                autotools.make()
                if self._run_unit_tests:
                    autotools.make(args=["check"])

    def _configure_cmake_file(self, filename):
        tokens = {}

        # Version format x.y.z.w upsets semver.
        ver = self.version.split(".")
        tokens["FONTCONFIG_VERSION_MAJOR"] = ver[0]
        tokens["FONTCONFIG_VERSION_MINOR"] = ver[1]
        tokens["FONTCONFIG_VERSION_PATCH"] = ver[2]

        src_dir = os.path.join(self.source_folder, "cmake")
        src_filename = os.path.join(src_dir, "{}.in".format(filename))

        with open(src_filename, "r") as src_file:
            src_contents = src_file.read()

        dst_dir = os.path.join(self.package_folder, "cmake")
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)

        dst_filename = os.path.join(dst_dir, filename)
        with open(dst_filename, "wt") as dst_file:
            dst_file.write(src_contents.format(**tokens))

    def package(self):
        with tools.environment_append(self._environment()):
            src_dir = os.path.join(self.source_folder, self._source_subfolder)
            with tools.chdir(src_dir):
                # don't run the full install - just the executables part, because we've encoded the sysconfigdir to work in a privileged location, so install-data and install will fail
                self._configure().make(target="install-exec")
                # populate the public headers manually
                self.copy("*.h", src="Fontconfig_src/fontconfig", dst="include/fontconfig")
        self.copy("*.cmake", src="cmake", dst="cmake")
        self._configure_cmake_file("FontconfigConfigVersion.cmake")

    def package_info(self):
        self.cpp_info.libs = ["fontconfig"] + self.deps_cpp_info["Freetype"].libs + self.deps_cpp_info["Expat"].libs
