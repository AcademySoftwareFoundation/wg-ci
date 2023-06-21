# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment

class FreetypeConan(ConanFile):
    name = "Freetype"
    license = "FTL"
    url = "https://www.freetype.org/"
    description = "Freetype is a freely available software library to render fonts."
    author = "David Turner, Robert Wilhelm, and Werner Lemberg"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [False], "fPIC": [True, False]}
    default_options = { "shared": False, "fPIC": True }
    revision_mode = "scm"

    exports_sources = "*"
 
    package_originator = "External"
    package_exportable = True

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _run_unit_tests(self):
        return "FREETYPE_RUN_UNITTESTS" in os.environ

    def source(self):
        version_data = self.conan_data["sources"][self.version]

        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])

        if self.settings.os == "Windows":
            # Checkout a standalone Cygwin installation that is required to run "./configure".
            cygwin_dir = os.path.join(self.source_folder, "cygwin-standalone")
            git = tools.Git(folder=cygwin_dir)
            git.clone("git@a_gitlab_url:libraries/conan/thirdparty/cygwin-standalone.git",
                        branch="foundry/v3.1.7")
            tools.untargz(os.path.join(cygwin_dir, "cygwin64.tgz"))

    def _gather_common_config_args(self):
        config_args = [
            "--enable-rpath",
            "--disable-doc",
            "--without-bzip2",
            "--without-png",
            "--without-zlib",
        ]

        if self.settings.os != "Windows":
            if self.options.fPIC:
                config_args.append("--enable-pic")

        if self.options.shared:
            config_args.extend([
                "--enable-shared",
                "--disable-static",
            ])
        else:
            config_args.extend([
                "--disable-shared",
                "--enable-static",
            ])

        if self.settings.build_type == "Debug":
            config_args.extend([
                "--disable-optimizations",
                "--disable-stripping",
                "--enable-debug",
            ])

        return config_args

    def _build_others(self, src_dir, config_args):
        with tools.chdir(src_dir):
            autotools = AutoToolsBuildEnvironment(self, win_bash=False)
            autotools.configure(args=config_args)

            make_args = [
                "TOP_DIR={}".format(os.path.join(self.build_folder, src_dir)),
                "-j{}".format(tools.cpu_count()),
            ]
            autotools.make(args=make_args)

    def _build_windows(self, src_dir, config_args):
        build_dir = os.path.normpath(self.build_folder).replace("\\", "/")
        config_args.append(r'--prefix=\"{}\"'.format(build_dir))

        with tools.chdir(src_dir):
            cygwin_dir = os.path.join(self.source_folder, "cygwin64", "bin")
            with tools.environment_append({"PATH": [cygwin_dir]}):
                # autogen.sh has \r\n line endings.
                tools.dos2unix("autogen.sh")

                self.run("{} -c \"CC=cl ./autogen.sh {}\"".format(
                    os.path.join(cygwin_dir, "sh.exe"),
                    ' '.join(config_args)))

            compiler_runtime = str(self.settings.get_safe("compiler.runtime"))
            config_name = str(self.settings.build_type)
            if compiler_runtime.startswith("MD"):
                config_name += " Multithreaded"
            else:
                config_name += " Singlethreaded"

            if self.options.shared:
                config_type = "DynamicLibrary"

                # Append symbol export definitions to ftoption.h.
                export_decls = \
                    "#define FT_BASE(x)       __declspec(dllexport) x\n" \
                    "#define FT_EXPORT(x)     __declspec(dllexport) x\n" \
                    "#define FT_EXPORT_DEF(x) __declspec(dllexport) x\n" \
                    "FT_END_HEADER\n"
                tools.replace_in_file(
                    "include/freetype/config/ftoption.h",
                    "FT_END_HEADER", export_decls)
            else:
                config_type = "StaticLibrary"

            platform_name = "x64"
            known_toolchains = {
                "14": "v140",  # VS 2015.
                "15": "v141",  # VS 2017.
                "16": "v142",  # VS 2019.
            }
            compiler_ver = str(self.settings.get_safe("compiler.version"))
            if compiler_ver in known_toolchains:
                toolchain_name = known_toolchains[compiler_ver]
            else:
                raise ValueError("Unknown MSVC compiler version {}.".format(compiler_ver))

            # Freetype doesn't provide x64 targets directly, so hack the
            # Visual Studio project files instead.
            tools.replace_in_file("builds/win32/vc2010/freetype.vcxproj",
                                    "Win32", platform_name)
            tools.replace_in_file("builds/win32/vc2010/freetype.sln",
                                    "Win32", platform_name)

            self.run(
                "msbuild builds\\win32\\vc2010\\freetype.sln /m "
                    "/p:Configuration=\"{}\" "
                    "/p:ConfigurationType=\"{}\" "
                    "/p:Platform=\"{}\" "
                    "/p:PlatformToolset=\"{}\""
                        .format(config_name,
                                config_type,
                                platform_name,
                                toolchain_name))

    def build(self):
        src_dir = os.path.join(self.source_folder, self._source_subfolder)
        config_args = self._gather_common_config_args()

        if self.settings.os == "Windows":
            self._build_windows(src_dir, config_args)
        else:
            self._build_others(src_dir, config_args)

    def _configure_cmake_file(self, filename):
        tokens = {}

        # Version format x.y.z.w upsets semver.
        ver = self.version.split(".")
        tokens["FREETYPE_VERSION_MAJOR"] = ver[0]
        tokens["FREETYPE_VERSION_MINOR"] = ver[1]
        tokens["FREETYPE_VERSION_PATCH"] = ver[2]

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
        src_folder = os.path.join(self.source_folder, self._source_subfolder)
        include_dir = os.path.join(src_folder, "include")
        self.copy("*.h", src=include_dir, dst="include")

        self.copy("*.cmake", src="cmake", dst="cmake")
        self._configure_cmake_file("FreetypeConfigVersion.cmake")

        build_dir = os.path.join(src_folder, "objs")
        self.copy("*.lib", src=build_dir, dst="lib", keep_path=False)
        self.copy("*.dll", src=build_dir, dst="bin", keep_path=False)
        self.copy("*.so",  src=build_dir, dst="lib", keep_path=False)
        self.copy("*.a",   src=build_dir, dst="lib", keep_path=False)
        self.copy("*.pdb", src=build_dir, dst="bin", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            debug = "_D" if self.settings.build_type == "Debug" else ""
            self.cpp_info.libs = [ "freetype250MT" + debug + ".lib" ]
        else:
            self.cpp_info.libs = [ "freetype" ]
