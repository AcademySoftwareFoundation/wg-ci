# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil
import stat
import xml.etree.cElementTree as ET
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanException
from contextlib import contextmanager

from jinja2 import Environment, FileSystemLoader

from semver import SemVer
from os import path


@contextmanager
def _patch_env_vars(env_var_dict, env_var_to_remove):
    original = dict(os.environ)
    os.environ.update(env_var_dict)
    for env_var in env_var_to_remove:
        if env_var in os.environ:
            del os.environ[env_var]
    yield
    os.environ.clear()
    os.environ.update(original)

class PythonConan(ConanFile):
    name = "Python"
    license = "PSF-2.0"
    author = "Guido van Rossum"
    url = "https://www.python.org/"
    description = "Python is an interpreted, object-oriented, high-level programming language with dynamic semantics."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True]}
    default_options = {"shared": True}
    no_copy_source = False  # Windows builds in-source
    revision_mode = "scm"
    exports_sources = "*.cmake"

    build_requires = (
        "bzip2/1.0.6@thirdparty/development",  # used by bz2 extension module
        "SQLite/3.32.3@thirdparty/development",  # used by _sqlite3 extension module
        "zlib/1.2.11@thirdparty/development",  # used by zlib extension module
    )

    package_originator = "External"
    package_exportable = True

    @property
    def _checkout_folder(self):
        return f"{self.name}_src"

    @property
    def _run_unit_tests(self):
        return "PYTHON_RUN_UNITTESTS" in os.environ

    @property
    def _base_version(self):
        v = SemVer(self.version, False)
        format_str = "{}{}" if self.settings.os == "Windows" else "{}.{}"
        return format_str.format(v.major, v.minor)

    @property
    def _is_python3(self):
        return SemVer(self.version, False).major >= 3

    @property
    def _with_conanified_ffi(self):
        if self.settings.os == "Macos":
            return False
        return tools.Version(self.version) >= "3.9.10"

    @property
    def _exe_suffix(self):
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            return "_d"
        return ""

    @property
    def _python_base_name(self):
        return f"python{self._base_version}{self._exe_suffix}"

    @property
    def _pythonw_base_name(self):
        return f"pythonw{self._base_version}{self._exe_suffix}"

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("patchelf/0.11@thirdparty/development")
        if self._with_conanified_ffi:
            # used by _ctypes extension module, no longer built as part of Python
            self.build_requires("libffi/3.4.2")

        # OpenSSL used by _ssl and _hashlib extension modules
        if self.settings.os == "Macos" and "arm" in self.settings.arch:
            self.build_requires("OpenSSL/[~1.1.1m]")
        else:
            self.build_requires("OpenSSL/1.1.1g@thirdparty/development")

    def configure(self):
        self.options["OpenSSL"].shared = False
        self.options["bzip2"].shared = False
        self.options["SQLite"].shared = False
        self.options["zlib"].shared = False
        if self._with_conanified_ffi:
            self.options["libffi"].shared = False

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._checkout_folder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule="recursive")

    def _make_msbuild_overrides_file(self):
        root = ET.Element("Project")
        doc = ET.SubElement(root, "PropertyGroup")

        ET.SubElement(doc, "opensslDir").text = self.deps_cpp_info["OpenSSL"].rootpath
        ET.SubElement(doc, "opensslIncludeDir").text = self.deps_cpp_info["OpenSSL"].include_paths[0]
        ET.SubElement(doc, "bz2Dir").text = self.deps_cpp_info["bzip2"].rootpath
        ET.SubElement(doc, "sqlite3Dir").text = self.deps_cpp_info["SQLite"].rootpath
        ET.SubElement(doc, "zlibDir").text = self.deps_cpp_info["zlib"].rootpath
        if self._with_conanified_ffi:
            ET.SubElement(doc, "libffiDir").text = self.deps_cpp_info["libffi"].rootpath
            ET.SubElement(doc, "libffiOutDir").text = self.deps_cpp_info["libffi"].lib_paths[0]
            ET.SubElement(doc, "libffiIncludeDir").text = self.deps_cpp_info["libffi"].include_paths[0]

        tree = ET.ElementTree(root)
        tree.write(
            path.join(self.build_folder, "external_overrides.props"),
            xml_declaration=True,
            encoding="utf-8",
        )

    @property
    def _abi_suffix(self):
        v = SemVer(self.version, False)
        if self.settings.os == "Windows":
            return f"{v.major}{v.minor}{self._exe_suffix}"
        else:
            return "{}.{}{}{}".format(
                v.major,
                v.minor,
                "d" if self.settings.build_type == "Debug" and v.major >= 3 else "",
                "m" if (v.major >= 3 and v.minor < 8) or v.major > 3 else ""
            )

    _autotools = None

    def _config_args(self):
        config_args = ["--prefix={}".format(self.package_folder)]

        if self._is_python3:
            # Python3 has mysteriously support for these two only :o
            config_args.append("--with-openssl={}".format(self.deps_cpp_info["OpenSSL"].rootpath))
            if tools.Version(self.version) >= "3.9.10":
                # This no longer exists in Python 3.9.10 configure args.
                config_args.append("--with-bz2={}".format(self.deps_cpp_info["bzip2"].rootpath))
        else:
            config_args.append("--enable-unicode=ucs4")
            config_args.append("--with-ensurepip")
            self._autotools.include_paths.extend([
                self.deps_cpp_info["OpenSSL"].include_paths[0],
                self.deps_cpp_info["bzip2"].include_paths[0],
            ])
            self._autotools.library_paths.extend([
                self.deps_cpp_info["OpenSSL"].lib_paths[0],
                self.deps_cpp_info["bzip2"].lib_paths[0],
            ])

        if self.settings.build_type == "Debug":
            config_args.append("--with-pydebug")
        # else:
        #     config_args.append("--enable-optimizations")

        if self.options.shared:
            if self.settings.os == "Macos":
                config_args.append(f"--enable-framework={self.package_folder}")
            else:
                config_args.append("--enable-shared")
        else:
            raise ConanException("static library building is unsupported")
        return config_args

    def _get_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.include_paths = [
            self.deps_cpp_info["SQLite"].include_paths[0],
            self.deps_cpp_info["zlib"].include_paths[0],
            self.deps_cpp_info["bzip2"].include_paths[0],
        ]
        self._autotools.library_paths = [
            self.deps_cpp_info["OpenSSL"].lib_paths[0],
            self.deps_cpp_info["bzip2"].lib_paths[0],
            self.deps_cpp_info["SQLite"].lib_paths[0],
            self.deps_cpp_info["zlib"].lib_paths[0],
        ]
        if self._with_conanified_ffi:
            self._autotools.include_paths.append(self.deps_cpp_info["libffi"].include_paths[0])
            self._autotools.library_paths.append(self.deps_cpp_info["libffi"].lib_paths[0])
        self._autotools.fpic = True

        return self._autotools

    @property
    def _msvc_toolchain(self):
        msvc_toolchains = {
            "15": "v141",
            "16": "v142",
            "17": "v143",
        }
        return msvc_toolchains[str(self.settings.compiler.version)]

    def build(self):
        src_dir = path.join(self.source_folder, self._checkout_folder)
        if self.settings.os == "Windows":

            self._make_msbuild_overrides_file()

            pcbuild_dir = path.join(src_dir, "PCbuild")
            args = [
                "-v",
                "{}".format("-d" if self.settings.build_type == "Debug" else ""), # build in debug mode (Py_DEBUG, enable assertions, etc)
                "-p x64",
                "-c {}".format(self.settings.build_type),
                "--no-tkinter",
                "{}".format("--no-bsddb" if not self._is_python3 else ""),
                '"/p:PlatformToolset={}"'.format( self._msvc_toolchain ),
                '"/p:ForceImportBeforeCppTargets={}"'.format(
                    path.join(self.build_folder, "external_overrides.props")
                ),  # override MSBUILD properties in existing Python build scripts with our own
            ]
            self.run("{}/build.bat {}".format(pcbuild_dir, " ".join(args)))
        else:
            # remove __PYVENV_LAUNCHER__ from the environment, since on macOSX, running the build Python
            # interpreter will think it is being run using the virtual environment interpreter
            # see config_init_program_name in Modules/main.c in 3.7.x
            autotools = self._get_autotools()
            with _patch_env_vars({"PYTHONUSERBASE": '--', "PYTHONNOUSERSITE": "1"}, ["__PYVENV_LAUNCHER__"]):
                self._autotools.configure(
                    configure_dir=src_dir,
                    args = self._config_args(),
                )
                make_args = [f"-j{tools.cpu_count()}"]
                autotools.make(args=make_args)
                if self._run_unit_tests:
                    # this takes a long time
                    test_args = ["test", "-j1"]
                    autotools.make(test_args)

    def _produce_config_files(self):
        p = path.join(self.package_folder, "cmake")
        if not path.exists(p):
            os.mkdir(p)

        pyver = SemVer(self.version, False)
        file_loader = FileSystemLoader(self.source_folder)
        env = Environment(loader=file_loader)

        def _configure(file_name):
            data = {
                "version_major": str(pyver.major),
                "version_minor": str(pyver.minor),
                "version_patch": str(pyver.patch),
                "os": self.settings.os,
                "bt": self.settings.build_type,
                "abi_suffix": self._abi_suffix,
            }

            interpreter_template = env.get_template(file_name)
            interpreter_template.stream(data).dump(path.join(self.package_folder, "cmake", file_name))

        _configure("Python_InterpreterTargets.cmake")
        _configure("Python_DevelopmentTargets.cmake")
        _configure("Python_Macros.cmake")
        _configure("PythonConfig.cmake")
        _configure("PythonConfigVersion.cmake")

    def package(self):
        self._produce_config_files()

        src_dir = path.join(self.source_folder, self._checkout_folder)
        if self.settings.os == "Windows":
            # no install command on Windows, so make it here
            pc_dir = path.join(src_dir, "PC")
            include_dir = path.join(src_dir, "include")
            lib_dir = path.join(src_dir, "lib")
            binary_dir = path.join(src_dir, "PCbuild", "amd64")

            # Library
            python_lib_filename = self._python_base_name + ".dll"
            python_lib_pdb_filename = self._python_base_name + ".pdb"

            # Command
            python_shell_pdb_filename = "python_d.pdb" if self.settings.build_type == "Debug" else "python.pdb"
            pythonw_shell_pdb_filename = "pythonw_d.pdb" if self.settings.build_type == "Debug" else "pythonw.pdb"
            w9xpopen_pdb_filename = "w9xpopen_d.pdb" if self.settings.build_type == "Debug" else "w9xpopen.pdb"

            self.copy(pattern="*.pyd", src=binary_dir, dst="DLLs")
            self.copy(
                pattern="*.dll",
                src=binary_dir,
                dst="DLLs",
                excludes=[python_lib_filename],
            )
            self.copy(pattern=python_lib_filename, src=binary_dir, dst="")
            self.copy(pattern="*", src=include_dir, dst="include")
            self.copy(pattern="pyconfig.h", src=pc_dir, dst="include")
            self.copy(pattern="*.lib", src=binary_dir, dst="libs")
            self.copy(pattern="*.exe", src=binary_dir, dst="")
            self.copy(pattern="*", src=lib_dir, dst="Lib")
            self.copy(pattern=python_shell_pdb_filename, src=binary_dir, dst="")
            self.copy(pattern=pythonw_shell_pdb_filename, src=binary_dir, dst="")
            self.copy(pattern=python_lib_pdb_filename, src=binary_dir, dst="")
            self.copy(pattern=w9xpopen_pdb_filename, src=binary_dir, dst="")
            self.copy(
                pattern="*.pdb",
                src=binary_dir,
                dst="DLLs",
                excludes=[
                    python_shell_pdb_filename,
                    pythonw_shell_pdb_filename,
                    python_lib_pdb_filename,
                    w9xpopen_pdb_filename,
                ],
            )

            # Ensure that python.exe exists next to python_d.exe on Debug builds, so it can be found
            # by e.g. Qt Debug builds which need python.exe as their build_requirement
            if self.settings.build_type == "Debug":
                shutil.copy2( f"{self.package_folder}/python_d.exe", f"{self.package_folder}/python.exe" )

            python_zip = self._python_base_name
            # Ensure that pip works correcly on various Windows locales, see:
            # https://stackoverflow.com/questions/35176270/python-2-7-lookuperror-unknown-encoding-cp65001
            with tools.environment_append({ "PYTHONIOENCODING": "UTF8",\
                                            "PYTHONHOME": self.package_folder }):
                # ignore user site packages, so that pip is not found in some machine configurations
                extra_args = ['-I' if self._is_python3 else '-s']
                self.run(f'{self.package_folder}/python{self._exe_suffix}.exe {" ".join(extra_args)} -m ensurepip')
        else:
            autotools = self._get_autotools()
            install_args = ["-j1"]
            if self.settings.os == "Macos":
                # there are additional Makefiles on macos that do not get configured
                install_args.append(f"PYTHONAPPSDIR={self.package_folder}")
            with _patch_env_vars({ "PYTHONUSERBASE": '--', "PYTHONNOUSERSITE": "1"}, ["__PYVENV_LAUNCHER__"]):
                autotools.install(args=install_args if install_args else None)

            # intentionally excluded extension
            v = SemVer(self.version, False)
            python_zip = f"python{v.major}{v.minor}"

            def _remove_broken_easy_install_symlink(path):
                # MacOS has a broken easy_install symlink, with 3.9.10 and 3.10.10.
                # TP-503353 logged to investigate further if this causes an issue.
                if self.settings.os != "Macos" or self.version < "3.9":
                    return False
                if not os.path.exists(path) and os.path.islink(path) and "easy_install" in path:
                    self.output.warn("'{}' does not exist, or points to a file which does not"
                                     " exist. Symlink will be removed.".format(path))
                    os.remove(path)
                    return True
                return False

            def _make_path_writeable(path):
                mode = os.stat(path).st_mode
                mode = mode | stat.S_IWRITE
                os.chmod(path, mode)

            def _make_directory_writeable(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for dir_path in [os.path.join(root, d) for d in dirs]:
                        if _remove_broken_easy_install_symlink(dir_path):
                            continue
                        _make_path_writeable(dir_path)
                    for file_path in [os.path.join(root, f) for f in files]:
                        if _remove_broken_easy_install_symlink(file_path):
                            continue
                        _make_path_writeable(file_path)

            # Python's Makefile sets built binaries with 555 permissions (not user writeable)
            _make_directory_writeable(self.package_folder)

        # make the PythonXY.zip of the standard library
        shutil.make_archive(
            path.join(self.package_folder, python_zip),
            "zip",
            path.join(src_dir, "Lib"),
        )

        if self.settings.os == "Macos":
            v = SemVer(self.version, False)
            python_framework_version_subdir = path.join(
                "Python.framework", "Versions", f"{v.major}.{v.minor}",
            )
            python_dylib = path.join(
                self.package_folder, python_framework_version_subdir, "Python",
            )
            python_install_name = path.join(
                "@rpath", python_framework_version_subdir, "Python"
            )
            self.run(
                "install_name_tool -id {} {}".format(python_install_name, python_dylib)
            )

            def _change_python_install_name(binary_path, rpath):
                self.run(f"install_name_tool -change {python_dylib} {python_install_name} {binary_path}")
                try:
                    self.run(f"install_name_tool -add_rpath {rpath} {binary_path}")
                except ConanException:
                    self.output.warn(f"RPATH {rpath} already exists for {binary_path}")

            pycommand = path.join(
                self.package_folder,
                python_framework_version_subdir,
                "bin",
                self._python_base_name,
            )

            if not self._is_python3:
                _change_python_install_name(pycommand, path.join("@executable_path", "..", "..", "..", ".."))

            _change_python_install_name(pycommand, path.join("@executable_path", "..", "..", "..", ".."))

            mac_app = path.join(
                self.package_folder,
                python_framework_version_subdir,
                "Resources",
                "Python.app",
                "Contents",
                "MacOS",
                "Python",
            )

            # AppBundle/Contents/Frameworks
            _change_python_install_name(mac_app, path.join("@executable_path", "..", "..", "..", "..", "..", "..", ".."))
            # AppBundle/Contents/MacOS for libraries located next to the host application
            _change_python_install_name(mac_app, path.join("@executable_path", "..", "..", "..", "..", "..", "..", "..", "..", "Macos"))

            # ensure that the bin folder symbolic links are relative to the framework, rather than absolute to build machine paths
            def _make_relative_symbolic_link(link_path):
                target = os.readlink(link_path)
                relative_path = os.path.relpath(target, os.path.dirname(link_path))
                os.unlink(link_path)
                os.symlink(relative_path, link_path)

            for root, _, files in os.walk(path.join(self.package_folder, "bin")):
                for file in files:
                    full_filepath = os.path.join(root, file)
                    if not os.path.islink(full_filepath):
                        continue
                    _make_relative_symbolic_link(full_filepath)

        elif self.settings.os == "Linux":
            patchelf_path = path.join(
                self.deps_cpp_info["patchelf"].bin_paths[0], "patchelf"
            )
            self.run(
                r"{} --force-rpath --set-rpath \$ORIGIN/../lib:\$ORIGIN {}".format(
                    patchelf_path, path.join(self.package_folder, "bin", "python3" if self._is_python3 else "python")
                )
            )

    def package_info(self):
        pyver = SemVer(self.version, False)
        self.cpp_info.name = "Python"

        if self.settings.os == "Windows":
            self.cpp_info.bindirs = [""]  # On windows, the bindir == rootpath
            self.cpp_info.includedirs = ["include"]
            self.cpp_info.libs = [f"python{self._abi_suffix}.lib"]
            self.cpp_info.libdirs = ["libs"]
        elif self.settings.os == "Linux":
            self.cpp_info.bindirs = ["bin"]
            self.cpp_info.includedirs = [f"include/python{self._abi_suffix}"]
            self.cpp_info.libs = [f"libpython{self._abi_suffix}.so"]
            self.cpp_info.libdirs = ["lib"]
        elif self.settings.os == "Macos":
            internal_root = path.join("Python.framework", "Versions", f"{pyver.major}.{pyver.minor}")
            self.cpp_info.bindirs = [path.join(internal_root, "bin")]
            self.cpp_info.includedirs = [path.join(internal_root, "Headers")]
            self.cpp_info.libs = ["Python"] # In case someone needs it...
            self.cpp_info.libdirs = [path.join(internal_root)]
            self.cpp_info.frameworks = ["Python.framework"]

        interpreter_dir = "{}/".format(self.cpp_info.bindirs[0]) if self.cpp_info.bindirs[0] != "" else ""
        self.user_info.interpreter = "{}python{}{}{}".format(
            interpreter_dir,
            "_d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else "",
            f"{pyver.major}.{pyver.minor}" if self.settings.os != "Windows" else "",
            ".exe" if self.settings.os == "Windows" else ""
        )

        self.user_info.pyhome = "Python.framework/Versions/Current" if self.settings.os == "Macos" else ""
