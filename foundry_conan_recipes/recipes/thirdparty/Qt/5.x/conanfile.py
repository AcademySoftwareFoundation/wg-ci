# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from os import environ, path, makedirs, pathsep
from shutil import copyfile
from conans import ConanFile, tools

class QtConan(ConanFile):
    name = "Qt"
    license = "LGPL-2.1-or-later"
    author = "The Qt Team"
    url = "https://www.qt.io"
    description = "Everything you need for your entire software development life cycle. Qt is the fastest and smartest way to produce industry-leading software that users love."
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True], "with_webengine": [True, False], "GLBackend": ["OpenGL" ,"FoundryGL"]}
    default_options = {"shared": True, "with_webengine": True, "GLBackend": "OpenGL"}
    revision_mode = "scm"
    short_paths = True
    generators = "pkg_config"

    package_originator = "External"
    package_exportable = True

    @property
    def _useFoundryGLBackend(self):
        return self.options.GLBackend == "FoundryGL"

    build_requires = [
        "JPEG/9e",
        "OpenSSL/[~1.1.1m]",
        "Perl/[~5]",
        "PNG/1.6.37@thirdparty/development",
        "SQLite/3.32.3@thirdparty/development",
        "libtiff/[~4.3.0]",
    ]

    def requirements(self):
        if self._useFoundryGLBackend:
            self.requires("foundrygl/0.1@common/development")

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("jom/1.1.3@thirdparty/development")
        elif self.settings.os == "Linux":
            self.build_requires("Fontconfig/2.13.93@thirdparty/development") # Brings in Freetype and Expat.
            self.build_requires("gperf/3.1@thirdparty/development")
            self.build_requires("icu/69.1@thirdparty/development")
        if self.options.with_webengine:
            self.build_requires("pythontool/2.7.18-prebuilt") # WebEngine source requires specifically Python 2, but only to run, not to embed
            self.build_requires("nodejs/18.7.0")
            if self.settings.os == "Linux":
                self.build_requires("bison/3.8.2")
                self.build_requires("flex/2.6.4")
# TODO: required on linux, possibly others:      "pkgconfig/0.29.2@thirdparty/development",
# QTWebEngine, on linux at least,  needs:
#        "gperf" - manually installed on linux
#        "libicu66", "libicu-dev" - manually installed on Linux.
# xcb libxtst-dev libcups2 libcups2-dev libgcrypt20 libgcrypt20-dev build-essential ruby libasound2-dev libbz2-dev libcap-dev libdrm-dev libegl1-mesa-dev libnss3-dev libpci-dev libpulse-dev libudev-dev gyp ninja-build - manually installed on Linux.

    def _excluded_modules(self):
        # see https://www.qt.io/product/features#js-6-3
        # exclude all GPL-only licensed modules
        gpl_modules = [
            "qtcharts",
            "qtdatavis3d",
            "qtnetworkauth",
            "qtqa",
            "qtvirtualkeyboard",
            "qtwayland",
            "qtwebglplugin",
        ]
        if self.version >= "5.15.1":
            gpl_modules.extend([
                "qtlottie",
                "qtquick3d",
                "qtquicktimeline"
            ])
        excluded = []
        excluded.extend(gpl_modules)
        # exclude extras modules that aren't applicable to the platform
        excluded.append("qtandroidextras")
        if self.settings.os == "Windows":
            excluded.append("qtmacextras")
            excluded.append("qtx11extras")
        elif self.settings.os == "Linux":
            excluded.append("qtmacextras")
            excluded.append("qtwinextras")
        elif self.settings.os == "Macos":
            excluded.append("qtwinextras")
            excluded.append("qtx11extras")
        return excluded

    @property
    def _source_subfolder(self):
        return "{}_src".format(self.name)

    def configure(self):
        self.options["libtiff"].shared = False

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"])
        perl_dir = path.join(self.deps_cpp_info["Perl"].rootpath, "bin")
        perl = path.join(perl_dir, "perl")
        src_dir = path.join(self.source_folder, self._source_subfolder)
        # not all modules in Qt are desired/needed, so exclude them from the source checkout (i.e. their submodules are not populated)
        excluded_modules = self._excluded_modules()
        if not self.options.with_webengine:
            excluded_modules.extend(["qtwebengine", "qtwebview"])
        module_subset_expr = "--module-subset=default," + ",".join("-{}".format(module) for module in excluded_modules)
        self.run("{} init-repository {}".format(perl, module_subset_expr), cwd=src_dir)

    def _ensure_pc_files(self):
        if not self.settings.os == "Linux":
            return
        # currently our package names are incorrectly cased for what QtWebengine is looking for with pkg-config, so make copies
        # grep the Qt source for '"type": "pkgConfig" to see which dependencies are pkgConfig friendly
        if not path.isfile(path.join(self.install_folder, "fontconfig.pc")):
            copyfile(path.join(self.install_folder, "Fontconfig.pc"), path.join(self.install_folder, "fontconfig.pc"))
        if not path.isfile(path.join(self.install_folder, "expat.pc")):
            copyfile(path.join(self.install_folder, "Expat.pc"), path.join(self.install_folder, "expat.pc"))
        if not path.isfile(path.join(self.install_folder, "freetype2.pc")):
            copyfile(path.join(self.install_folder, "Freetype.pc"), path.join(self.install_folder, "freetype2.pc"))
        if not path.isfile(path.join(self.install_folder, "libpng.pc")):
            copyfile(path.join(self.install_folder, "PNG.pc"), path.join(self.install_folder, "libpng.pc"))
        if not path.isfile(path.join(self.install_folder, "sqlite3.pc")):
            copyfile(path.join(self.install_folder, "SQLite.pc"), path.join(self.install_folder, "sqlite3.pc"))

    @property
    def _cxx_std(self):
        """
        Default to C++ 14. This was VFX20 for Qt 5.12.11, and had also been used for VFX22, Qt 5.15.2 (albeit incorrectly).
        If VFX23 is detected, use C++17. This is mandated for GCC11 builds, and made consistent for all platforms.
        """
        cxx_std = "c++14"
        if tools.Version(self.version) >= "5.15.2":
            v = tools.Version(str(self.settings.compiler.version))
            if self.settings.compiler == "gcc":
                if v >= "11.0.0":
                    cxx_std = "c++17"
            elif self.settings.compiler == "Visual Studio":
                if v >= "17":
                    cxx_std = "c++17"
            elif self.settings.compiler == "apple-clang":
                os_version = self.settings.get_safe("os.version")
                if os_version and tools.Version(os_version) >= "11.0":
                    cxx_std = "c++17"
        return cxx_std

    @property
    def _perl_lib(self):
        perl_lib = None
        if self.settings.os == "Linux":
            base_lib = path.join(self.deps_cpp_info["Perl"].rootpath, "lib", "perl5", "5.36.0")
            perl_lib = pathsep.join([base_lib, path.join(base_lib, "x86_64-linux")])
        return perl_lib

    def _configure(self):
        # QT packages may be found at: https://doc.qt.io/qt-5/qtmodules.html
        # note: do not need to explicitly skip any modules that did not have their source checked out
        modules_to_skip = [
            "qt3d", # Causes build errors on Linux.
            "qtactiveqt",
# Required:            "qtbase",
            "qtconnectivity",
# Required for qml:            "qtdeclarative",    # Required due to Qt v5.x build requirements.
            "qtdoc",
            "qtgamepad",
# Required for quick.2:            "qtgraphicaleffects",
# Required:            "qtlocation",
# Required:            "qtmultimedia",
            "qtpurchasing",
# Required:            "qtquickcontrols",
# Required:            "qtquickcontrols2",
            "qtremoteobjects",
# Required:            "qtscript",
            "qtscxml",
# Required:            "qtsensors",
            "qtserialbus", # Causes build errors on Linux.
            "qtserialport", # Causes build errors on Linux.
            "qtspeech",
# Required for macdeployqt, windeployqt tools.            "qttools",
            "qttranslations",
# Required:            "qtwebchannel", # https://github.com/qt/qtwebchannel
            "qtwebglplugin",
            "qtwebsockets",
# Required:            "qtxmlpatterns"
        ]
        dont_make=[
            "examples",
            "tests"
        ]
        options_to_say_no_to=[
            "cups",
            "eglfs",
            "harfbuzz",
            "iconv",
            "mtdev",
            "openvg",
            "pch",
            "sql-db2",
            "sql-ibase",
            "sql-mysql",
# TODO            "xrender",
        ]

        config_args=[]
        # avoiding very spammy warnings
        if self.settings.os == "Linux":
            config_args.append("QMAKE_CXXFLAGS='-w'")
        elif self.settings.os == "Macos":
            config_args.append("QMAKE_CXXFLAGS='-w'")

        # note GIF library source is found in the Qt source tree
        config_args.extend([
            "-silent",
            "-c++std", self._cxx_std,
            "-confirm-license",
            "-force-debug-info",  # Bundle any pdb files also for release builds.
            "-opengl", "desktop",
            "-opensource",
            "-prefix", self.package_folder,
            "-qt-pcre", # Needed for regular expressions in QString by the feature "regularexpression". This feature does not appear to be used at Foundry. To be reviewed.
            "-shared",
        ])

        def _add_library(lib_name, lib_option, extra_library_path_dependency=None, link_only_dependent_packages=None):
            library_search_paths = []
            library_search_paths.extend(self.deps_cpp_info[lib_name].lib_paths)
            if extra_library_path_dependency is not None:
                for extra in extra_library_path_dependency:
                    library_search_paths.extend(self.deps_cpp_info[extra].lib_paths)

            libraries = []
            libraries.extend(self.deps_cpp_info[lib_name].libs)
            if link_only_dependent_packages is not None:
                for dependent in link_only_dependent_packages:
                    libraries.extend(self.deps_cpp_info[dependent].libs)

            lprefix = "" if self.settings.os == "Windows" else "-l"
            libraries_to_link = " ".join(lprefix + lib for lib in libraries)

            library_option_cmd = f'{lib_option}="{libraries_to_link}"'
            include_search_path_cmd = f'-I"{self.deps_cpp_info[lib_name].include_paths[0]}"'
            library_search_path_cmd = " ".join(f'-L"{path}"' for path in library_search_paths)

            return [
                library_option_cmd,
                include_search_path_cmd,
                library_search_path_cmd,
            ]

        config_args.extend(["-openssl-linked"])
        config_args.extend(_add_library("OpenSSL", "OPENSSL_LIBS"))
        config_args.extend(["-system-libjpeg"])
        config_args.extend(_add_library("JPEG", "LIBJPEG_LIBS"))
        config_args.extend(["-system-zlib"]) # Required for PNG: otherwise any system zlib will be used, despite the transitive dependency PNG has on the artifactory-supplied zlib, which would have been ignored.
        config_args.extend(_add_library("zlib", "ZLIB_LIBS"))
        config_args.extend(["-system-tiff"])
        config_args.extend(_add_library("libtiff", "TIFF_LIBS", link_only_dependent_packages=["JPEG", "zlib"]))
        config_args.extend(["-system-libpng"])
        config_args.extend(["-system-sqlite"])
        if self.settings.os == "Linux":
            # use packaged ICU to control versions which differ across distros, also statically linked
            # this is for the QCollator backend mostly
            config_args.extend(["-icu"])
            config_args.extend(_add_library("icu", "ICU_LIBS"))
        else:
            options_to_say_no_to.append("icu")
            config_args.extend(_add_library("PNG", "LIBPNG_LIBS"))
            config_args.extend(_add_library("SQLite", "SQLITE_LIBS"))

        for module in modules_to_skip:
            config_args.append("-skip")
            config_args.append(module)
        for part in dont_make:
            config_args.append("-nomake")
            config_args.append(part)
        config_args.extend(["-no-{}".format(option) for option in options_to_say_no_to])

        src_dir = path.join(self.source_folder, self._source_subfolder)
        if self.settings.os == "Windows":
            config_args.extend([
                "-debug" if self.settings.build_type == "Debug" else "-release",
                "-mp",
                "-make-tool",
                path.join(self.deps_cpp_info["jom"].rootpath, self.deps_user_info["jom"].jom_exe),
            ])
            self.run(
                path.join(
                    src_dir,
                    "configure.bat {}".format(" ".join(config_args))
                ),
                run_environment=True
            )
        else:
            if self.settings.os == "Macos":
                # Cannot have pure debug frameworks, so build both.
                config_args.extend([
                    ("-debug-and-release" if self.settings.build_type == "Debug" else "-release"),
                    "-framework",
# TODO: is this needed?                "-platform", "macx-clang",
# TODO: is this needed?                "-sdk", "macosx10.15",
# TODO: is this needed?                "-libdir", os.path.join(installPrefix, "frameworks")
                ])
                if "arm" in self.settings.arch:
                    config_args.extend([
                        "-device-option",
                        "QMAKE_APPLE_DEVICE_ARCHS=arm64",
                        "-make", "tools", # Qt thinks it's cross-compiling and disables tools builds, so force re-enable them
                    ])
                if self._useFoundryGLBackend:
                  environ["FOUNDRYGL_FRAMEWORK_PATH"] = path.join( self.deps_cpp_info["foundrygl"].rootpath, "lib")
            else:
                config_args.append("-system-freetype")
                config_args.extend(_add_library("Freetype", "FREETYPE_LIBS"))
                config_args.extend(_add_library("Fontconfig", "FONTCONFIG_LIBS", extra_library_path_dependency=["Expat"]))
            with tools.environment_append({"PERLLIB": self._perl_lib}):
                self.run(
                    path.join(
                        src_dir,
                        "configure {}".format(" ".join(config_args))
                    ),
                    run_environment=True
                )

    @property
    def _jom_path(self):
        return path.join(self.deps_cpp_info["jom"].rootpath, self.deps_user_info["jom"].jom_exe)

    def build(self):
        self._ensure_pc_files()
        make_tool = self._jom_path if self.settings.os == "Windows" else "make"
        # point pkg-config at where the pkg_config generator wrote .pc files
        # this is needed for both qmake, and GN, as they both call pkg-config separately
        # note that this is prepending with our path
        with tools.environment_append({"PKG_CONFIG_PATH": [self.install_folder], "PERLLIB": self._perl_lib}):
            self._configure()
            self.run("{} -j{}".format(make_tool, tools.cpu_count()), run_environment=True)

    def package(self):
        make_tool = self._jom_path if self.settings.os == "Windows" else "make"
        with tools.environment_append({"PKG_CONFIG_PATH": [self.install_folder], "PERLLIB": self._perl_lib}):
            self._configure()
            self.run("{} -j{} install".format(make_tool, tools.cpu_count()), run_environment=True)

        # add qt.conf file to make the package relocatable
        bin_folder = path.join(self.package_folder, "bin")
        makedirs(bin_folder, exist_ok=True)
        with open(path.join(bin_folder, "qt.conf"), "wt") as conf_file:
            conf_file.writelines(["[Paths]\n", "Prefix = ..\n"])
