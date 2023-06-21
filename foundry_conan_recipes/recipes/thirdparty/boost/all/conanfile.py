# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import glob
import os
from os import path
import stat
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration, ConanException
from conans.tools import os_info

import semver
from semver import SemVer


class BoostConan(ConanFile):
    name = "boost"
    license = "BSL-1.0"
    author = "The Boost community"
    url = "https://www.boost.org"
    description = "Boost provides free peer-reviewed portable C++ source libraries"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "python_version": [None, "2", "3", "3.9", "3.10"],
        "namespace": "ANY",
    }
    default_options = {"shared": False, "fPIC": True, "python_version": None, "namespace": None}
    no_copy_source = False # source is actually modified (adding dist/ folder)
    short_paths = True
    revision_mode = "scm"
    
    package_originator = "External"
    package_exportable = True

    @property
    def _checkout_folder(self):
        return "{}_src".format(self.name)

    @property
    def _run_unit_tests(self):
        return "BOOST_RUN_UNITTESTS" in os.environ

    @property
    def _toolsets(self):
        if os_info.is_windows:
            if self.settings.compiler == "Visual Studio":
                msvc_toolchains = {
                    "15": ("vc141", "msvc-14.1"),
                    "16": ("vc142", "msvc-14.2"),
                    "17": ("vc143", "msvc-14.3"),
                }
                return msvc_toolchains[str(self.settings.compiler.version)]
        elif os_info.is_macos:
            if self.settings.compiler == "apple-clang":
                return ("clang", "clang")
        else:
            assert os_info.is_linux
            if self.settings.compiler == "gcc":
                return ("gcc", "gcc")
        raise RuntimeError("Compiler {} is currently unsupported on {}".format(self.settings.compiler, os_info.os_version_name))

    @property
    def _disable_icu(self):
        return True # since icu has too varied support and versioning, particularly among Linux distributions

    def _get_shared_option(self, p):
        if p in self.options:
            return self.options[p].shared

        # If user does not provide options for dependencies, the default values
        # provided here will be used.
        # At the time of writing, these default values match the default values
        # of their respective recipes.
        default_shared_options = {'bzip2': False, 'zlib': False}
        return default_shared_options.get(p, False)

    def _is_private(self, p):
        return self.options.shared and not self._get_shared_option(p)


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os != "Windows":
            try:
                if not self.options.fPIC and self.options.shared:
                    raise ConanInvalidConfiguration(
                        "Don't know how to disable fPIC "
                        "for shared library builds")
            except ConanException as exception:
                self.output.warn("Ignoring: {}".format(exception))

    def _configure_b2_invocation(self):
        cflags = ""
        self._b2_arguments = [
            "toolset={}".format(self._b2_toolset)
        ]
        self._b2_test_arguments = []
        self._b2_test_arguments.append("--include-tests=system,chrono,regex")
        if self.options.python_version == "None":
            self._b2_arguments.append("--without-python")
        self._b2_arguments.append("variant={}".format("debug" if self.settings.build_type == "Debug" else "release"))
        self._b2_arguments.append("link={}".format("shared" if self.options.shared else "static"))
        if self.settings.os == "Macos" and "arm" in self.settings.arch:
            self._b2_arguments.append("address-model=64")
            self._b2_arguments.append("architecture=arm") # this is the CPU type
        else:
            self._b2_arguments.append("address-model={}".format('64' if self.settings.arch == 'x86_64' else '32'))
            self._b2_arguments.append("architecture=x86") # this is the CPU type
        self._b2_arguments.append("threading=multi")
        self._b2_arguments.append("runtime-link=shared")
        if self.options.python_version and self.settings.build_type == "Debug":
            self._b2_arguments.append("python-debugging=on")
        if semver.gt(self.version, "1.66.0", False):
            self._b2_arguments.append("visibility=hidden")
        elif self.settings.os != "Windows":
            cflags += " -fvisibility=hidden -fvisibility-inlines-hidden"

        if not os_info.is_windows:
            # -fPIC is assumed for shared, but needs to be added for static libraries
            if self.options.fPIC and not self.options.shared:
                cflags += " -fPIC"
        if not os_info.is_windows:
            self._b2_arguments.append("--layout=system") # CMake is picky about the file name layouts
        # https://www.boost.org/build/doc/html/bbv2/overview/invocation.html#bbv2.overview.invocation.options
        #self._b2_arguments.append("-d+2") # Show "quiet" actions and display all action text, as they are executed. (debug level 2)
        self._b2_arguments.append("-q") # Stop at the first error, as opposed to continuing to build targets that don't depend on the failed ones.
        self._b2_arguments.append("-j{}".format(tools.cpu_count())) # Run up to N commands in parallel.
        if os_info.is_windows:
            self._b2_arguments.append("--hash") # for guaranteed length paths, but not human readable

        if cflags != "":
            self._b2_arguments.append(f"cflags='{cflags}'")

        if self._disable_icu:
            self._b2_arguments.extend([
                "--disable-icu",        # disables looking for libicu
                "boost.locale.icu=off", # disables icu as a backend to locale
            ])


    def requirements(self):
        self.requires("bzip2/1.0.6@thirdparty/development", private=self._is_private("bzip2"))
        self.requires("zlib/1.2.11@thirdparty/development", private=self._is_private("zlib"))
        if self.options.python_version:
            if self.options.python_version == "2":
                self.requires("Python/2.7.18@thirdparty/development")
            elif self.options.python_version == "3":
                self.requires("Python/3.7.7@thirdparty/development")
            elif self.options.python_version == "3.9":
                self.requires("Python/3.9.10")
            elif self.options.python_version == "3.10":
                self.requires("Python/3.10.10")

    def build_requirements(self):
        if self.settings.os == "Linux" and self.options.shared:
            self.build_requires("patchelf/0.11@thirdparty/development")


    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")


    def _basic_lib_info(self, dep):
        return (
            self.deps_cpp_info[dep].version,
            self.deps_cpp_info[dep].include_paths[0].replace('\\', '/'),
            self.deps_cpp_info[dep].lib_paths[0].replace('\\', '/')
        )


    @property
    def _python_executable(self):
        return path.join(
            path.normpath(self.deps_cpp_info['Python'].rootpath),
            path.normpath(self.deps_user_info['Python'].interpreter)
        )


    def _create_user_config_jam(self, folder):
        """To help locating the third party deps"""
        self.output.info("Generate user-config.jam in '{}'".format(folder))

        contents = ""
        contents += "import option ;"
        contents += "\nusing zlib : {} : <include>{} <search>{} ;".format(*self._basic_lib_info("zlib"))
        if self.settings.os in ("Linux", "Macos"):
            contents += "\nusing bzip2 : {} : <include>{} <search>{} ;".format(*self._basic_lib_info("bzip2"))

        if self.options.python_version:
            python_version = SemVer(self.deps_cpp_info['Python'].version, False)
            python_include = self.deps_cpp_info['Python'].include_paths[0].replace('\\', '/')
            python_lib = self.deps_cpp_info['Python'].lib_paths[0].replace('\\', '/')
            python_executable = self._python_executable.replace('\\', '/')
            is_debug = self.settings.build_type == "Debug"
            python_conditions = '<python-debugging>on' if is_debug else ''

            contents += '\nusing python : %s : "%s" : "%s" : "%s" : %s ;' % (
                f"{python_version.major}.{python_version.minor}",
                python_executable,
                python_include,
                python_lib,
                python_conditions
            )

        contents += "\noption.set keep-going : false ;"
        filename = path.join(folder, "user-config.jam")
        tools.save(filename,  contents)


    def _build_b2(self, src_dir):
        self._bootstrap_toolset, self._b2_toolset = self._toolsets
        self._configure_b2_invocation()

        if self.version >= "1.80.0" and os_info.is_windows:
            self._b2 = os.path.join(self.build_folder, "b2")
        else:
            self._b2 = os.path.join(self.build_folder, "bin", "b2")
        if os_info.is_windows:
            self._b2 += ".exe"
        if os.path.isfile(self._b2):
            # already built on a previous run
            return

        build_dir = os.path.join(src_dir, "tools", "build")
        bootstrapper = os.path.join(build_dir, "bootstrap")
        localb2 = os.path.join(build_dir, "b2")
        if os_info.is_windows:
            bootstrapper += ".bat"
            localb2 += ".exe"
        else:
            bootstrapper += ".sh"

        with tools.chdir(build_dir):
            bootstrapper_args = {
                "bootstrapper": bootstrapper,
                "toolset": self._bootstrap_toolset
            }
            self.run("{bootstrapper} {toolset}".format(**bootstrapper_args))
            b2_args = {
                "b2": localb2,
                "userconfig": path.join(self.build_folder, "user-config.jam"),
                "toolset": self._b2_toolset,
                "prefix": self.build_folder
            }

            self.run("{b2} --user-config={userconfig} toolset={toolset} --prefix={prefix} install".format(**b2_args))


    def _build_bcp(self, src_dir):
        self._bcp = os.path.join(src_dir, "dist", "bin", "bcp")
        if os_info.is_windows:
            self._bcp += ".exe"
        if os.path.isfile(self._bcp):
            # already built on a previous run
            return

        bcp_dir = os.path.join(src_dir, "tools", "bcp")

        # this dirties the source tree, with the following folders
        # /boost - containing hard links to the headers
        # dist/bin/bcp - the built executable
        with tools.chdir(bcp_dir):
            args = {
                "b2": self._b2,
                "builddir": os.path.join(self.build_folder, "bcp"),
                "toolset": self._b2_toolset,
            }
            self.run("{b2} --build-dir={builddir} --toolset={toolset}".format(**args))


    def _get_library_list(self, src_dir):
        # as much as I'd like to use "b2 --show-libraries" it returns an incomplete number of libs for use with bcp, and also missing
        # dependencies for source-based libraries
        # https://stackoverflow.com/questions/13604090/which-boost-libraries-are-header-only
        # https://stackoverflow.com/questions/52899638/how-do-i-build-boost-log-exported-with-bcp
        # Python 3.5+ simplification: library_names = [f.name for f in os.scandir(os.path.join(src_dir, "libs")) if f.is_dir()]
        library_names = [lib for lib in os.listdir(os.path.join(src_dir, "libs")) if os.path.isdir(os.path.join(src_dir, "libs", lib))]
        return library_names


    def _namespace_boost(self, src_dir):
        libraries = self._get_library_list(src_dir)
        namespace = str(self.options.namespace)
        self.output.info("Modifying Boost to use the namespace: '{}'".format(namespace))
        args = {
            "bcp": self._bcp,
            "namespace": namespace,
            "srcdir": src_dir,
            "dstdir": os.path.join(self.build_folder, namespace),
            "libraries": " ".join(libraries), # bcp ALL libraries, regardless of options in this recipe, so that --without-X flags to b2 still apply
        }
        os.makedirs(args["dstdir"], exist_ok=True)
        self.run("{bcp} --namespace={namespace} --namespace-alias --boost={srcdir} headers boost_install build boost {libraries} {dstdir}".format(**args))
        return args["dstdir"]

    def _add_runpaths_to_libs(self):
        """
        For GCC builds using new dtags (RUNPATHS), each shared library is responsible for finding
        its dependents, so must have their own RUNPATHs.
        For older builds, an RPATH from the calling executable takes precedence over RUNPATH.
        """
        if self.settings.os == "Linux" and self.options.shared:
            patchelf_path = os.path.join(self.deps_cpp_info["patchelf"].bin_paths[0], "patchelf")
            for symlink in glob.glob(os.path.join(self.package_folder, "lib", "*.so")):
                self.run(f'"{patchelf_path}" --set-rpath \$ORIGIN "{symlink}"')

    def _build_libs(self, src_dir):
        build_dir = os.path.join(self.build_folder, "libs")
        build_log = os.path.join(self.build_folder, "buildlog.txt")
        with tools.chdir(src_dir):
            build_args = {
                "b2": self._b2,
                "userconfig": path.join(self.build_folder, "user-config.jam"),
                "args": ' '.join(self._b2_arguments),
                "prefix": self.package_folder,
                "builddir": build_dir,
                "log": build_log
            }
            self.run("{b2} {args} --user-config={userconfig} --prefix={prefix} --build-dir={builddir} headers install -o{log}".format(**build_args))
            # Due to a bug in 1.66.0 the install step needs to be repeated to get the include files installed
            if self.version == "1.66.0":
               self.run("{b2} {args} --user-config={userconfig} --prefix={prefix} --build-dir={builddir} headers install -o{log}".format(**build_args))

            self._add_runpaths_to_libs()


    def _test_libs(self, src_dir):
        test_dir = os.path.join(src_dir, "status")
        # boost_check_library.py is not executable, but needs to be
        st = os.stat(os.path.join(test_dir, "boost_check_library.py"))
        os.chmod(os.path.join(test_dir, "boost_check_library.py"), st.st_mode | stat.S_IEXEC)
        test_build_dir = os.path.join(self.build_folder, "tests")
        test_build_log = os.path.join(self.build_folder, "testlog.txt")
        with tools.chdir(test_dir):
            test_args = {
                "b2": self._b2,
                "testargs": ' '.join(self._b2_test_arguments),
                "buildargs": ' '.join(self._b2_arguments),
                "builddir": test_build_dir,
                "log": test_build_log
            }
            self.run("{b2} {testargs} {buildargs} --build-dir={builddir} -o{log}".format(**test_args))


    def build(self):
        src_dir = os.path.join(self.source_folder, self._checkout_folder)
        self._create_user_config_jam(self.build_folder)
        self._build_b2(src_dir)
        if self.options.namespace:
            self._build_bcp(src_dir)
            src_dir = self._namespace_boost(src_dir)
        self._build_libs(src_dir)
        if self._run_unit_tests:
            self._test_libs(src_dir)

    def package_info(self):
        compile_definitions = [
            "BOOST_ALL_NO_LIB", # disable auto-linking
        ]
        self.user_info.Boost_USE_STATIC_LIBS = "OFF" if self.options.shared else "ON"
        if self.options.shared:
            compile_definitions.append("BOOST_ALL_DYN_LINK")

        if self.options.namespace:
            self.user_info.Boost_NAMESPACE = self.options.namespace
            self.user_info.Boost_NO_BOOST_CMAKE = "ON" # no support for custom namespaces in the generated CMake config files
        if self.options.python_version:
            python_version = SemVer(self.deps_cpp_info["Python"].version, False)
            if not self.options.shared:
                compile_definitions.append("BOOST_PYTHON_STATIC_LIB")
            if self.settings.build_type == "Debug":
                self.user_info.Boost_USE_DEBUG_PYTHON = "ON"
                compile_definitions.append("BOOST_DEBUG_PYTHON") # see https://www.boost.org/doc/libs/1_70_0/libs/python/doc/html/building/python_debugging_builds.html, needed on Windows for clean program shutdown
            else:
                self.user_info.Boost_USE_DEBUG_PYTHON = "OFF"
            if semver.gt(self.version, "1.66.0", False):
                if self.options.namespace:
                    # uses FindBoost.cmake, and note the change in Boost 1.67+ in https://cmake.org/cmake/help/v3.19/module/FindBoost.html
                    self.user_info.Boost_PYTHON_COMPONENT = "python{}{}".format(str(python_version.major), str(python_version.minor))
                else:
                    # this only works with the generated CMake config file
                    self.user_info.Boost_PYTHON_COMPONENT = "python"
            else:
                self.user_info.Boost_PYTHON_COMPONENT = "python{}".format("" if python_version.major == 2 else str(python_version.major))
        self.user_info.Boost_COMPILE_DEFINITIONS = ";".join(compile_definitions)

    def package_id(self):
        if self.options.python_version is None:
            for pyver in ("2", "3", "3.9", "3.10"):
                compatible_package = self.info.clone()
                compatible_package.options.python_version = pyver
                self.compatible_packages.append(compatible_package)
