# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conans import ConanFile, AutoToolsBuildEnvironment, tools

import os, re, shutil, glob, pathlib
from os import path
from jinja2 import Environment, FileSystemLoader


class FFmpegConan(ConanFile):
    name = "FFmpeg"
    settings = ["os", "arch", "compiler", "build_type"]
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    url = "https://ffmpeg.org"
    author = "Fabrice Bellard"
    license = "LGPL-2.1-or-later"
    exports_sources = "*.cmake.in"

    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    build_requires = [
        "yasm/1.3.0",
        "zlib/1.2.11@thirdparty/development"
    ]


    def build_requirements(self):
        if self.settings.os == 'Windows':
            # The order of these packages matters!
            self.build_requires("mingw_installer/8.1@foundry/stable")
            self.build_requires("msys2_installer/20161025@foundry/stable")


    def configure(self):
        # These aren't needed for a C library
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd


    @property
    def _source_subfolder(self):
        return f"{self.name}_src"


    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])


    @property
    def _config_args(self):
        # not using `--enable-rpath` because it writes absolute paths on the build machine
        arch = "arm64" if "arm" in self.settings.arch else "x86_64"
        flags = [
            "--enable-shared",
            "--disable-static",
            '--enable-zlib',
            "--enable-pic",
            "--disable-doc",
            f"--arch={arch}",
            "--disable-symver", # Avoid having the .58.100 suffix in the file names
        ]

        if self.settings.os == "Windows":
            flags.append("--target-os=mingw32")
        elif self.settings.os == "Macos":
            flags.append("--install-name-dir='@rpath'")
            # standard RPATHs to load from this package
            # and also an application bundle with dylibs in Contents/Frameworks
            # and also when dylibs are in the same folder as the tools
            flags.append("--extra-ldexeflags=-Wl,-rpath,@executable_path/../lib -Wl,-rpath,@executable_path/../Frameworks -Wl,-rpath,@executable_path")
        elif self.settings.os == "Linux":
            # standard RPATHs to load from this package
            # and also an application layout with the shared libs beside this executable
            # this expression is get \$$ORIGIN in the configure script, translating to $ORIGIN on the eventual linker command
            flags.append("--extra-ldexeflags=-Wl,-rpath,\\\$\$ORIGIN/../lib -Wl,-rpath,\\\$\$ORIGIN")

        if self.settings.build_type == "Debug":
            flags.extend(["--disable-optimizations", "--disable-mmx", "--disable-stripping", "--enable-debug"])

        return flags


    def build(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)

        with tools.environment_append({"PATH" : [self.deps_cpp_info["yasm"].bin_paths[0]]}):
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            if self.settings.os == "Windows":
                # Because it is helpfully handing in MSVC flags to gcc, remove these flags
                autotools.flags = []
                autotools.cxxflags = []
            autotools.configure(configure_dir=src_dir, args=self._config_args)
            autotools.make(args=[f"-j{tools.cpu_count()}"])
            autotools.install()


    def _produce_config_files(self):
        if not path.exists(path.join(self.package_folder, "cmake")):
            os.makedirs(path.join(self.package_folder, "cmake"))

        v = tools.Version(self.version)
        data = {
            "version_major": v.major,
            "version_minor": v.minor,
            "version_patch": v.patch,
            "os": self.settings.os,
            "shsuffix": ".dylib" if self.settings.os == "Macos" else ".so", # Only valid on Mac and Linux
        }

        if self.settings.os == "Windows":
            # On Windows these libraries have a version specifier in their name,
            # so instead of `avdevice.dll` we end up with `avdevice-42.dll`.
            # Unfortunately, there is no straightforward way to find out what version
            # which dll will have before building, so we resort to looking at the file
            # names and changing our Cmake accordingly.

            libraries_to_find = {
                "avdevice", "avfilter", "avformat", "avcodec", "avutil",
                "swresample", "swscale"
            }

            cmake_variables = {library: f"{library.upper()}_DLL_SUFFIX" for library in libraries_to_find}

            # We have to define all these variables not to break the CMake template
            # they are used in.
            library_suffixes = {key: "" for key in cmake_variables.values()}
            bin_path = pathlib.Path(self.package_folder) / "bin"
            for file in bin_path.glob("**/*.dll"):
                filepath = pathlib.Path(file)
                for library_name, variable in cmake_variables.items():
                    # We'd want to find files that looks like this:
                    #     avdevice-42.dll
                    #     avformat-3.dll
                    # so the `version` part would be `-42` and `-3` respectively.
                    match = re.match(fr"{library_name}(?P<version>-\d+).dll", filepath.name)
                    if not match:
                        continue
                    library_suffixes[variable] = match.group("version")
            data.update(library_suffixes)

        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _config_file(file_name):
            template = env.get_template(file_name + ".in")
            template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))

        _config_file("FFmpegConfig.cmake")
        _config_file("FFmpegConfigVersion.cmake")


    def package(self):
        self._produce_config_files()

        self.output.info("moving lib files into the lib directory")
        for lib_file in glob.glob(path.join(self.package_folder, "bin", "*.lib")):
            shutil.move(lib_file, path.join(self.package_folder, "lib"))


    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.sharedlinkflags.append("-Wl,-Bsymbolic")
        elif self.settings.os == "Windows":
            self.cpp_info.libs.extend(['ws2_32', 'secur32', 'shlwapi', 'strmiids', 'vfw32', 'bcrypt'])
