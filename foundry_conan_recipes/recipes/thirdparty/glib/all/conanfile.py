# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import shutil

from conans import ConanFile, Meson, tools
from jinja2 import Environment, FileSystemLoader


class GLibConan(ConanFile):
    name = "GLib"
    license = "LGPL-2.1-or-later"
    author = "Shawn Amundson, The GNOME Project"
    url = "https://gitlab.gnome.org/GNOME/glib"
    description = ("GLib is a general-purpose, portable utility library, which provides many "
                   "useful data types, macros, type conversions, string utilities, file utilities, "
                   "a mainloop abstraction, and so on.")

    settings = "os", "compiler", "build_type", "arch"

    options = {"shared": [True]}
    default_options = {"shared": True}

    exports_sources = "cmake/*"
    revision_mode = "scm"

    package_originator = "External"
    package_exportable = True

    build_requires = ('pcre2/10.42', )

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if self.settings.os == 'Macos':
            self.build_requires('pkgconfig/0.29.2@thirdparty/development')

    @property
    def _source_subfolder(self):
        return f"{self.name}_src"

    @property
    def _run_unit_tests(self):
        return "GLIB_RUN_UNITTESTS" in os.environ

    def _get_cygwin_bin_dir(self):
        return os.path.join(self.source_folder, 'cygwin64', 'bin').replace('\\', '/')

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        git = tools.Git(folder=self._source_subfolder)
        git.clone(version_data["git_url"])
        git.checkout(version_data["git_hash"], submodule='recursive')

        if self.settings.os == 'Windows':
            # Cygwin is required with at least the following packages:
            #    * pkg-config
            git = tools.Git(folder='cygwin-standalone')
            git.clone(
                'git@a_gitlab_url:libraries/conan/thirdparty/cygwin-standalone.git',
                branch='92e12f9e3e0e843cde573f45f813e17d9b4af96f',  # foundry/v3.4.5
                shallow=True)
            tools.untargz('cygwin-standalone/cygwin64.tgz')

            # Give pkg-config the standard name, or else Meson won't find it.
            os.rename(os.path.join(self._get_cygwin_bin_dir(), 'pkgconf.exe'),
                      os.path.join(self._get_cygwin_bin_dir(), 'pkg-config.exe'))

            # Cygwin's `link.exe` file conflicts with MSVC's linker; remove it.
            os.remove(os.path.join(self._get_cygwin_bin_dir(), 'link.exe'))

    def _patch_pc_files(self):
        # On Unix systems, pkg-config files are expected to use relative prefixes to the file
        # location (via the ${pcfiledir} variable). On Windows, however, pkg-config fails to resolve
        # the variable correctly; prefixes need to be patched on the fly.

        if self.settings.os != 'Windows':
            return

        for dep_name in self.deps_cpp_info.deps:
            root_path = self.deps_cpp_info[dep_name].rootpath
            pkgconfig_dir = os.path.join(root_path, 'lib', 'pkgconfig')
            for filename in os.listdir(pkgconfig_dir):
                if filename.endswith('.pc'):
                    src_pc_file = os.path.join(pkgconfig_dir, filename)
                    dst_pc_file = os.path.join(self.build_folder, filename)
                    shutil.copy2(src_pc_file, dst_pc_file)
                    tools.replace_prefix_in_pc_file(dst_pc_file, root_path)

    def _get_pc_directories(self):
        pc_file_directories = []
        if self.settings.os != 'Windows':
            for dep_name in self.deps_cpp_info.deps:
                pc_file_directories.append(
                    os.path.join(self.deps_cpp_info[dep_name].rootpath, 'lib', 'pkgconfig'))
        else:
            # Files patched on the fly are written to the build directory.
            pc_file_directories.append(self.build_folder)
        return pc_file_directories

    def _configure_meson(self):
        args = [
            '-Dwith_libintl=false',  # GPL
            '-Dbuild_gettextize=false',  # GPL: https://a_gitlab_url/libraries/conan/thirdparty/GNOME/GLib/-/blob/2.75.2/tools/glib-gettextize.in#L5
            '-Dbuild_submodules=false',
            '-Dlibmount=disabled',
            '-Dselinux=disabled',
            '-Dpkgconfig.relocatable=true',
        ]
        if not self._run_unit_tests:
            args.append('-Dtests=false')

        meson = Meson(self)
        meson.configure(args=args,
                        source_folder=self._source_subfolder,
                        pkg_config_paths=self._get_pc_directories())
        return meson

    def _build_environment(self):
        env = {}
        if self.settings.os == 'Windows':
            env['PATH'] = [self._get_cygwin_bin_dir()]
        elif self.settings.os == 'Macos':
            env['PATH'] = [self.deps_cpp_info["pkgconfig"].bin_paths[0]]
        # pkg-config is assumed installed on Linux machines.
        return env

    def build(self):
        self._patch_pc_files()

        with tools.environment_append(self._build_environment()):
            meson = self._configure_meson()
            meson.build()
            if self._run_unit_tests:
                meson.test()

    def package(self):
        with tools.environment_append(self._build_environment()):
            self._configure_meson().install()

        self._write_cmake_config_files()

        # PCRE2 is built statically into the shared library; the dependency is not needed in the
        # `.pc` file.
        tools.replace_in_file(os.path.join(self.package_folder, 'lib', 'pkgconfig', 'glib-2.0.pc'),
                              'Requires.private: libpcre2-8 >= 10.32', '')

    def _write_cmake_config_files(self):
        cmake_dst = os.path.join(self.package_folder, 'cmake')
        os.makedirs(cmake_dst, exist_ok=True)

        if self.settings.os == 'Windows':
            lib_dirname = 'bin'
            lib_prefix = ''
            lib_extension = '.dll'
        else:
            lib_dirname = 'lib'
            lib_prefix = 'lib'
            lib_extension = '.so' if self.settings.os == 'Linux' else '.dylib'

        data = {
            'lib_version': str(self.version),
            'lib_dirname': lib_dirname,
            'lib_filename': f'{lib_prefix}glib-2.0{lib_extension}',
        }

        if self.settings.os == 'Windows':
            data['win_lib_filename'] = 'glib-2.0.lib'

        file_loader = FileSystemLoader(os.path.join(self.source_folder, 'cmake'))
        env = Environment(loader=file_loader)

        cmakeconfig_template = env.get_template('GLibConfig.cmake.in')
        cmakeconfig_template.stream(data).dump(os.path.join(cmake_dst, 'GLibConfig.cmake'))

        cmakeconfigversion_template = env.get_template('GLibConfigVersion.cmake.in')
        cmakeconfigversion_template.stream(data).dump(
            os.path.join(cmake_dst, 'GLibConfigVersion.cmake'))
